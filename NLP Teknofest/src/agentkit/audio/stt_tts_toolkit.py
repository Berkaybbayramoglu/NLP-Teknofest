# -*- coding: utf-8 -*-
"""
LLM-free STT <-> TTS Dosya Dönüştürücü (Türkçe)
================================================
GitHub'a uygun, sınıf tabanlı bir araçtır. Aşağıdakileri destekler:
- ASR (Whisper large v3 turbo Türkçe) ile ses -> metin
- Coqui TTS ile metin -> ses
- Bir .txt dosyasındaki prompt'u "ajan"a gönderip cevabı .txt olarak kaydetme
  (ajanı bir Python fonksiyonu veya bir shell komutu olarak bağlayabilirsiniz).

Kurulum ve kullanım örnekleri için README.md dosyasına bakın.

Not: Bu modül, dış bağımlılıkları *çalışma zamanında* yüklemez. Gerekli paketleri
kullanıcı ortamına kurmanız gerekir (bkz. requirements.txt).
"""
from __future__ import annotations

import os
import sys
import json
import time
import shlex
import logging
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Optional, Dict, Any

__all__ = ["STTTTSConverter", "AgentSpec", "main"]
__version__ = "0.2.0"

log = logging.getLogger("stt_tts_toolkit")
if not log.handlers:
    _h = logging.StreamHandler(stream=sys.stdout)
    _h.setFormatter(logging.Formatter("[%(levelname)s] %(message)s"))
    log.addHandler(_h)
log.setLevel(os.environ.get("STT_TTS_LOGLEVEL", "INFO").upper())


@dataclass
class AgentSpec:
    """
    Ajan entegrasyonu için esnek tanım.

    Üç yoldan biriyle cevap üretebilirsiniz:
    1) python_func: Callable[[str], str]  → doğrudan Python fonksiyon çağrısı
    2) python_target: "modul_yolu:fonksiyon_adi"  → dinamik import ile çağrı
    3) shell_cmd: "komut --flag ..."  → komut satırı çalıştırılır, prompt argüman olarak eklenir

    Öncelik sırası: python_func > python_target > shell_cmd
    """
    python_func: Optional[Callable[[str], str]] = None
    python_target: Optional[str] = None
    shell_cmd: Optional[str] = None


class STTTTSConverter:
    """
    STT (ASR) ve TTS işlemlerini yöneten sınıf.

    Attributes
    ----------
    asr_model_id : str
        Hugging Face ASR model kimliği.
    tts_model_id : str
        Coqui TTS model kimliği.
    device : Optional[str]
        "cuda", "cpu" vb. Aksi halde otomatik seçmeye çalışır.
    tts_speaker : Optional[str]
        Çok konuşurlu modellerde kullanılacak konuşmacı adı.
    sample_rate : int
        Çıktı WAV örnekleme frekansı.
    agent : Optional[AgentSpec]
        Prompt'u işlemek için harici bir ajan spesifikasyonu.
    """

    def __init__(
        self,
        asr_model_id: str = "selimc/whisper-large-v3-turbo-turkish",
        tts_model_id: str = "tts_models/tr/common-voice/glow-tts",
        device: Optional[str] = None,
        tts_speaker: Optional[str] = None,
        sample_rate: int = 22050,
        agent: Optional[AgentSpec] = None,
    ) -> None:
        self.asr_model_id = asr_model_id
        self.tts_model_id = tts_model_id
        self.device = device or self._auto_device()
        self.tts_speaker = tts_speaker
        self.sample_rate = sample_rate
        self.agent = agent

        self._asr = None
        self._tts = None

        log.debug("Initialized with device=%s", self.device)

    # ----------------------- yükleyiciler -----------------------
    def _auto_device(self) -> str:
        # torch opsu yoksa CPU'ya düş
        try:
            import torch  # type: ignore
            if torch.cuda.is_available():
                return "cuda"
        except Exception:
            pass
        return "cpu"

    def _ensure_asr(self):
        if self._asr is None:
            from transformers import pipeline  # type: ignore
            log.info("ASR pipeline yükleniyor: %s", self.asr_model_id)
            self._asr = pipeline(
                task="automatic-speech-recognition",
                model=self.asr_model_id,
                device=0 if self.device == "cuda" else -1,
                chunk_length_s=30,
            )
        return self._asr

    def _ensure_tts(self):
        if self._tts is None:
            from TTS.api import TTS  # type: ignore
            log.info("TTS modeli yükleniyor: %s", self.tts_model_id)
            self._tts = TTS(self.tts_model_id)
        return self._tts

    # ----------------------- çekirdek işlemler -----------------------
    def transcribe_audio(self, audio_path: str, language: str = "tr") -> str:
        """
        Verilen ses dosyasını metne çevirir.

        Parameters
        ----------
        audio_path : str
            Girdi ses dosyası (wav/mp3/flac ...).
        language : str
            ISO dil kodu, varsayılan "tr".

        Returns
        -------
        str
            ASR çıktısı (metin).
        """
        asr = self._ensure_asr()
        log.info("ASR başlıyor: %s", audio_path)
        result = asr(audio_path, generate_kwargs={"language": language})
        # transformers>=4.40 için tipler: {"text": "..."} veya {"chunks":[...],"text":"..."}
        text = result.get("text") if isinstance(result, dict) else str(result)
        log.info("ASR tamamlandı (%d karakter).", len(text))
        return text or ""

    def synthesize_speech(self, text: str, out_wav_path: str) -> str:
        """
        Verilen metni ses dosyasına dönüştürür.

        Returns
        -------
        str
            Üretilen WAV dosyasının yolu.
        """
        tts = self._ensure_tts()
        out = Path(out_wav_path)
        out.parent.mkdir(parents=True, exist_ok=True)
        log.info("TTS başlıyor → %s", out.as_posix())
        # Coqui TTS API: tts_to_file(text=..., file_path=..., speaker=..., language=...)
        kwargs: Dict[str, Any] = {"text": text, "file_path": out.as_posix()}
        if self.tts_speaker:
            kwargs["speaker"] = self.tts_speaker
        tts.tts_to_file(**kwargs)
        log.info("TTS tamamlandı (%s).", out.name)
        return out.as_posix()

    # ----------------------- dosya iş akışları -----------------------
    def audio_to_text_file(self, audio_path: str, out_txt_path: str, language: str = "tr") -> str:
        text = self.transcribe_audio(audio_path, language=language)
        out = Path(out_txt_path)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(text, encoding="utf-8")
        log.info("Transkript kaydedildi: %s", out.as_posix())
        return out.as_posix()

    def text_file_to_audio(self, in_txt_path: str, out_wav_path: str) -> str:
        text = Path(in_txt_path).read_text(encoding="utf-8")
        return self.synthesize_speech(text, out_wav_path)

    def audio_to_tts(self, audio_path: str, out_wav_path: str, language: str = "tr") -> str:
        text = self.transcribe_audio(audio_path, language=language)
        return self.synthesize_speech(text, out_wav_path)

    # ----------------------- ajan entegrasyonu -----------------------
    def _call_python_target(self, target: str, prompt: str) -> str:
        mod_name, func_name = target.split(":", 1)
        mod = __import__(mod_name, fromlist=[func_name])
        func = getattr(mod, func_name)
        return str(func(prompt))

    def _call_shell_cmd(self, cmd: str, prompt: str) -> str:
        # prompt'u son argüman olarak ekler ve stdout'u döner
        parts = shlex.split(cmd) + [prompt]
        proc = subprocess.run(parts, capture_output=True, text=True, check=False)
        if proc.returncode != 0:
            raise RuntimeError(f"Ajan komutu hata verdi (exit={proc.returncode}): {proc.stderr.strip()}")
        return proc.stdout.strip()

    def run_agent(self, prompt: str) -> str:
        """
        Prompt'u ajan aracılığıyla çalıştırır.

        AgentSpec verilmemişse, kimlikli echo davranışına düşer.
        """
        if self.agent is None:
            log.warning("AgentSpec tanımlı değil; echo davranışı kullanılacak.")
            return f"[echo] {prompt}"
        if self.agent.python_func is not None:
            return str(self.agent.python_func(prompt))
        if self.agent.python_target:
            return self._call_python_target(self.agent.python_target, prompt)
        if self.agent.shell_cmd:
            return self._call_shell_cmd(self.agent.shell_cmd, prompt)
        log.warning("AgentSpec boş; echo.")
        return f"[echo] {prompt}"

    def prompt_file_to_agent_txt(self, in_prompt_txt: str, out_txt_path: str) -> str:
        """
        Bir .txt dosyasındaki prompt'u ajana gönderir ve cevabı yeni bir .txt'e yazar.
        """
        prompt = Path(in_prompt_txt).read_text(encoding="utf-8").strip()
        if not prompt:
            raise ValueError(f"Boş prompt: {in_prompt_txt}")
        log.info("Ajan çalıştırılıyor (kaynak: %s)...", in_prompt_txt)
        reply = self.run_agent(prompt)
        out = Path(out_txt_path)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(str(reply), encoding="utf-8")
        log.info("Ajan cevabı kaydedildi: %s", out.as_posix())
        return out.as_posix()


# ----------------------- CLI -----------------------
def _build_argparser():
    import argparse
    p = argparse.ArgumentParser(
        prog="stt_tts_toolkit",
        description="Türkçe STT<->TTS dönüştürücü ve .txt -> ajan -> .txt iş akışı",
    )
    p.add_argument("--asr-model", default="selimc/whisper-large-v3-turbo-turkish")
    p.add_argument("--tts-model", default="tts_models/tr/common-voice/glow-tts")
    p.add_argument("--device", default=None, help="'cuda' veya 'cpu'. Boş bırakılırsa otomatik seçilir.")
    p.add_argument("--speaker", default=None, help="TTS konuşmacı adı (opsiyonel).")
    p.add_argument("--sample-rate", type=int, default=22050)

    sub = p.add_subparsers(dest="cmd", required=True)

    # Ses -> Metin
    sp1 = sub.add_parser("stt", help="Ses dosyasını metne çevir ve .txt olarak kaydet")
    sp1.add_argument("--in-audio", required=True)
    sp1.add_argument("--out-text", required=True)
    sp1.add_argument("--language", default="tr")

    # Metin -> Ses
    sp2 = sub.add_parser("tts", help="Metni sesten üret")
    sp2.add_argument("--in-text", required=True)
    sp2.add_argument("--out-audio", required=True)

    # Ses -> (ASR) -> Metin -> (TTS) -> Ses
    sp3 = sub.add_parser("stt-tts", help="Ses dosyasını ASR ile metne çevir ve yeniden seslendir")
    sp3.add_argument("--in-audio", required=True)
    sp3.add_argument("--out-audio", required=True)
    sp3.add_argument("--language", default="tr")

    # .txt prompt -> Ajan -> .txt cevap
    sp4 = sub.add_parser("agent", help=".txt prompt'u ajana gönder ve cevabı .txt kaydet")
    sp4.add_argument("--in-prompt", required=True)
    sp4.add_argument("--out-text", required=True)
    sp4.add_argument("--agent-python", default=None, help="modul_yolu:fonksiyon_adi")
    sp4.add_argument("--agent-cmd", default=None, help="Örn: 'python my_agent.py' (prompt argüman olarak eklenir)")

    return p

def main(argv=None) -> int:
    args = _build_argparser().parse_args(argv)

    agent = None
    if getattr(args, "agent_python", None) or getattr(args, "agent_cmd", None):
        agent = AgentSpec(
            python_target=getattr(args, "agent_python", None),
            shell_cmd=getattr(args, "agent_cmd", None),
        )

    tool = STTTTSConverter(
        asr_model_id=args.asr_model,
        tts_model_id=args.tts_model,
        device=args.device,
        tts_speaker=args.speaker,
        sample_rate=args.sample_rate,
        agent=agent,
    )

    try:
        if args.cmd == "stt":
            tool.audio_to_text_file(args.in_audio, args.out_text, language=args.language)
        elif args.cmd == "tts":
            tool.text_file_to_audio(args.in_text, args.out_audio)
        elif args.cmd == "stt-tts":
            tool.audio_to_tts(args.in_audio, args.out_audio, language=args.language)
        elif args.cmd == "agent":
            tool.prompt_file_to_agent_txt(args.in_prompt, args.out_text)
        else:
            raise ValueError(f"Bilinmeyen komut: {args.cmd}")
        return 0
    except Exception as e:
        log.error("Hata: %s", e)
        return 1

if __name__ == "__main__":
    raise SystemExit(main())