import queue, sys
import sounddevice as sd

class AudioIn:
    def __init__(self, samplerate, block_seconds, input_index=None):
        self.q = queue.Queue()
        self.samplerate = samplerate
        self.blocksize = int(samplerate * block_seconds)
        self.stream = sd.InputStream(
            channels=1, samplerate=samplerate, dtype="float32",
            blocksize=self.blocksize, callback=self._cb,
            device=(input_index, None) if input_index is not None else None
        )

    def _cb(self, indata, frames, time_info, status):
        if status:
            print(status, file=sys.stderr)
        self.q.put(indata.copy().reshape(-1, 1))

    def __enter__(self):
        self.stream.__enter__()
        return self

    def __exit__(self, exc_type, exc, tb):
        self.stream.__exit__(exc_type, exc, tb)

    def get_block(self):
        return self.q.get()

def list_devices():
    return sd.query_devices()
