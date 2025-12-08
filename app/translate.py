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
            f"Then choose option 2: 'Install English ↔ Spanish Packages'."
        )


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


def _get_idiom_items(from_lang: str, to_lang: str):
    """
    Return a sorted list of idioms for this direction:
    items[i] = (normalized_idiom, idiom_translation).
    """
    if from_lang == "en" and to_lang == "es":
        base = IDIOMS.get("en_to_es", {})
    elif from_lang == "es" and to_lang == "en":
        base = IDIOMS.get("es_to_en", {})
    else:
        return []

    # Normalize keys so matching is easier
    normalized = {}
    for k, v in base.items():
        norm_key = _normalize_quotes(k).lower()
        normalized[norm_key] = v

    # Sort by length so longer idioms match first
    items = sorted(normalized.items(), key=lambda kv: len(kv[0]), reverse=True)
    return items


def _tag_idioms_with_items(text: str, items):
    """
    Replace known idioms in `text` with __IDIOM_i__ placeholders,
    where i is the index in `items`.
    """
    new_text = _normalize_quotes(text)
    lower_text = new_text.lower()

    for i, (idiom_norm, _idiom_trans) in enumerate(items):
        idx = lower_text.find(idiom_norm)
        if idx == -1:
            continue

        placeholder = f"__IDIOM_{i}__"
        end = idx + len(idiom_norm)

        # Replace in both strings so indices stay in sync
        new_text = new_text[:idx] + placeholder + new_text[end:]
        lower_text = lower_text[:idx] + placeholder.lower() + lower_text[end:]

    return new_text


def translate_text(text, from_lang, to_lang):
    """
    Translate text using Argos, with idiom handling for EN↔ES.
    """
    ensure_pack(from_lang, to_lang)

    # 1) Idiom list for this direction
    items = _get_idiom_items(from_lang, to_lang)

    if not items:
        # No idioms for this language pair -> normal Argos
        return T.translate(text, from_lang, to_lang)

    # 2) Tag idioms in source
    tagged_text = _tag_idioms_with_items(text, items)

    # 3) Argos translation on tagged text
    raw_translated = T.translate(tagged_text, from_lang, to_lang)

    # 4) Restore idioms:
    #    Accept "__IDIOM_24__", "_IDIOM_24_", "__IDIOM_24_", etc.
    def repl(match: re.Match) -> str:
        idx = int(match.group(1))
        if 0 <= idx < len(items):
            return items[idx][1]  # idiom_translation
        return match.group(0)     # fallback

    # _+ before and after = "one or more underscores".
    final_translated = re.sub(r"_+IDIOM_(\d+)_+", repl, raw_translated)

    return final_translated
