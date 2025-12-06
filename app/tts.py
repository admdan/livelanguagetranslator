from piper.voice import PiperVoice
import sounddevice as sd
import numpy as np
import soundfile as sf

def speak(text, voice_path, voice_config, save_path=None):
    """
        Speak the given text using Piper, and optionally save the TTS audio
        to a WAV file if save_path is provided.

        text:        string to synthesize
        voice_path:  path to the Piper voice .onnx file
        voice_config:path to the Piper voice .json config
        save_path:   optional path to write a .wav file for this TTS output
    """
    # Load Piper voice
    voice = PiperVoice.load(voice_path, config_path=voice_config)

    # Prepare output audio stream
    stream = sd.OutputStream(
        samplerate=voice.config.sample_rate,
        channels=1,
        dtype="int16",
    )
    stream.start()

    # Collect chunks for saving (if requested)
    all_chunks = []  # list of np.int16 arrays

    try:
        # Piper version yields AudioChunk objects
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

                # If we are saving, keep a copy
                if save_path is not None:
                    all_chunks.append(pcm.copy())
    finally:
        stream.stop()
        stream.close()

        # After playback, write to file if requested
        if save_path is not None and all_chunks:
            full_pcm = np.concatenate(all_chunks)
            # full_pcm is int16, so write directly as PCM_16
            sf.write(save_path, full_pcm, voice.config.sample_rate, subtype="PCM_16")

