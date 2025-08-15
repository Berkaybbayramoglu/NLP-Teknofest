# src/agentkit/kpi/evaluator.py
import io, json, time, pathlib, contextlib
from typing import Any, Dict, List, Tuple, Optional
import numpy as np
import pandas as pd
from sentence_transformers import SentenceTransformer, util

class KPIEvaluator:
    def __init__(self, agent_executor, emb_model_name: str = "trmteb/turkish-embedding-model", similarity_threshold: float = 0.65):
        self.agent = agent_executor
        self.emb = SentenceTransformer(emb_model_name)
        self.th = similarity_threshold

    @staticmethod
    def _extract_json_objects(text: str) -> List[dict]:
        objs, stack, start = [], 0, None
        for i, ch in enumerate(text):
            if ch == "{":
                if stack == 0: start = i
                stack += 1
            elif ch == "}":
                if stack > 0:
                    stack -= 1
                    if stack == 0 and start is not None:
                        block = text[start:i+1]
                        try: objs.append(json.loads(block))
                        except Exception: pass
                        start = None
        return objs

    @staticmethod
    def _to_text(x: Any) -> str:
        if x is None: return ""
        if isinstance(x, (dict, list)):
            try: return json.dumps(x, ensure_ascii=False)
            except Exception: return str(x)
        return str(x)

    @staticmethod
    def _norm(name: Optional[str]) -> str:
        return (name or "").strip().lower()

    @staticmethod
    def _sequential_tool_match(agent_tools: List[str], expected_tools: List[str]) -> Tuple[int, int, bool]:
        total, i, correct = len(agent_tools), 0, 0
        for at in agent_tools:
            if i < len(expected_tools) and KPIEvaluator._norm(at) == KPIEvaluator._norm(expected_tools[i]):
                correct += 1
                i += 1
        return correct, total, (correct == total == len(expected_tools))

    @staticmethod
    def _pairwise_finals(gold_finals: List[dict], pred_finals: List[dict]) -> List[Tuple[str, str]]:
        pairs, n = [], min(len(gold_finals), len(pred_finals))
        for i in range(n):
            g = gold_finals[i].get("action_input")
            p = pred_finals[i].get("action_input")
            pairs.append((KPIEvaluator._to_text(g), KPIEvaluator._to_text(p)))
        return pairs

    def _cosine(self, a: str, b: str) -> float:
        ea = self.emb.encode(a or "", convert_to_tensor=True, normalize_embeddings=True)
        eb = self.emb.encode(b or "", convert_to_tensor=True, normalize_embeddings=True)
        return float(util.cos_sim(ea, eb).item())

    @staticmethod
    def _load_gold_from_scenario(scn: Dict) -> Tuple[List[str], List[dict]]:
        gold_tools, gold_finals = [], []
        for step in scn.get("conversations", []):
            if step.get("role") != "assistant": continue
            objs = KPIEvaluator._extract_json_objects(step.get("content", ""))
            for obj in objs:
                action = obj.get("action")
                if KPIEvaluator._norm(action) == "final answer":
                    gold_finals.append(obj)
                elif action:
                    gold_tools.append(action)
        return gold_tools, gold_finals

    @staticmethod
    def _load_scenarios(path: str) -> List[Dict[str, Any]]:
        raw = pathlib.Path(path).read_bytes()
        data = json.loads(raw.decode("utf-8-sig", errors="replace"))
        return data if isinstance(data, list) else [data]

    def evaluate(self, scn: Dict, verbose: bool = False) -> Dict[str, Any]:
        scn_id = scn.get("id") or scn.get("name") or "SCENARIO"
        conversations = scn.get("conversations", [])
        critical = scn.get("critical_steps", []) or []
        gold_tools, gold_finals = self._load_gold_from_scenario(scn)
        expected_tools = critical if critical else gold_tools

        latencies, stdout_chunks = [], []
        first = True
        for step in conversations:
            if step.get("role") != "user": continue
            user_msg = step.get("content", "")
            t0 = time.time()
            buf = io.StringIO()
            try:
                with contextlib.redirect_stdout(buf):
                    if first:
                        resp = self.agent.invoke({"input": user_msg, "chat_history": []})
                        first = False
                    else:
                        resp = self.agent.invoke({"input": user_msg})
            except Exception:
                pass
            t1 = time.time()
            latencies.append(max(0.001, t1 - t0))
            stdout_chunks.append(buf.getvalue())

        combined = "\n".join(stdout_chunks)
        objs = self._extract_json_objects(combined)
        agent_tools, agent_finals = [], []
        for obj in objs:
            action = obj.get("action")
            if not action: continue
            if self._norm(action) == "final answer": agent_finals.append(obj)
            else: agent_tools.append(action)

        correct, total_calls, scenario_ok = self._sequential_tool_match(agent_tools, expected_tools)
        tool_success = (correct / total_calls) if total_calls > 0 else np.nan

        pairs = self._pairwise_finals(gold_finals, agent_finals)
        sims = []
        for g, p in pairs:
            if g or p:
                try: sims.append(self._cosine(g, p))
                except Excep
