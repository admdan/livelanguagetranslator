import json
from pathlib import Path

def load_idiom_dict() -> dict:
    """
    Load idioms from app/idioms/idioms.json and return as a dictionary.
    """
    # Path to this file: app/idiom_loader.py
    # We need to go to: app/idioms/idioms.json
    here = Path(__file__).resolve().parent
    idioms_path = here / "idioms" / "idioms.json"

    with idioms_path.open("r", encoding="utf-8") as f:
        return json.load(f)


# Optional manual test
if __name__ == "__main__":
    idioms = load_idiom_dict()
    print("Example EN→ES:", idioms["en_to_es"].get("break a leg"))
    print("Example ES→EN:", idioms["es_to_en"].get("apretarse el cinturón"))