from argostranslate import package as P, translate as T
# Uncomment the codes for setup and test

# 1. Download necessary packages for English to Spanish translation models and vice versa
"""for p in P.get_available_packages():
    if (p.from_code, p.to_code) in {("en","es"),("es","en")}:
        P.install_from_path(p.download())"""

# 2. List installed packages
"""installed_packages = P.get_installed_packages()
print([(p.from_code, p.to_code, p.package_version) for p in installed_packages])"""

# 3. Quick offline test
print("EN to ES:", T.translate("Hello everyone", "en", "es"))
print("ES to EN:", T.translate("Estoy bien", "es", "en"))
