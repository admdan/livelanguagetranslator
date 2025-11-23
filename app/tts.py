from piper.voice import PiperVoice
import sounddevice as sd
import numpy as np

def speak(text, voice_path, voice_config):
    # Load Piper voice
    voice = PiperVoice.load(voice_path, config_path=voice_config)

    # Prepare output audio stream
    stream = sd.OutputStream(
        samplerate=voice.config.sample_rate,
        channels=1,
        dtype="int16",
    )
    stream.start()

    try:
        # Your Piper version yields AudioChunk objects
        for chunk in voice.synthesize(text):
            pcm = None  # default

            # Try int16 array sources first
            if hasattr(chunk, "audio_int16_array"):
                pcm = chunk.audio_int16_array
            elif hasattr(chunk, "_audio_int16_array"):
                pcm = chunk._audio_int16_array
            # Try byte sources
            elif hasattr(chunk, "audio_int16_bytes"):
                pcm = np.frombuffer(chunk.audio_int16_bytes, dtype=np.int16)
            elif hasattr(chunk, "_audio_int16_bytes"):
                pcm = np.frombuffer(chunk._audio_int16_bytes, dtype=np.int16)
            # Float fallback
            elif hasattr(chunk, "audio_float_array"):
                pcm = (np.array(chunk.audio_float_array) * 32767).astype(np.int16)

            # If nothing worked, skip chunk
            if pcm is None:
                continue

            # Normalize shape
            pcm = np.asarray(pcm).reshape(-1)

            if pcm.size > 0:
                stream.write(pcm)
    finally:
        stream.stop()
        stream.close()
