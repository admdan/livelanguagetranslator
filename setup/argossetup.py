from argostranslate import package as P, translate as T

tr_direction=[("en","es"),("es", "en")] # Set of direction of language translation

# (Choice 1 ) Method to show menu
def show_menu():
    print("\n=== Argos Translate Menu ===\n")
    print("1. Show Menu Again")
    print("2. Install English ↔ Spanish Packages")
    print("3. List Installed Packs")
    print("4. Test Translation")
    print("0. Exit")

# (Choice 2) Download necessary packages for English to Spanish translation models and vice versa
def install_packages():
    for p in P.get_available_packages():
        if (p.from_code, p.to_code) in tr_direction:
            print(f"Installing {p.from_code} to {p.to_code} (v{p.package_version})")
            P.install_from_path(p.download())
    print("\nInstallation complete.")

# (Choice 3) List installed packages
def list_packages():
    print("\nInstalled packages:")
    installed_packages = P.get_installed_packages()
    if not installed_packages:
        print("  No packages installed.\n")
        return

    for p in installed_packages:
        print(f"\t{p.from_code.upper()} to {p.to_code.upper()} (v{p.package_version})")

# (Choice 4) Quick offline test of packages for translation
def test_translation():
    print("\nTest translation:")
    print("1. English to Spanish")
    print("2. Spanish to English")
    try:
        choice = int(input("\nChoose an option (1 or 2): "))

        if choice not in [1,2]:
            print("\nInvalid choice. Please try again.\n")
            return

        # Get language codes based on user choice
        from_lang, to_lang = tr_direction[choice-1]

        if from_lang == "en":
            print("\nExamples of English words: hello, good morning, how are you, I love you")
        elif from_lang == "es":
            print("\nExamples of Spanish words: hola, buenos días, cómo estás, te quiero")

        # Asks for user input text
        text = input(f"\nEnter a sentence in {from_lang.upper()} language: ")

        # Translate using chosen direction
        result = T.translate(text, from_lang, to_lang)
        print(f"Translated text ({from_lang.upper()} to {to_lang.upper()}): ", result)

    except ValueError as ve:
        print("\nInvalid choice. Please try again.\n")
        return
    except Exception as e:
        print("Error: ", e)

def main():
    decision = 1  # Start with value 1 to show menu

    while decision != 0:
        show_menu()

        try:
            decision = int(input("\nEnter your choice (0–4): "))
        except ValueError:
            print("Please enter a number between 0 and 4.\n")
            decision = 1
            continue

        if decision == 1:
            continue  # Just shows the menu again
        elif decision == 2:
            install_packages()
        elif decision == 3:
            list_packages()
        elif decision == 4:
            test_translation()
        elif decision == 0:
            print("Goodbye!")
        else:
            print("Invalid choice. Please try again.")
            decision = 1  # Return to menu

if __name__ == "__main__":
    main()