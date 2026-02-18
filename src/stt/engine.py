"""
Offline Speech-to-Text engine using Vosk and PyAudio.
Zero latency, no cloud dependencies, privacy-first.
"""
import os
import json
import queue
import logging
import threading
import struct
import pyaudio
from vosk import Model, KaldiRecognizer

# Імпортуємо поріг шуму з нашого єдиного джерела істини (Single Source of Truth)
try:
    from src.config.settings import NOISE_GATE_THRESHOLD
except ImportError:
    NOISE_GATE_THRESHOLD = 500

logger = logging.getLogger(__name__)

class STTEngine:
    """Production-ready Offline STT Engine with Noise Gate."""
    
    def __init__(self, model_path="src/assets/models/vosk-model-pl"):
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Vosk STT model not found at {model_path}. Please download it first.")
            
        # Завантажуємо модель у пам'ять
        logger.info("Loading offline Vosk STT model. This may take a few seconds...")
        self.model = Model(model_path)
        self.recognizer = KaldiRecognizer(self.model, 16000)
        
        self.audio = pyaudio.PyAudio()
        self.stream = None
        self.is_listening = False
        self.text_queue = queue.Queue()
        self.listen_thread = None
        
        logger.info("STT Engine initialized successfully.")

    def _get_rms(self, block):
        """Calculate Root Mean Square (energy) of audio block for Noise Gate."""
        count = len(block) // 2
        format_str = f"<{count}h"
        shorts = struct.unpack(format_str, block)
        sum_squares = sum(s * s for s in shorts)
        return (sum_squares / count) ** 0.5 if count > 0 else 0

    def start_listening(self):
        """Start capturing and transcribing audio in the background."""
        if self.is_listening:
            return
            
        self.stream = self.audio.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=16000,
            input=True,
            frames_per_buffer=4000
        )
        self.is_listening = True
        self.listen_thread = threading.Thread(target=self._listen_worker, daemon=True)
        self.listen_thread.start()
        logger.info("🎙️ Mikrofon włączony. Nasłuchiwanie...")

    def _listen_worker(self):
        """Background thread reading from microphone and feeding Vosk."""
        while self.is_listening:
            try:
                data = self.stream.read(4000, exception_on_overflow=False)
                
                # Застосування Noise Gate (ігноруємо тихі звуки та фоновий галас)
                rms = self._get_rms(data)
                if rms < NOISE_GATE_THRESHOLD:
                    continue  # Пропускаємо фрейм, якщо він тихіший за поріг
                
                if self.recognizer.AcceptWaveform(data):
                    result = json.loads(self.recognizer.Result())
                    text = result.get("text", "").strip()
                    if text:
                        logger.info(f"👤 Klient: {text}")
                        self.text_queue.put(text)
            except Exception as e:
                if self.is_listening:
                    logger.error(f"STT Error: {e}")

    def get_text(self, block=True, timeout=None):
        """Retrieve recognized text from the queue."""
        try:
            return self.text_queue.get(block=block, timeout=timeout)
        except queue.Empty:
            return ""

    def stop_listening(self):
        """Stop audio capture."""
        self.is_listening = False
        if self.stream:
            self.stream.stop_stream()
            self.stream.close()
        if self.listen_thread and self.listen_thread.is_alive():
            self.listen_thread.join(timeout=2)
        logger.info("🛑 Mikrofon wyłączony.")
        
    def __del__(self):
        self.stop_listening()
        if hasattr(self, 'audio') and self.audio:
            self.audio.terminate()
