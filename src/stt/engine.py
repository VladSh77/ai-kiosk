"""Speech-to-Text engine with fallback mechanisms."""
import logging
import speech_recognition as sr
from pathlib import Path
import wave
import audioop

from config.settings import STT_ENGINE, STT_LANGUAGE, SAMPLE_RATE, SILENCE_THRESHOLD

logger = logging.getLogger(__name__)

class STTEngine:
    """Speech recognition engine with multiple backends."""
    
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        self.language = STT_LANGUAGE
        self.engine = STT_ENGINE
        
        # Adjust for ambient noise
        with self.microphone as source:
            logger.info("Calibrating microphone for ambient noise...")
            self.recognizer.adjust_for_ambient_noise(source, duration=1)
        
        logger.info(f"STT Engine initialized with {self.engine}, language: {self.language}")
    
    def listen(self, timeout=5, phrase_time_limit=10) -> str:
        """Listen for speech and convert to text."""
        try:
            with self.microphone as source:
                logger.debug("Listening for speech...")
                audio = self.recognizer.listen(
                    source,
                    timeout=timeout,
                    phrase_time_limit=phrase_time_limit
                )
            
            # Save audio for audit (optional)
            self._save_audio(audio)
            
            # Recognize speech
            text = self._recognize(audio)
            
            if text:
                logger.info(f"Recognized: {text}")
                self._save_transcript(text)
                return text
            
        except sr.WaitTimeoutError:
            logger.debug("Listening timeout - no speech detected")
        except sr.UnknownValueError:
            logger.debug("Could not understand audio")
        except sr.RequestError as e:
            logger.error(f"Speech recognition service error: {e}")
        except Exception as e:
            logger.error(f"Unexpected error in speech recognition: {e}", exc_info=True)
        
        return ""
    
    def _recognize(self, audio) -> str:
        """Recognize speech using configured engine."""
        try:
            if self.engine == 'google':
                return self.recognizer.recognize_google(audio, language=self.language)
            elif self.engine == 'sphinx':
                return self.recognizer.recognize_sphinx(audio, language=self.language)
            else:
                logger.warning(f"Unknown STT engine: {self.engine}, falling back to google")
                return self.recognizer.recognize_google(audio, language=self.language)
        except Exception as e:
            logger.debug(f"Recognition failed: {e}")
            return ""
    
    def _save_audio(self, audio):
        """Save audio for audit purposes (optional)."""
        try:
            from config.settings import AUDIO_DIR
            import datetime
            
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = AUDIO_DIR / f"audio_{timestamp}.wav"
            
            with open(filename, "wb") as f:
                f.write(audio.get_wav_data())
            
            logger.debug(f"Saved audio to {filename}")
        except Exception as e:
            logger.error(f"Failed to save audio: {e}")
    
    def _save_transcript(self, text):
        """Save transcript for audit."""
        try:
            from config.settings import TRANSCRIPTS_DIR
            import datetime
            
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = TRANSCRIPTS_DIR / f"transcript_{timestamp}.txt"
            
            with open(filename, "w", encoding="utf-8") as f:
                f.write(f"{timestamp}: {text}\n")
            
            logger.debug(f"Saved transcript to {filename}")
        except Exception as e:
            logger.error(f"Failed to save transcript: {e}")
