
# Teknofest-NLP

* LangChain tabanlı bir Telekom ajanı ve istenirse metrik (KPI) değerlendirme modülü. İsteğe bağlı sesli giriş (STT) ve sesli çıktı (TTS) desteği içerir.

  
Hızlı Başlangıç
```
git clone <repo-url>

cd llm-agent-kpi

python -m venv .venv && source .venv/bin/activate

pip install -U pip


# Bağımlılıkları senin ortamına göre kur:

# langchain, langchain-core, langchain-community, transformers, unsloth, sentence-transformers,

# pydantic, numpy, pandas, torch (CUDA/CPU durumuna göre), accelerate, soundfile, librosa vb.

export PYTHONPATH=src
```
  

Dizin Yapısı
```
llm-agent-kpi/

├─ pyproject.toml

├─ README.md

├─ .env.example

├─ data/

│ ├─ user.json

│ └─ packages.json

├─ scenarios/

│ └─ scenario1.json

├─ src/

│ └─ agentkit/

│ ├─ __init__.py

│ ├─ config.py

│ ├─ pipeline.py

│ ├─ models/

│ │ ├─ __init__.py

│ │ └─ loader.py

│ ├─ tools/

│ │ ├─ __init__.py

│ │ ├─ api_functions.py

│ │ ├─ schemas.py

│ │ └─ registry.py

│ ├─ agent/

│ │ ├─ __init__.py

│ │ └─ core.py

│ ├─ chat/

│ │ ├─ __init__.py

│ │ └─ cli.py

│ ├─ kpi/

│ │ ├─ __init__.py

│ │ └─ evaluator.py

│ └─ audio/

│ ├─ __init__.py

│ ├─ integration.py

│ └─ stt_tts_toolkit.py ← kendi dosyanızı buraya koyun

└─ scripts/

├─ run_chat.py

└─ run_kpi.py
```
  

Yapılandırma

  

.env.example içeriğini .env olarak kopyalayıp düzenleyin veya ortam değişkeni verin.

  

## Önemli anahtarlar:

  

```CUDA_VISIBLE_DEVICES ```, ``` FORCE_CPU ```

  

```MODEL_NAME```,``` DEVICE_MAP```, ```MAX_MEMORY```, ```LOAD_IN_4BIT```

  

```MAX_SEQ_LENGTH```, ```MAX_NEW_TOKENS```, ```TEMPERATURE```

  

```AGENTKIT_DATA_DIR```, ```AGENTKIT_USER_DB```, ```AGENTKIT_PACKAGES_DB```

  

Varsayılan veri dosyaları ```data/``` altındadır.

  

## Ajanı Çalıştırma (CLI)

  

- Metin tabanlı sohbet:

  
```
export PYTHONPATH=src

python scripts/run_chat.py
```
  
  

## Seçenekler:

  

--cpu CPU’da çalıştırır.

  

--no-unsloth Unsloth yerine Transformers yükleyici kullanır.

  

--audio STT/TTS özelliklerini etkinleştirir.

  

--asr-model ASR model kimliği.

  

--tts-model TTS model kimliği.

  

--speaker TTS konuşmacı adı/ID (model destekliyorsa).

  

Örnek:

  

```python scripts/run_chat.py --audio --asr-model selimc/whisper-large-v3-turbo-turkish --tts-model tts_models/tr/common-voice/glow-tts ```

  
  

## Sohbet içinde komutlar:

  

```/stt ```<dosya>: Ses dosyasını metne çevirip ajana gönderir.

  

```/tts ```[çıkış.wav]: Son ajan cevabını ses dosyasına dönüştürür. Varsayılan reply.wav.

  

## KPI Değerlendirme

  

- Senaryo tabanlı ölçüm:

  

```
export PYTHONPATH=src

python scripts/run_kpi.py --scenario scenarios/scenario1.json --out kpi.csv --verbose
```
  
## Çıktı metrikleri:

  

- tool_success_rate: Beklenen araç sırasına göre isabet oranı.

  

- scenario_success: Araç sırası tamamen doğruysa başarılı.

  

- semantic_similarity: Final Answer metin benzerliği (cümle gömme ile).

  

- response_time_mean, total_response_time: Çalışma süreleri.

  

## Senaryo formatı:
- ```scenario/``` dizininde bulunan 100 adet senaryo ile kpi yaklaşımları test edilmiştir ve sonuçları **scenario_kpi_evaluate.xlsx** excel tablosunda yer almaktadır.
```
{

"id": "S1",

"conversations": [

{ "role": "user", "content": "..." },

{ "role": "assistant", "content": "{\"thought\":\"...\",\"action\":\"Final Answer\",\"action_input\":\"...\"}" }

],

"critical_steps": ["getBillDetails"]

}```

#2025