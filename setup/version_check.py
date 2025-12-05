import sys
import importlib
from importlib.metadata import version, PackageNotFoundError

print(f"PYTHON: {sys.version} \n")


def show(mod_name: str, dist_name: str | None = None):
    """
    mod_name  = name you import
    dist_name = name you pip install (None => same as mod_name)
    """
    if dist_name is None:
        dist_name = mod_name

    # Get package version from installed metadata (pip)
    try:
        ver = version(dist_name)
    except PackageNotFoundError:
        ver = "installed (no dist metadata)"

    # Try to import the module itself
    try:
        mod = importlib.import_module(mod_name)
    except Exception as e:
        print(f"{mod_name}: ERROR importing ({e}); dist version: {ver}")
        return None

    print(f"{mod_name}: {ver}")
    return mod


# ----- TORCH -----
torch = show("torch")
if torch is not None:
    try:
        print("  CUDA available:", torch.cuda.is_available())
        print("  CUDA version:", torch.version.cuda)
        if torch.cuda.is_available():
            print("  GPU:", torch.cuda.get_device_name(0))
    except Exception as e:
        print("  Torch CUDA info ERROR:", e)

print()

# ----- FASTER-WHISPER / CTRANSLATE2 -----
faster_whisper = show("faster_whisper", "faster-whisper")
ctranslate2 = show("ctranslate2", "ctranslate2")
print()

# ----- ARGOS & PIPER -----
argostranslate = show("argostranslate", "argostranslate")
piper = show("piper", "piper-tts")
print()

# ----- NUMPY & AUDIO LIBS -----
numpy = show("numpy", "numpy")
sounddevice = show("sounddevice", "sounddevice")
soundfile = show("soundfile", "soundfile")
webrtcvad = show("webrtcvad", "webrtcvad-wheels")

print("\nDONE")