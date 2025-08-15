# src/agentkit/pipeline.py
import torch

class CustomTextGenerationPipeline:
    def __init__(
        self,
        model,
        tokenizer,
        max_length: int = 16384,
        max_new_tokens: int = 512,
        temperature: float = 0.0,
        do_sample: bool = False,
        return_full_text: bool = False,
        device: str | None = None,
    ):
        self.model = model
        self.tokenizer = tokenizer
        self.max_length = max_length
        self.max_new_tokens = max_new_tokens
        self.temperature = temperature
        self.do_sample = do_sample
        self.return_full_text = return_full_text
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")

    def __call__(self, inputs, **kwargs):
        prompt = inputs[0] if isinstance(inputs, list) else inputs
        enc = self.tokenizer(
            prompt,
            return_tensors="pt",
            truncation=True,
            max_length=self.max_length,
        )
        enc = {k: v.to(self.device) for k, v in enc.items()}
        out = self.model.generate(
            **enc,
            max_new_tokens=self.max_new_tokens,
            temperature=self.temperature,
            do_sample=self.do_sample,
        )
        full_text = self.tokenizer.decode(out[0], skip_special_tokens=True)
        if self.return_full_text:
            gen = full_text
        else:
            prompt_text = self.tokenizer.decode(enc["input_ids"][0], skip_special_tokens=True)
            gen = full_text[len(prompt_text):].lstrip() if full_text.startswith(prompt_text) else full_text
        return [{"generated_text": gen}]
