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
