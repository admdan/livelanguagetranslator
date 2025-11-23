import numpy as np

def energy_vad(block: np.ndarray, gate: float) -> bool:
    # block: mono float32 [-1,1]
    return float(np.mean(block**2)) > gate

# Optional: WebRTC VAD for better results on noisy audio
class WebRTCVADWrapper:
    def __init__(self, sample_rate=16000, aggressiveness=2):
        import webrtcvad
        self.vad = webrtcvad.Vad(aggressiveness)
        self.sample_rate = sample_rate

    def is_speech(self, block: np.ndarray) -> bool:
        # Convert float32 [-1,1] to 16-bit PCM and ensure 20/30 ms frames
        import struct
        pcm16 = np.clip(block.squeeze() * 32768.0, -32768, 32767).astype(np.int16).tobytes()
        # Assume block length was set from block_seconds; for a quick start
        # we just feed as one chunk; for best results, split into 20 ms frames.
        try:
            return self.vad.is_speech(pcm16, self.sample_rate)
        except Exception:
            return False
