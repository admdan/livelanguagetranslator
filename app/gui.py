import threading
import queue
import time
from datetime import timedelta
import numpy as np
import tkinter as tk
from tkinter import ttk, filedialog
import os
import soundfile as sf
import yaml

# Imports from pipeline
from .config import load_config
from .audio_io import AudioIn
from .vad import energy_vad, WebRTCVADWrapper
from .asr import ASR
from .translate import translate_text
from . import tts as tts_mod

# Config profiles
CONFIG_PROFILES = [
    ("Default (Auto)", "config/default.yaml"),
    ("GPU Fast Mode", "config/gpu_fast.yaml"),
    ("CPU Safe Mode", "config/cpu_safe.yaml"),
]


# Language direction choices
LANG_DIRECTIONS = [
    ("English → Spanish", "en", "es"),
    ("Spanish → English", "es", "en"),
]


# Main GUI app
class LLTApp(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Live Language Translator (LLT)")
        self.geometry("1150x650")
        self.minsize(900, 600)

        self.ui_queue = queue.Queue()
        self.worker_thread = None
        self.stop_event = threading.Event()
        self.session_start_time = None

        self._build_widgets()

        self.after(100, self._poll_queue)
        self.after(200, self._update_time)

    # GUI
    def _build_widgets(self):
        top_frame = ttk.Frame(self, padding=10)
        top_frame.pack(side=tk.TOP, fill=tk.X)

        # Profile selector
        ttk.Label(top_frame, text="Profile:").pack(side=tk.LEFT)
        self.profile_var = tk.StringVar()
        profile_names = [name for name, path in CONFIG_PROFILES]
        self.profile_combo = ttk.Combobox(
            top_frame,
            textvariable=self.profile_var,
            values=profile_names,
            state="readonly",
            width=20,
        )
        self.profile_combo.current(0)
        self.profile_combo.pack(side=tk.LEFT, padx=(0, 10))

        # Language direction selector
        ttk.Label(top_frame, text="Direction:").pack(side=tk.LEFT)
        self.direction_var = tk.StringVar()
        dir_names = [name for name, src, tgt in LANG_DIRECTIONS]
        self.direction_combo = ttk.Combobox(
            top_frame,
            textvariable=self.direction_var,
            values=dir_names,
            state="readonly",
            width=20,
        )
        self.direction_combo.current(0)
        self.direction_combo.pack(side=tk.LEFT, padx=5)

        # Voice selector (depends on profile + target language)
        ttk.Label(top_frame, text="Voice:").pack(side=tk.LEFT)
        self.voice_var = tk.StringVar()
        self.voice_combo = ttk.Combobox(
            top_frame,
            textvariable=self.voice_var,
            values=[],
            state="readonly",
            width=40,
        )
        self.voice_combo.pack(side=tk.LEFT, padx=5)

        # Keep currently loaded presets for mapping label -> id
        self.current_voice_presets = []

        # Bind profile combo and direction combo so that changing profile/direction refreshes voices
        self.profile_combo.bind("<<ComboboxSelected>>", lambda e: self._refresh_voice_choices())
        self.direction_combo.bind("<<ComboboxSelected>>", lambda e: self._refresh_voice_choices())

        self._refresh_voice_choices()

        # Mute TTS checkbox
        self.mute_tts_var = tk.BooleanVar(value=False)
        self.mute_check = ttk.Checkbutton(
            top_frame,
            text="Mute TTS",
            variable=self.mute_tts_var
        )
        self.mute_check.pack(side=tk.LEFT, padx=5)

        # Start/Stop buttons
        self.start_button = ttk.Button(top_frame, text="Start", command=self.start_session)
        self.start_button.pack(side=tk.LEFT, padx=5)

        self.stop_button = ttk.Button(top_frame, text="Stop", command=self.stop_session, state=tk.DISABLED)
        self.stop_button.pack(side=tk.LEFT, padx=5)

        # Session timer
        self.time_label_var = tk.StringVar(value="Session time: 00:00")
        ttk.Label(top_frame, textvariable=self.time_label_var).pack(side=tk.RIGHT)

        # Status + Confidence row
        status_frame = ttk.Frame(self, padding=5)
        status_frame.pack(side=tk.TOP, fill=tk.X)
        self.status_var = tk.StringVar(value="Idle")
        ttk.Label(status_frame, textvariable=self.status_var).pack(side=tk.LEFT)

        # Confidence label
        self.conf_var = tk.StringVar(value="Conf: -")
        ttk.Label(status_frame, textvariable=self.conf_var).pack(side=tk.RIGHT)

        # Audio level bar
        audio_frame = ttk.Frame(self, padding=5)
        audio_frame.pack(side=tk.TOP, fill=tk.X)
        ttk.Label(audio_frame, text="Audio level:").pack(side=tk.LEFT)

        self.audio_level = tk.DoubleVar(value=0.0)
        self.audio_bar = ttk.Progressbar(
            audio_frame,
            variable=self.audio_level,
            orient="horizontal",
            mode="determinate",
            maximum=100,
            length=300,
        )
        self.audio_bar.pack(side=tk.LEFT, padx=5)

        # Text areas
        mid_frame = ttk.Frame(self, padding=10)
        mid_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        # Make two equal-width columns
        mid_frame.columnconfigure(0, weight=1, uniform="cols")
        mid_frame.columnconfigure(1, weight=1, uniform="cols")
        mid_frame.rowconfigure(0, weight=1)

        # Transcription (left)
        t_frame = ttk.LabelFrame(mid_frame, text="Speech Transcription", padding=5)
        t_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 5))

        self.transcription_text = tk.Text(t_frame, wrap="word")
        self.transcription_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scroll1 = ttk.Scrollbar(t_frame, command=self.transcription_text.yview)
        scroll1.pack(side=tk.RIGHT, fill=tk.Y)
        self.transcription_text.configure(yscrollcommand=scroll1.set)

        # Translation (right)
        tr_frame = ttk.LabelFrame(mid_frame, text="Translated Speech", padding=5)
        tr_frame.grid(row=0, column=1, sticky="nsew", padx=(5, 0))

        self.translation_text = tk.Text(tr_frame, wrap="word")
        self.translation_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scroll2 = ttk.Scrollbar(tr_frame, command=self.translation_text.yview)
        scroll2.pack(side=tk.RIGHT, fill=tk.Y)
        self.translation_text.configure(yscrollcommand=scroll2.set)

        # Log area
        bottom_frame = ttk.Frame(self, padding=10)
        bottom_frame.pack(side=tk.BOTTOM, fill=tk.X)

        self.log_var = tk.StringVar(value="Ready.")
        ttk.Label(bottom_frame, textvariable=self.log_var).pack(side=tk.LEFT)

        # Save transcription button
        self.save_button = ttk.Button(
            bottom_frame,
            text="Save Transcript",
            command=self.save_transcript
        )
        self.save_button.pack(side=tk.RIGHT)

    # Session control
    def start_session(self):
        if self.worker_thread and self.worker_thread.is_alive():
            return

        # Clear
        self.transcription_text.delete("1.0", tk.END)
        self.translation_text.delete("1.0", tk.END)

        self.stop_event.clear()
        self.session_start_time = time.time()

        # Find selected direction
        selected_dir = self.direction_var.get()
        src_lang, tgt_lang = None, None
        for name, src, tgt in LANG_DIRECTIONS:
            if name == selected_dir:
                src_lang, tgt_lang = src, tgt
                break

        # Find selected config profile
        selected_prof = self.profile_var.get()
        profile_path = CONFIG_PROFILES[0][1]
        for name, path in CONFIG_PROFILES:
            if selected_prof == name:
                profile_path = path
                break

        # Read mute TTS setting
        mute_tts = self.mute_tts_var.get()

        # Map selected voice label to preset id
        selected_label = self.voice_var.get()
        voice_preset_id = None
        for p in self.current_voice_presets:
            if p.get("label", p.get("id")) == selected_label:
                voice_preset_id = p.get("id")
                break

        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.status_var.set("Running…")

        # Start worker thread
        self.worker_thread = threading.Thread(
            target=run_translation_session,
            args=(profile_path, src_lang, tgt_lang, self.ui_queue, self.stop_event, mute_tts, voice_preset_id),
            daemon=True,
        )
        self.worker_thread.start()


    def stop_session(self):
        self.stop_event.set()
        self.status_var.set("Stopping…")
        self.log_var.set("Stopping session…")

        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)


    # GUI update loops
    def _poll_queue(self):
        try:
            while True:
                msg = self.ui_queue.get_nowait()
                t = msg.get("type")

                if t == "transcript":
                    self._append_text(self.transcription_text, msg["text"])

                elif t == "translation":
                    self._append_text(self.translation_text, msg["text"])

                elif t == "audio_level":
                    self.audio_level.set(msg["value"])

                elif t == "status":
                    self.status_var.set(msg["text"])

                elif t == "log":
                    self.log_var.set(msg["text"])

                elif t == "conf": # Update confidence display
                    try:
                        self.conf_var.set(f"Conf: {msg['value']:.2f}")
                    except Exception:
                        self.conf_var.set("Conf: -")

        except queue.Empty:
            pass

        self.after(50, self._poll_queue)


    def _update_time(self):
        if self.session_start_time and not self.stop_event.is_set():
            elapsed = int(time.time() - self.session_start_time)
            self.time_label_var.set(
                f"Session time: {str(timedelta(seconds=elapsed))[:-3]}"
            )
        self.after(200, self._update_time)


    @staticmethod
    def _append_text(widget, text):
        widget.insert(tk.END, text + "\n")
        widget.see(tk.END)

    def save_transcript(self):
        """Save both transcription and translation to a .txt file."""
        transcript = self.transcription_text.get("1.0", tk.END).strip()
        translation = self.translation_text.get("1.0", tk.END).strip()

        if not transcript and not translation:
            self.log_var.set("Nothing to save.")  # optional
            return

        content = (
                "=== Speech Transcription ===\n"
                + transcript
                + "\n\n=== Translated Speech ===\n"
                + translation
                + "\n"
        )

        file_path = filedialog.asksaveasfilename(
            title="Save Transcript",
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
        )

        if not file_path:
            return

        try:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)
            self.log_var.set(f"Saved transcript to: {file_path}")
        except Exception as e:
            self.log_var.set(f"Error saving file: {e}")

    def _refresh_voice_choices(self):
        """Reload available TTS voices based on selected profile + target language."""
        # Determine selected config profile path
        selected_prof = self.profile_var.get()
        profile_path = CONFIG_PROFILES[0][1]
        for name, path in CONFIG_PROFILES:
            if selected_prof == name:
                profile_path = path
                break

        # Determine target language from direction
        selected_dir = self.direction_var.get()
        src_lang, tgt_lang = None, None
        for name, src, tgt in LANG_DIRECTIONS:
            if name == selected_dir:
                src_lang, tgt_lang = src, tgt
                break

        # Load YAML directly
        try:
            with open(profile_path, "r", encoding="utf-8") as f:
                cfg = yaml.safe_load(f)
        except Exception:
            cfg = {}

        tts_section = cfg.get("tts", {})
        presets_by_lang = tts_section.get("presets", {})
        lang_presets = presets_by_lang.get(tgt_lang, []) or []

        # Update combobox values
        labels = [p.get("label", p.get("id", "unknown")) for p in lang_presets]
        self.current_voice_presets = lang_presets

        self.voice_combo["values"] = labels
        if labels:
            # Keep current selection if possible, else default to first
            current = self.voice_var.get()
            if current not in labels:
                self.voice_var.set(labels[0])
        else:
            self.voice_var.set("")

# Worker thread pipeline logic
def run_translation_session(profile_path, src_lang, tgt_lang, ui, stop_event, mute_tts, voice_preset_id=None):

    # Load chosen profile
    cfg = load_config(default_path=profile_path)

    # Folder and counter for saving mic audio
    record_folder = "recordings"
    os.makedirs(record_folder, exist_ok=True)
    phrase_idx = 0

    # Override direction
    cfg["translate"]["from_lang"] = src_lang
    cfg["translate"]["to_lang"] = tgt_lang

    sr = cfg["audio"]["sample_rate"]
    block_sec = cfg["audio"]["block_seconds"]
    gate = cfg["vad"]["energy_gate"]
    pause_timeout = cfg["vad"]["pause_timeout"]

    # VAD
    vad_webrtc = None
    if cfg["vad"]["use_webrtc"]:
        try:
            vad_webrtc = WebRTCVADWrapper(sample_rate=sr, aggressiveness=2)
        except Exception:
            ui.put({"type": "log", "text": "[VAD] WebRTC unavailable, using energy gate."})

    # ASR
    asr = ASR(
        model_size=cfg["asr"]["model_size"],
        device=cfg["asr"]["device"],
        language=src_lang,
        beam_size=cfg["asr"]["beam_size"],
        temperature=cfg["asr"]["temperature"],
    )

    tts_section = cfg.get("tts", {})
    tts_enabled = tts_section.get("enabled", True)

    # Base fallback
    voice_path = tts_section.get("voice_path")
    voice_cfg = tts_section.get("voice_config")

    # Try to resolve from presets
    presets_by_lang = tts_section.get("presets", {})
    lang_presets = presets_by_lang.get(tgt_lang, []) if isinstance(presets_by_lang, dict) else []

    chosen = None
    if voice_preset_id:
        for p in lang_presets:
            if p.get("id") == voice_preset_id:
                chosen = p
                break

    # If no preset explicitly chosen (edge case), pick first for that language
    if chosen is None and lang_presets:
        chosen = lang_presets[0]

    if chosen is not None:
        voice_path = chosen.get("voice_path", voice_path)
        voice_cfg = chosen.get("voice_config", voice_cfg)
        ui.put({"type": "log", "text": f"[TTS] Using voice preset: {chosen.get('label', chosen.get('id'))}"})
    else:
        ui.put({"type": "log", "text": "[TTS] No matching preset; using fallback voice."})

    if not voice_path or not voice_cfg:
        ui.put({"type": "log", "text": "[TTS] Missing voice_path/voice_config; TTS may fail."})

    ui.put({"type": "status", "text": f"Ready ({src_lang} → {tgt_lang})"})
    ui.put({"type": "log", "text": "Listening… speak and pause to process."})

    buffered = []
    last_voice = None
    speech_active = False

    with AudioIn(sr, block_sec, input_index=cfg["audio"]["device_input_index"]) as ain:
        try:
            while not stop_event.is_set():

                block = ain.get_block()

                # Audio level
                if block is not None and block.size > 0:
                    rms = float(np.sqrt(np.mean(block**2)))
                else:
                    rms = 0.0
                level = min(100, rms * 4000)
                ui.put({"type": "audio_level", "value": level})

                # VAD
                is_voice = vad_webrtc.is_speech(block) if vad_webrtc else energy_vad(block, gate)

                if is_voice:
                    speech_active = True
                    last_voice = time.time()
                    buffered.append(block)

                elif speech_active and last_voice and (time.time() - last_voice >= pause_timeout):
                    pcm = np.concatenate(buffered, axis=0) if buffered else None
                    buffered.clear()
                    speech_active = False

                    if pcm is None or len(pcm) == 0:
                        continue

                    try:
                        file_path = os.path.join(record_folder, f"mic_phrase_{phrase_idx:03d}.wav")
                        sf.write(file_path, pcm, sr)  # pcm is float32, sr is sample rate
                        phrase_idx += 1
                        ui.put({"type": "log", "text": f"Saved mic audio: {file_path}"})
                    except Exception as e:
                        ui.put({"type": "log", "text": f"Error saving mic audio: {e}"})

                    # ASR
                    t0 = time.time()
                    out = asr.transcribe_np(pcm)
                    text = out["text"]
                    conf = out["confidence"]

                    if not text:
                        continue

                    # Send latest confidence to GUI
                    ui.put({"type": "conf", "value": conf})

                    ui.put({"type": "transcript",
                            "text": f"[{src_lang}] {text} (conf={conf:.2f})"})

                    # Translation
                    translated = translate_text(text, src_lang, tgt_lang)
                    ui.put({"type": "translation",
                            "text": f"[→ {tgt_lang}] {translated} (Δt={time.time()-t0:.2f}s)"})

                    # TTS
                    if tts_enabled and translated and not mute_tts:
                        ui.put({"type": "status", "text": "Speaking…"})

                        # Build filename for TTS audio for this phrase
                        tts_path = os.path.join(record_folder, f"tts_phrase_{phrase_idx - 1:03d}.wav")

                        try:
                            # Save TTS audio to file
                            tts_mod.speak(translated, voice_path, voice_cfg, save_path=tts_path)
                            ui.put({"type": "log", "text": f"Saved TTS audio: {tts_path}"})
                        except Exception as e:
                            ui.put({"type": "log", "text": f"[TTS Error] {e}"})
                        ui.put({"type": "status", "text": "Running…"})
        except Exception as e:
            ui.put({"type": "log", "text": f"[Error] {e}"})
            ui.put({"type": "status", "text": "Error"})

    ui.put({"type": "log", "text": "Session stopped."})
    ui.put({"type": "status", "text": "Idle"})



if __name__ == "__main__":
    app = LLTApp()
    app.mainloop()
