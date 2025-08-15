# src/agentkit/config.py
from __future__ import annotations

import os
import logging
from dataclasses import dataclass, field
from typing import Dict, Optional

try:
    import torch
except Exception:  # torch opsiyonel kurulumlarda import hatası olursa
    torch = None  # type: ignore


@dataclass
class DeviceConfig:
    """Çoklu GPU, 4bit yükleme ve bellek eşlemeleri için basit yapı."""
    device_map: str = "auto"           
    max_memory: Dict[int, str] = field(default_factory=lambda: {0: "14GB", 1: "14GB"})
    use_4bit: bool = True


@dataclass
class GenerationConfig:
    """Model üretim (generate) için varsayılanlar."""
    max_seq_length: int = 16384
    max_new_tokens: int = 512
    temperature: float = 0.0
    do_sample: bool = False
    use_cache: bool = True


@dataclass
class Settings:
    """
    Global ayarlar:
    - Ortam değişkenleri (CUDA_VISIBLE_DEVICES, UNSLOTH_DISABLE_FAST_GENERATION)
    - Torch varsayılan tensör tipi
    - Logging
    - Model/üretim konfigleri
    """
    # --- Ortam ---
    cuda_visible_devices: str = os.getenv("CUDA_VISIBLE_DEVICES", "0,1")
    unsloth_disable_fast_generation: str = os.getenv("UNSLOTH_DISABLE_FAST_GENERATION", "1")

    # --- Torch ---
    prefer_cuda_default_tensor: bool = True 
    force_cpu: bool = False                  

    # --- Logging ---
    log_level: str = os.getenv("LOG_LEVEL", "INFO")
    log_format: str = "[%(asctime)s] %(levelname)s %(name)s: %(message)s"

    # --- Model ve üretim ---
    model_name: str = os.getenv(
        "MODEL_NAME",
        "unsloth/Mistral-Small-3.2-24B-Instruct-2506-bnb-4bit"
    )
    device: DeviceConfig = field(default_factory=DeviceConfig)
    gen: GenerationConfig = field(default_factory=GenerationConfig)

    def apply(self) -> None:
        """
        Ortam değişkenlerini ve torch varsayılanlarını uygula.
        Bu fonksiyon tek bir kez, uygulama başlangıcında çağrılmalı.
        """
        os.environ["CUDA_VISIBLE_DEVICES"] = self.cuda_visible_devices
        os.environ["UNSLOTH_DISABLE_FAST_GENERATION"] = self.unsloth_disable_fast_generation

        logging.basicConfig(
            level=getattr(logging, self.log_level.upper(), logging.INFO),
            format=self.log_format,
        )
        logging.getLogger(__name__).info(
            "Environment set: CUDA_VISIBLE_DEVICES=%s, UNSLOTH_DISABLE_FAST_GENERATION=%s",
            os.environ.get("CUDA_VISIBLE_DEVICES"),
            os.environ.get("UNSLOTH_DISABLE_FAST_GENERATION"),
        )

        if torch is not None and not self.force_cpu:
            try:
                if self.prefer_cuda_default_tensor and torch.cuda.is_available():
                    torch.set_default_tensor_type(torch.cuda.FloatTensor)  # type: ignore
                    logging.getLogger(__name__).info("Torch default tensor -> torch.cuda.FloatTensor")
                else:
                    torch.set_default_tensor_type(torch.FloatTensor)       # type: ignore
                    logging.getLogger(__name__).info("Torch default tensor -> torch.FloatTensor")
            except Exception as e:
                logging.getLogger(__name__).warning("Torch default tensor ayarlanamadı: %s", e)

    @classmethod
    def from_env(cls) -> "Settings":
        """
        .env / ortamdan okuyarak Settings örneği üretir.
        İsterseniz buraya daha fazla env parametresi ekleyebilirsiniz.
        """
        mm_raw = os.getenv("MAX_MEMORY", "")
        if mm_raw:
            mm: Dict[int, str] = {}
            for part in mm_raw.split(","):
                idx, val = part.split(":")
                mm[int(idx.strip())] = val.strip()
        else:
            mm = {0: "14GB"}

        device_map = os.getenv("DEVICE_MAP", "auto")
        use_4bit = os.getenv("LOAD_IN_4BIT", "true").lower() in {"1", "true", "yes"}

        max_seq_length = int(os.getenv("MAX_SEQ_LENGTH", "16384"))
        max_new_tokens = int(os.getenv("MAX_NEW_TOKENS", "512"))
        temperature = float(os.getenv("TEMPERATURE", "0.0"))
        do_sample = os.getenv("DO_SAMPLE", "false").lower() in {"1", "true", "yes"}
        use_cache = os.getenv("USE_CACHE", "true").lower() in {"1", "true", "yes"}

        return cls(
            cuda_visible_devices=os.getenv("CUDA_VISIBLE_DEVICES", "0,1"),
            unsloth_disable_fast_generation=os.getenv("UNSLOTH_DISABLE_FAST_GENERATION", "1"),
            prefer_cuda_default_tensor=os.getenv("PREFER_CUDA_TENSOR", "true").lower() in {"1", "true", "yes"},
            force_cpu=os.getenv("FORCE_CPU", "false").lower() in {"1", "true", "yes"},
            log_level=os.getenv("LOG_LEVEL", "INFO"),
            model_name=os.getenv(
                "MODEL_NAME",
                "unsloth/Mistral-Small-3.2-24B-Instruct-2506-bnb-4bit"
            ),
            device=DeviceConfig(
                device_map=device_map,
                max_memory=mm,
                use_4bit=use_4bit,
            ),
            gen=GenerationConfig(
                max_seq_length=max_seq_length,
                max_new_tokens=max_new_tokens,
                temperature=temperature,
                do_sample=do_sample,
                use_cache=use_cache,
            ),
        )


settings = Settings.from_env()
