import argparse, os
from agentkit.agent.core import build_agent

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--cpu", action="store_true")
    p.add_argument("--no-unsloth", action="store_true")
    p.add_argument("--audio", action="store_true")
    p.add_argument("--asr-model", default="selimc/whisper-large-v3-turbo-turkish")
    p.add_argument("--tts-model", default="tts_models/tr/common-voice/glow-tts")
    p.add_argument("--speaker", default=None)
    p.add_argument("--stt-lang", default="tr")
    p.add_argument("--tts-out", default=None)
    args = p.parse_args()

    if args.cpu:
        os.environ["FORCE_CPU"] = "1"
        os.environ["CUDA_VISIBLE_DEVICES"] = ""

    agent = build_agent(use_unsloth=not args.no_unsloth)

    audio_tool = None
    if args.audio:
        try:
            from agentkit.audio.integration import make_audio_tool
            audio_tool = make_audio_tool(
                agent_executor=agent,
                asr_model=args.asr_model,
                tts_model=args.tts_model,
                speaker=args.speaker,
            )
        except Exception as e:
            print(f"[audio kapalı] {e}")

    print("Chat hazır. Çıkış: 'çık' / 'exit' / 'quit'.")
    print("Ses komutları: '/stt <ses_dosyası>'  '/tts [çıkış.wav]'")
    first, last_reply = True, ""

    while True:
        try:
            msg = input("🟢 Siz: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n👋 Görüşmek üzere!")
            break

        if msg.lower() in {"çık", "exit", "quit"}:
            print("👋 Görüşmek üzere!")
            break

        if msg.startswith("/stt"):
            if not audio_tool:
                print("⚠️ Ses özelliği kapalı. '--audio' ile aç.")
                continue
            parts = msg.split(" ", 1)
            if len(parts) < 2 or not parts[1].strip():
                print("⚠️ Kullanım: /stt <ses_dosyası>")
                continue
            in_audio = parts[1].strip()
            try:
                text = audio_tool.transcribe_audio(in_audio, language=args.stt_lang)
                print(f"[STT] {text}")
                payload = {"input": text, "chat_history": []} if first else {"input": text}
                resp = agent.invoke(payload)
                first = False
                last_reply = resp.get("output", "")
                print("\n🔵 Yanıt:\n" + last_reply + "\n")
            except Exception as e:
                print(f"❌ STT hata: {e}")
            continue

        if msg.startswith("/tts"):
            if not audio_tool:
                print("⚠️ Ses özelliği kapalı. '--audio' ile aç.")
                continue
            out_path = args.tts_out
            parts = msg.split(" ", 1)
            if len(parts) > 1 and parts[1].strip():
                out_path = parts[1].strip()
            if not out_path:
                out_path = "reply.wav"
            if not last_reply:
                print("⚠️ Henüz cevap yok.")
                continue
            try:
                path = audio_tool.synthesize_speech(last_reply, out_path)
                print(f"[TTS] kaydedildi → {path}")
            except Exception as e:
                print(f"❌ TTS hata: {e}")
            continue

        if not msg:
            print("⚠️ Boş mesaj.")
            continue

        resp = agent.invoke({"input": msg, "chat_history": []}) if first else agent.invoke({"input": msg})
        first = False
        last_reply = resp.get("output", "")
        print("\n🔵 Yanıt:\n" + last_reply + "\n")

if __name__ == "__main__":
    main()
