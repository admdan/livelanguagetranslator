import numpy as np, math, time
from faster_whisper import WhisperModel

class ASR:
    def __init__(self, model_size, device, compute_type=None, language=None, beam_size=5, temperature=0.0):
        if compute_type is None:
            compute_type = "float32" if device == "cuda" else "int8"
        self.model = WhisperModel(model_size, device=device, compute_type=compute_type)
        self.language = language
        self.beam_size = beam_size
        self.temperature = temperature

    def transcribe_np(self, pcm: np.ndarray):
        """pcm mono float32 [-1,1]; returns dict with text, confidence, segments, timings"""
        t0 = time.time()

        # 🔧 make sure it’s 1D float32 mono
        pcm_fixed = np.asarray(pcm, dtype="float32").reshape(-1)

        # 🔥 call Faster-Whisper directly on the NumPy audio (no temp file, no soundfile)
        segments, info = self.model.transcribe(
            pcm_fixed,
            language=self.language,
            beam_size=self.beam_size,
            temperature=self.temperature,
            vad_filter=True,
        )
        text = "".join([s.text for s in segments]).strip()
        # Confidence proxy: average exp(avg_logprob) across segments (0..1)
        probs = []
        seg_list = []
        for s in segments:
            seg_list.append({
                "start": s.start, "end": s.end, "text": s.text,
                "avg_logprob": getattr(s, "avg_logprob", None)
            })
            if getattr(s, "avg_logprob", None) is not None:
                probs.append(math.exp(s.avg_logprob))
        # Safely handle confidence if avg_logprob is missing
        if probs:
            conf = float(sum(probs) / len(probs))
        else:
            # Fallback: use 1.0 or 1.0 - no_speech_prob if available
            no_sp = getattr(info, "no_speech_prob", 0.0)
            conf = float(1.0 - no_sp) if no_sp else 1.0

        return {
            "text": text,
            "confidence": conf,
            "segments": seg_list,
            "language": getattr(info, "language", None),
            "elapsed_sec": time.time() - t0
        }

