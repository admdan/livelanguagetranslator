# 🗣️ Live Language Translator (LLT)

**Live Language Translator (LLT)** is a Python-based offline translation prototype designed to demonstrate real-time bilingual speech translation between **English** and **Spanish**.  
It uses a combination of **Argos Translate** for offline machine translation, **Faster-Whisper** for speech recognition, and **Piper TTS** for natural voice output — all runnable locally without internet connectivity.

---

## 🚀 Features

- 🔊 **Offline English ↔ Spanish Translation** using Argos Translate  
- 🎙️ **Speech-to-Text** transcription powered by Faster-Whisper  
- 🗣️ **Text-to-Speech Output** with Piper  
- 💻 Lightweight CLI interface for testing translations and setup
- 🧩 Modular setup for future hardware integration (earpiece prototype)

---

## 🧠 System Overview
[Microphone] → [Speech Recognition (Whisper)] → [Argos Translate] → [TTS (Piper)] → [Speaker]

## ⚙️ Setting Up the Environment
### 1. Start by cloning the repository to your computer:

```bash
git clone https://github.com/admdan/livelanguagetranslator.git
cd livelanguagetranslator
```
### 2.  Create a Virtual Environment:

- Make sure you have Python 3.11. If you don't, you can run these in Pycharm terminal:

``` bash
# Windows (and then follow subsequent steps to accept agreement terms)
winget install Python.Python.3.11

# macOS (if you have Homebrew)
brew update
brew install python@3.11
python3.11 --version
```

- Use Python 3.11 (Argos Translate does not yet support 3.13).
```bash
python -m venv .venv
```
- Activate it:
```bash
# Windows 
.\.venv\Scripts\activate

# macOs/Linux
source .venv/bin/activate
```

### 3. Install Dependencies
#### Option A - Recommended (using requirements.txt):
- Simply run:
```bash
pip install -r requirements.txt
```

#### Option B - Manual installation: 
- Make sure `pip` is up to date:
```bash
python -m pip install --upgrade pip
```
- Then install the required libraries:
```bash
pip install faster-whisper argostranslate==1.9.6 sounddevice soundfile websockets numpy
```

- (Optional for adding voice output later)
```bash
pip install piper-tts
```

### 4. Run the Argos Translate Setup
- This file lets you download translation models, list installed packages, and test basic translations directly.
```bash
python setup/argossetup.py
```
Configuration Profiles

LLT now includes multiple configuration profiles stored in the config/ directory.
Each profile adjusts device usage and model settings to support different hardware environments.

default.yaml – General-purpose settings for most systems.

cpu_safe.yaml – Forces CPU-only mode with lighter ASR settings.

gpu_fast.yaml – Enables GPU acceleration with higher-quality ASR settings.

To run the pipeline with a specific profile:

python -m app.pipeline --profile config/default.yaml
python -m app.pipeline --profile config/cpu_safe.yaml
python -m app.pipeline --profile config/gpu_fast.yaml


In PyCharm, three Run Configurations are included:

Run Pipeline – Default

Run Pipeline – CPU Safe

Run Pipeline – GPU Fast

These can be selected from the Run Configuration dropdown in the top-right corner of PyCharm.
## 🔮 Future Work
- 🎧 Integrate real-time microphone input and output
- 🔄 Enable two-way speech conversation simulation
- 🗣️ Add Piper voice playback for spoken responses
- 💡 Test hardware deployment (e.g., Raspberry Pi or Bluetooth earpiece)
- 🧰 Build GUI or mobile interface for ease of use

## 🧪 Development Notes
- Developed and tested with Python 3.11
- All translation runs offline once language models are installed
- Modular setup allows easy integration into hardware prototypes

## 👨‍💻 Authors
1. **Adam Nasir**, Penn State University
2. **Dominic Starr**, Penn State University
3. **Evan Sisler**, Penn State University
4. **Emerson Meara**, Penn State University
5. **Abdul Mohamed**, Penn State University
