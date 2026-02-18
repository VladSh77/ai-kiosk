import os
import random
import sys
import threading
import time
import tkinter as tk

from PIL import Image, ImageTk

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.nlp.processor import NLPProcessor
from src.stt.engine import STTEngine
from src.tts.engine import TTSEngine


class KarkandakiKiosk:
    def __init__(self, root):
        self.root = root
        self.root.attributes("-fullscreen", True)
        self.root.configure(bg="#f9a03f")

        self.tts = TTSEngine()
        self.stt = STTEngine()
        self.nlp = NLPProcessor()

        self.mode = "PROMO"
        self.last_interaction = time.time()
        self.stop_promo = threading.Event()

        self.promo_playlist = [
            "Karkandaki to zdrowsza alternatywa dla fastfoodów.",
            "Wszystkie karkandaki za osiem złotych!",
            "Sosy własnej produkcji są naprawdę bardzo dobre.",
        ]

        self._setup_ui()
        self.start_promo_thread()

    def _setup_ui(self):
        try:
            img = Image.open("src/assets/images/karkandaki_box.jpg").resize(
                (700, 450), Image.Resampling.LANCZOS
            )
            self.photo = ImageTk.PhotoImage(img)
            self.label = tk.Label(self.root, image=self.photo, bg="#f9a03f")
            self.label.pack(pady=20)

            self.status_label = tk.Label(
                self.root,
                text="ZAPYTAJ MNIE O COKOLWIEK",
                font=("Arial", 24, "bold"),
                bg="#f9a03f",
                fg="white",
            )
            self.status_label.pack(pady=10)

            self.canvas = tk.Canvas(
                self.root, width=200, height=200, bg="#f9a03f", highlightthickness=0
            )
            self.canvas.pack(pady=20)
            self.circle = self.canvas.create_oval(
                10, 10, 190, 190, fill="white", outline=""
            )
            self.btn_text = self.canvas.create_text(
                100, 100, text="START", font=("Arial", 20, "bold"), fill="#f9a03f"
            )

            self.canvas.tag_bind(
                self.circle, "<Button-1>", lambda e: self.toggle_mode()
            )
            self.canvas.tag_bind(
                self.btn_text, "<Button-1>", lambda e: self.toggle_mode()
            )
        except Exception as e:
            print(f"[UI ERROR] {e}")

    def toggle_mode(self):
        if self.mode == "PROMO":
            self.mode = "DIALOG"
            self.canvas.itemconfig(self.circle, fill="#ff4444")
            self.canvas.itemconfig(self.btn_text, text="STOP", fill="white")
            threading.Thread(target=self._dialog_session, daemon=True).start()
        else:
            self.mode = "PROMO"
            self._reset_ui()

    def _reset_ui(self):
        self.canvas.itemconfig(self.circle, fill="white")
        self.canvas.itemconfig(self.btn_text, text="START", fill="#f9a03f")
        self.status_label.config(text="ZAPYTAJ MNIE O COKOLWIEK")

    def start_promo_thread(self):
        def promo_loop():
            while not self.stop_promo.is_set():
                if self.mode == "PROMO":
                    msg = random.choice(self.promo_playlist)
                    self.tts.speak_wait(msg)
                    time.sleep(15)
                time.sleep(1)

        threading.Thread(target=promo_loop, daemon=True).start()

    def _dialog_session(self):
        print("[DIALOG] Wątek wystartował.")
        try:
            self.stt.start_listening()
            self.last_interaction = time.time()
            while self.mode == "DIALOG":
                if time.time() - self.last_interaction > 15:
                    break

                text = self.stt.get_text()
                if text:
                    print(f"[STT] Rozpoznano: {text}")
                    self.last_interaction = time.time()
                    resp = self.nlp.generate_response(text)
                    self.tts.speak_wait(resp)
                    break
                time.sleep(0.1)
        except Exception as e:
            print(f"[DIALOG ERROR] {e}")
        finally:
            self.stt.stop_listening()
            self.mode = "PROMO"
            self.root.after(0, self._reset_ui)


if __name__ == "__main__":
    root = tk.Tk()
    app = KarkandakiKiosk(root)
    root.mainloop()
