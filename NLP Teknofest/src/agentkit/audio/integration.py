from agentkit.audio.stt_tts_toolkit import STTTTSConverter, AgentSpec

def make_audio_tool(agent_executor, asr_model=None, tts_model=None, device=None, speaker=None, sample_rate=22050):
    def run_agent(prompt: str) -> str:
        r = agent_executor.invoke({"input": prompt})
        return r.get("output", "")
    return STTTTSConverter(
        asr_model_id=asr_model or "selimc/whisper-large-v3-turbo-turkish",
        tts_model_id=tts_model or "tts_models/tr/common-voice/glow-tts",
        device=device,
        tts_speaker=speaker,
        sample_rate=sample_rate,
        agent=AgentSpec(python_func=run_agent),
    )
