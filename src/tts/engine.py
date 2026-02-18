"""Text-to-Speech engine with fallback and audio logging."""
import logging
import pyttsx3
from pathlib import Path
import threading
import queue
import time

from config.settings import TTS_ENGINE, TTS_VOICE, TTS_RATE, TTS_VOLUME

logger = logging.getLogger(__name__)

class TTSEngine:
    """Text-to-speech engine with queuing and error handling."""
    
    def __init__(self):
        self.engine = None
        self.speech_queue = queue.Queue()
        self.is_speaking = False
        self.speaking_thread = None
        self.voice = TTS_VOICE
        self.rate = TTS_RATE
        self.volume = TTS_VOLUME
        
        self._init_engine()
        self._start_worker()
        
        logger.info(f"TTS Engine initialized with rate: {self.rate}")
    
    def _init_engine(self):
        """Initialize the TTS engine with configured settings."""
        try:
            self.engine = pyttsx3.init()
            
            # Set rate and volume
            self.engine.setProperty('rate', self.rate)
            self.engine.setProperty('volume', self.volume)
            
            voices = self.engine.getProperty('voices')
            selected_voice = None
            
            # Priorytet 1: Polski głos Zosia
            for voice in voices:
                if 'Zosia' in voice.name and 'pl_PL' in str(voice.languages):
                    selected_voice = voice
                    logger.info(f"Found Polish voice: {voice.name}")
                    break
            
            # Priorytet 2: Inne głosy żeńskie
            if not selected_voice:
                female_voices = ['Zuzana', 'Shelley', 'Sandy', 'Agnessa', 'Kate', 'Mariska', 'Milena', 'Monika', 'Natasha', 'Nika', 'Ola', 'Paulina', 'Tessa', 'Tina', 'Vani', 'Yelda', 'Yuna', 'Sara', 'Satu']
                for voice in voices:
                    if any(female in voice.name for female in female_voices):
                        selected_voice = voice
                        logger.info(f"Found female voice: {voice.name}")
                        break
            
            # Priorytet 3: Dowolny głos
            if not selected_voice and voices:
                selected_voice = voices[0]
                logger.info(f"Using default voice: {selected_voice.name}")
            
            if selected_voice:
                self.engine.setProperty('voice', selected_voice.id)
                logger.info(f"Selected voice: {selected_voice.name}")
            else:
                logger.warning("No voice found, using default")
            
        except Exception as e:
            logger.error(f"Failed to initialize TTS engine: {e}")
            self.engine = None
    
    def _start_worker(self):
        """Start background thread for speech queue processing."""
        self.is_speaking = True
        self.speaking_thread = threading.Thread(target=self._speech_worker, daemon=True)
        self.speaking_thread.start()
        logger.debug("TTS worker thread started")
    
    def _speech_worker(self):
        """Process speech queue in background."""
        while self.is_speaking:
            try:
                text = self.speech_queue.get(timeout=1)
                if text and self.engine:
                    logger.info(f"Speaking: {text[:50]}...")
                    self._speak_sync(text)
                    self._save_audio_log(text)
                self.speech_queue.task_done()
            except queue.Empty:
                continue
            except Exception as e:
                logger.error(f"Error in speech worker: {e}")
    
    def _speak_sync(self, text: str):
        """Synchronous speech function."""
        try:
            self.engine.say(text)
            self.engine.runAndWait()
        except Exception as e:
            logger.error(f"Speech error: {e}")
    
    def speak(self, text: str):
        """Queue text for speaking (non-blocking)."""
        if not text:
            return
        
        if len(text) > 1000:
            logger.warning(f"Text too long ({len(text)} chars), truncating")
            text = text[:997] + "..."
        
        self.speech_queue.put(text)
        logger.debug(f"Queued speech: {text[:50]}...")
    
    def speak_wait(self, text: str):
        """Speak text and wait for completion (blocking)."""
        if not text:
            return
        
        if not self.engine:
            logger.error("TTS engine not available")
            return
        
        try:
            logger.info(f"Speaking (blocking): {text[:50]}...")
            self._speak_sync(text)
            self._save_audio_log(text)
        except Exception as e:
            logger.error(f"Speech error: {e}")
    
    def _save_audio_log(self, text: str):
        """Save speech text to log for audit."""
        try:
            from config.settings import TRANSCRIPTS_DIR
            import datetime
            
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = TRANSCRIPTS_DIR / f"tts_{timestamp}.txt"
            
            with open(filename, "w", encoding="utf-8") as f:
                f.write(f"{timestamp}: {text}\n")
            
            logger.debug(f"Saved TTS log to {filename}")
        except Exception as e:
            logger.error(f"Failed to save TTS log: {e}")
    
    def stop(self):
        """Stop the TTS engine gracefully."""
        self.is_speaking = False
        if self.speaking_thread and self.speaking_thread.is_alive():
            self.speaking_thread.join(timeout=2)
        
        if self.engine:
            try:
                self.engine.stop()
            except:
                pass
        
        logger.info("TTS engine stopped")
    
    def __del__(self):
        """Cleanup on deletion."""
        self.stop()
