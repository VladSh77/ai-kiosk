"""Main entry point for AI Kiosk application with secure error handling."""
import sys
import logging
import time
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from config.settings import LOG_FILE, LOG_LEVEL, LOG_FORMAT, UNKNOWN_RESPONSE
from src.stt.engine import STTEngine
from src.tts.engine import TTSEngine
from src.nlp.processor import NLPProcessor

# Configure secure logging
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format=LOG_FORMAT,
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class AIKiosk:
    """Main kiosk application with voice interface."""
    
    def __init__(self):
        self.running = False
        self.stt = None
        self.tts = None
        self.nlp = None
        logger.info("AI Kiosk initialized")
    
    def initialize(self):
        """Initialize all components."""
        try:
            logger.info("Initializing AI Kiosk components...")
            self.tts = TTSEngine()
            self.stt = STTEngine()
            self.nlp = NLPProcessor()
            logger.info("All components initialized successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to initialize components: {e}", exc_info=True)
            return False
    
    def start(self):
        """Start the kiosk main loop."""
        if not self.initialize():
            logger.critical("Cannot start kiosk - initialization failed")
            return
        
        self.running = True
        logger.info("AI Kiosk started - listening for voice input")
        self.tts.speak_wait("Ласкаво просимо до ресторану Каркандакі. Чим я можу допомогти?")
        
        try:
            while self.running:
                # 1. Listen for voice input
                logger.debug("Waiting for voice input...")
                query = self.stt.listen(timeout=10)
                
                if not query:
                    continue
                
                # 2. Special commands
                if query.lower() in ['вихід', 'стоп', 'stop', 'exit']:
                    self.tts.speak("До побачення!")
                    self.stop()
                    break
                
                if query.lower() in ['меню', 'menu', 'що є']:
                    response = self.nlp.get_all_menu()
                    self.tts.speak(response)
                    continue
                
                # 3. Process query through NLP
                logger.info(f"Processing: {query}")
                response = self.nlp.process_query(query)
                
                # 4. Speak response
                self.tts.speak(response)
                
        except KeyboardInterrupt:
            logger.info("Received shutdown signal")
        except Exception as e:
            logger.error(f"Unexpected error in main loop: {e}", exc_info=True)
        finally:
            self.stop()
    
    def stop(self):
        """Gracefully shutdown the kiosk."""
        self.running = False
        if self.tts:
            self.tts.stop()
        logger.info("AI Kiosk stopped")

def main():
    """Application entry point with error handling."""
    kiosk = AIKiosk()
    
    try:
        kiosk.start()
    except Exception as e:
        logger.critical(f"Fatal error: {e}", exc_info=True)
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
