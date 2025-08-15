# src/agentkit/models/loader.py
from agentkit.config import settings
from agentkit.pipeline import CustomTextGenerationPipeline

class ModelLoader:
    def __init__(self, cfg=None):
        self.cfg = cfg or settings

    def load(self, model_name=None, use_unsloth=True):
        name = model_name or self.cfg.model_name
        if use_unsloth:
            from unsloth import FastLanguageModel
            model, tokenizer = FastLanguageModel.from_pretrained(
                model_name=name,
                max_seq_length=self.cfg.gen.max_seq_length,
                dtype=None,
                load_in_4bit=self.cfg.device.use_4bit,
                device_map=self.cfg.device.device_map,
                max_memory=self.cfg.device.max_memory,
            )
            model.generation_config.max_new_tokens = self.cfg.gen.max_new_tokens
            model.generation_config.use_cache = self.cfg.gen.use_cache
            return model, tokenizer
        from transformers import AutoModelForCausalLM, AutoTokenizer
        tok = AutoTokenizer.from_pretrained(name)
        mdl = AutoModelForCausalLM.from_pretrained(name)
        return mdl, tok

    def build_pipeline(self, model_name=None, use_unsloth=True):
        model, tok = self.load(model_name, use_unsloth)
        return CustomTextGenerationPipeline(
            model=model,
            tokenizer=tok,
            max_length=self.cfg.gen.max_seq_length,
            max_new_tokens=self.cfg.gen.max_new_tokens,
            temperature=self.cfg.gen.temperature,
            do_sample=self.cfg.gen.do_sample,
        )
