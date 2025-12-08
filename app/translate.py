from argostranslate import translate as T, package as P
import re

from .idioms_loader import load_idiom_dict

# Load idioms once at import time
IDIOMS = load_idiom_dict()


def ensure_pack(from_code, to_code):
    packs = {(p.from_code, p.to_code) for p in P.get_installed_packages()}
    if (from_code, to_code) not in packs:
        raise RuntimeError(
            f"Argos package {from_code}->{to_code} is not installed. "
            f"Please run the Argos setup script first:\n\n"
            f"  python setup/argossetup.py\n\n"
            f"Then choose option 2: 'Install English ↔ Spanish Packages'.")

def _normalize_quotes(s: str) -> str:
    """
    Normalize curly quotes to straight quotes so Whisper output and JSON keys match better.
    """
    return (
        s.replace("’", "'")
         .replace("‘", "'")
         .replace("“", '"')
         .replace("”", '"')
    )


def _get_idiom_mapping(from_lang: str, to_lang: str) -> dict:
    """Pick the right idiom dictionary based on direction."""
    if from_lang == "en" and to_lang == "es":
        base = IDIOMS.get("en_to_es", {})
    elif from_lang == "es" and to_lang == "en":
        base = IDIOMS.get("es_to_en", {})
    else:
        return {}

    # Normalize keys so matching is easier
    normalized = {}
    for k, v in base.items():
        norm_key = _normalize_quotes(k).lower()
        normalized[norm_key] = v
    return normalized


def _tag_idioms(text: str, mapping: dict):
    """
    Replace known idioms in `text` with __IDIOM_n__ placeholders.

    Returns:
        tagged_text (str),
        replacements (list[(placeholder, idiom_translation)])
    """
    if not mapping:
        return text, []

    # Normalize quotes and keep a lowercase copy for searching
    new_text = _normalize_quotes(text)
    lower_text = new_text.lower()

    replacements = []

    # Sort idioms by length so longer ones match first
    items = sorted(mapping.items(), key=lambda kv: len(kv[0]), reverse=True)

    for i, (idiom_norm, idiom_trans) in enumerate(items):
        # simple substring search in the lowercase version
        idx = lower_text.find(idiom_norm)
        if idx == -1:
            continue

        placeholder = f"__IDIOM_{i}__"

        # Replace in both strings so indices stay in sync
        end = idx + len(idiom_norm)
        new_text = new_text[:idx] + placeholder + new_text[end:]
        lower_text = lower_text[:idx] + placeholder.lower() + lower_text[end:]

        replacements.append((placeholder, idiom_trans))

    return new_text, replacements


def _restore_idioms(text: str, replacements):
    """Replace placeholders with idiom translations."""
    for placeholder, idiom_trans in replacements:
        text = text.replace(placeholder, idiom_trans)
    return text


def translate_text(text, from_lang, to_lang):
    print("\n[translate_text] CALL")
    print("  direction:", from_lang, "->", to_lang)
    print("  input   :", repr(text))

    ensure_pack(from_lang, to_lang)

    mapping = _get_idiom_mapping(from_lang, to_lang)
    print("  idioms loaded:", len(mapping))

    if mapping:
        tagged_text, repls = _tag_idioms(text, mapping)
        print("  TAGGED:", repr(tagged_text))
        print("  REPLS :", repls)

        raw_translated = T.translate(tagged_text, from_lang, to_lang)
        final_translated = _restore_idioms(raw_translated, repls)

        print("  RAW   :", repr(raw_translated))
        print("  FINAL :", repr(final_translated))
        return final_translated

    print("  (no idiom map for this direction)")
    return T.translate(text, from_lang, to_lang)