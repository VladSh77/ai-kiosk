"""Main entry point for AI Kiosk application with secure error handling."""
import sys
import logging
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from config.settings import LOG_FILE, LOG_LEVEL, LOG_FORMAT, UNKNOWN_RESPONSE

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
        logger.info("AI Kiosk initialized")
    
    def start(self):
        """Start the kiosk main loop."""
        self.running = True
        logger.info("AI Kiosk started")
        
        try:
            while self.running:
                # TODO: Implement main voice loop
                # 1. Listen for voice input
                # 2. Convert speech to text
                # 3. Process query (menu/QA)
                # 4. Generate response
                # 5. Convert text to speech
                # 6. Play response
                pass
        except KeyboardInterrupt:
            logger.info("Received shutdown signal")
        except Exception as e:
            logger.error(f"Unexpected error: {e}", exc_info=True)
            # In production, might want to restart or show error screen
        finally:
            self.stop()
    
    def stop(self):
        """Gracefully shutdown the kiosk."""
        self.running = False
        logger.info("AI Kiosk stopped")
    
    def process_query(self, text: str) -> str:
        """Process user query and return appropriate response."""
        if not text or len(text) > 500:  # Security: limit input length
            logger.warning(f"Invalid query length: {len(text) if text else 0}")
            return UNKNOWN_RESPONSE
        
        # TODO: Implement menu/QA matching
        # For now, return unknown response
        return UNKNOWN_RESPONSE

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
