import time, numpy as np
from .config import load_config
from .audio_io import AudioIn
from .vad import energy_vad, WebRTCVADWrapper
from .asr import ASR
from .translate import translate_text
from . import tts as tts_mod

def main():
    cfg = load_config()
    sr = cfg["audio"]["sample_rate"]
    block_sec = cfg["audio"]["block_seconds"]
    gate = cfg["vad"]["energy_gate"]
    pause_timeout = cfg["vad"]["pause_timeout"]

    # VAD
    vad_webrtc = None
    if cfg["vad"]["use_webrtc"]:
        try:
            vad_webrtc = WebRTCVADWrapper(sample_rate=sr, aggressiveness=2)
        except Exception:
            print("[VAD] webrtcvad not available; falling back to energy gate")

    # ASR
    asr = ASR(
        model_size=cfg["asr"]["model_size"],
        device=cfg["asr"]["device"],
        language=cfg["asr"]["language"],
        beam_size=cfg["asr"]["beam_size"],
        temperature=cfg["asr"]["temperature"],
    )

    from_lang = cfg["translate"]["from_lang"]
    to_lang   = cfg["translate"]["to_lang"]

    tts_enabled = cfg["tts"]["enabled"]
    voice_path  = cfg["tts"]["voice_path"]
    voice_cfg   = cfg["tts"]["voice_config"]

    print(f"[Ready] {from_lang} → {to_lang} | sr={sr} | model={cfg['asr']['model_size']} | device={cfg['asr']['device']}")
    print("Ctrl+C to exit.\n")

    buffered = []
    last_voice_time = None
    speech_active = False

    with AudioIn(sr, block_sec, input_index=cfg["audio"]["device_input_index"]) as ain:
        try:
            while True:
                block = ain.get_block()  # mono float32
                is_voice = (vad_webrtc.is_speech(block) if vad_webrtc else energy_vad(block, gate))

                if is_voice:
                    speech_active = True
                    last_voice_time = time.time()
                    buffered.append(block)
                elif speech_active and last_voice_time and (time.time() - last_voice_time) >= pause_timeout:
                    # flush phrase
                    pcm = np.concatenate(buffered, axis=0) if buffered else None
                    buffered.clear()
                    speech_active = False
                    if pcm is None or len(pcm) == 0:
                        continue

                    t0 = time.time()
                    asr_out = asr.transcribe_np(pcm)
                    text = asr_out["text"]
                    conf = asr_out["confidence"]
                    if not text:
                        print("[ASR] (empty)")
                        continue

                    print(f"[ASR {from_lang}] {text}  (conf={conf:.2f}, {asr_out['elapsed_sec']:.2f}s)")
                    translated = translate_text(text, from_lang, to_lang)
                    print(f"[→ {to_lang}] {translated}  (end-to-end {(time.time()-t0):.2f}s)")

                    if tts_enabled and translated:
                        try:
                            tts_mod.speak(translated, voice_path, voice_cfg)
                        except Exception as e:
                            print("[TTS] error:", e)
        except KeyboardInterrupt:
            print("\n[Exit] Bye!")

if __name__ == "__main__":
    main()
