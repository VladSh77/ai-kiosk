import os
import random
import sys
import threading
import time
import tkinter as tk

from PIL import Image, ImageTk

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

        self.mode = "PROMO"
        self.last_interaction = time.time()
        self.stop_promo = threading.Event()
        self.nlp = NLPProcessor()
        self.promo_playlist = [
            "Karkandaki to zdrowsza alternatywa dla fastfoodów. Świeże i smaczne!",
            "Wszystkie karkandaki za osiem złotych! Kolejowa 41, Ostrów Wielkopolski.",
            "Sosy własnej produkcji są naprawdę bardzo dobre. Właściciel prowadzi lokal z pasji!",
            "Karkardanki podawane w błyskawicznym tempie. Każdy znajdzie coś dla siebie.",
        ]

        self.smart_replies = [
            "To ciekawe, ale u nas zawsze jest czas na karkandaka za 8 złotych!",
            "Świetne pytanie! Nasz właściciel z pasją tworzy te smaki, spróbuj wołowego.",
            "Interesujące! Ale czy wiesz, że mamy też karkandaki na słodko z nutellą?",
            "Nie znam odpowiedzi, ale polecam nasze karkandaki - wysoka ocena mówi sama za siebie!",
        ]

        self._setup_ui()
        self.start_promo_thread()

    def _setup_ui(self):
        try:
            img = Image.open("src/assets/images/karkandaki_box.jpg").resize(
                (700, 450), Image.Resampling.LANCZOS
            )
            self.photo = ImageTk.PhotoImage(img)
            tk.Label(self.root, image=self.photo, bg="#f9a03f").pack(pady=10)
        except Exception as e:
            print(f"[UI WARNING] Nie udało się załadować zdjęcia: {e}")

        tk.Label(
            self.root,
            text="KARKANDAKI – LEGENDA SMAKU!",
            font=("Helvetica", 40, "bold"),
            fg="white",
            bg="#f9a03f",
        ).pack()
        tk.Label(
            self.root,
            text="CENA: 8 ZŁ | ul. Kolejowa 41",
            font=("Helvetica", 28, "bold"),
            fg="white",
            bg="#f9a03f",
        ).pack(pady=5)

        self.status_label = tk.Label(
            self.root,
            text="ZAPYTAJ MNIE O COKOLWIEK",
            font=("Helvetica", 24, "italic"),
            bg="#f9a03f",
        )
        self.status_label.pack(pady=10)

        self.canvas = tk.Canvas(
            self.root, width=300, height=300, bg="#f9a03f", highlightthickness=0
        )
        self.canvas.pack(pady=5)
        self.circle = self.canvas.create_oval(
            10, 10, 290, 290, fill="white", outline="white"
        )
        self.btn_text = self.canvas.create_text(
            150, 150, text="START", font=("Helvetica", 40, "bold"), fill="#f9a03f"
        )

        self.canvas.tag_bind(
            self.circle, "<Button-1>", lambda e: self.activate_dialog()
        )
        self.canvas.tag_bind(
            self.btn_text, "<Button-1>", lambda e: self.activate_dialog()
        )

    def start_promo_thread(self):
        self.stop_promo.clear()
        threading.Thread(target=self._promo_loop, daemon=True).start()

    def _promo_loop(self):
        idx = 0
        while not self.stop_promo.is_set():
            if self.mode == "PROMO":
                try:
                    self.tts.speak_wait(self.promo_playlist[idx])
                except Exception as e:
                    print(f"[PROMO ERROR] Błąd TTS: {e}")
                idx = (idx + 1) % len(self.promo_playlist)
                time.sleep(3)
            else:
                time.sleep(1)

    def activate_dialog(self):
        if self.mode == "PROMO":
            print("\n[SYSTEM] >>> Zmiana trybu na DIALOG")
            self.mode = "DIALOG"
            self.stop_promo.set()
            self.tts.stop()
            self.canvas.itemconfig(self.circle, fill="red")
            self.canvas.itemconfig(self.btn_text, text="MÓW", fill="white")
            self.status_label.config(text="Słucham Cię! Mów śmiało.")
            threading.Thread(target=self._dialog_session, daemon=True).start()

    def _dialog_session(self):
        print("[DIALOG] Wątek wystartował. Uruchamianie nasłuchu STT...")
        try:
            self.stt.start_listening()
            self.last_interaction = time.time()
            while self.mode == "DIALOG":
                if time.time() - self.last_interaction > 15:
                    print("[DIALOG] Timeout 15s - brak aktywności.")
                    break

                text = self.stt.get_text()
        if text:
            print(f"[STT] Rozpoznano tekst: '{text}'")
            self.last_interaction = time.time()
            resp = self.nlp.generate_response(text)
                        if "pogod" in text.lower()
                        else random.choice(self.smart_replies)
                    )
                    print(f"[TTS] Rozpoczynam odtwarzanie odpowiedzi: '{resp}'")
                    self.tts.speak_wait(resp)
                    print("[TTS] Zakończono odtwarzanie.")
                    break  # Wracamy do ekranu głównego po jednej interakcji

                time.sleep(0.1)
        except Exception as e:
            print(f"[DIALOG CRITICAL ERROR] {e}")
        finally:
            print("[DIALOG] Czyszczenie... Zatrzymywanie STT.")
            self.stt.stop_listening()
            self.mode = "PROMO"
            self.root.after(0, self._reset_ui)
            self.start_promo_thread()
            print("[SYSTEM] >>> Powrót do trybu PROMO\n")

    def _reset_ui(self):
        self.canvas.itemconfig(self.circle, fill="white")
        self.canvas.itemconfig(self.btn_text, text="START", fill="#f9a03f")
        self.status_label.config(text="ZAPYTAJ MNIE O COKOLWIEK")


if __name__ == "__main__":
    print("[SYSTEM] Inicjalizacja Kiosku Karkandaki...")
    root = tk.Tk()
    app = KarkandakiKiosk(root)
    root.mainloop()
