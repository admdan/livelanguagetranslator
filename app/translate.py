from argostranslate import translate as T, package as P

def ensure_pack(from_code, to_code):
    packs = {(p.from_code, p.to_code) for p in P.get_installed_packages()}
    if (from_code, to_code) not in packs:
        raise RuntimeError(
            f"Argos package {from_code}->{to_code} is not installed. "
            f"Please run the Argos setup script first:\n\n"
            f"  python setup/argossetup.py\n\n"
            f"Then choose option 2: 'Install English ↔ Spanish Packages'.")

def translate_text(text, from_lang, to_lang):
    ensure_pack(from_lang, to_lang)
    return T.translate(text, from_lang, to_lang)
