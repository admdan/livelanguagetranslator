import os, yaml, argparse

def load_config(default_path="config/default.yaml"):
    parser = argparse.ArgumentParser()
    parser.add_argument("--profile", default=default_path)
    parser.add_argument("--from", dest="from_lang", default=None)
    parser.add_argument("--to", dest="to_lang", default=None)
    parser.add_argument("--tts", dest="tts_enabled", action="store_true")
    parser.add_argument("--no-tts", dest="tts_enabled", action="store_false")
    parser.set_defaults(tts_enabled=None)
    args = parser.parse_args()

    with open(args.profile, "r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f)

    # CLI overrides
    if args.from_lang: cfg["translate"]["from_lang"] = args.from_lang
    if args.to_lang:   cfg["translate"]["to_lang"]   = args.to_lang
    if args.tts_enabled is not None: cfg["tts"]["enabled"] = args.tts_enabled

    # Expand “auto” device choice
    if cfg["asr"]["device"] == "auto":
        try:
            import torch
            cfg["asr"]["device"] = "cuda" if torch.cuda.is_available() else "cpu"
        except Exception:
            cfg["asr"]["device"] = "cpu"

    return cfg
