"""Kiosk mode management for fullscreen display."""
import logging
import subprocess
import sys
import time
import os
from pathlib import Path

logger = logging.getLogger(__name__)

class KioskMode:
    """Manage kiosk fullscreen mode."""
    
    def __init__(self):
        self.process = None
        self.display = os.environ.get('DISPLAY', ':0')
        self.xauthority = os.environ.get('XAUTHORITY', os.path.expanduser('~/.Xauthority'))
        
    def start_browser(self, url="http://localhost:8080"):
        """Start browser in kiosk mode."""
        try:
            # Check if we're on a graphical system
            if not self._check_x_server():
                logger.warning("No X server found, running in console mode")
                return False
            
            # Kill any existing browser instances
            self._kill_browsers()
            
            # Start Chromium in kiosk mode
            cmd = [
                'chromium-browser',
                '--kiosk',
                '--incognito',
                '--no-first-run',
                '--disable-pinch',
                '--overscroll-history-navigation=0',
                '--disable-features=TranslateUI',
                '--disk-cache-dir=/dev/null',
                '--disable-session-crashed-bubble',
                '--disable-infobars',
                '--check-for-update-interval=31536000',
                url
            ]
            
            logger.info(f"Starting browser in kiosk mode: {' '.join(cmd)}")
            self.process = subprocess.Popen(
                cmd,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                env={
                    'DISPLAY': self.display,
                    'XAUTHORITY': self.xauthority
                }
            )
            
            logger.info(f"Browser started with PID: {self.process.pid}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to start browser: {e}")
            return False
    
    def start_web_server(self):
        """Start the AI Kiosk web server."""
        try:
            # Import here to avoid circular imports
            sys.path.insert(0, str(Path(__file__).parent.parent.parent))
            from src.main import AIKiosk
            
            # Start kiosk in a separate process?
            # For now, just return the instance
            return AIKiosk()
            
        except Exception as e:
            logger.error(f"Failed to start web server: {e}")
            return None
    
    def _check_x_server(self):
        """Check if X server is running."""
        try:
            result = subprocess.run(
                ['xset', '-q'],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                env={'DISPLAY': self.display}
            )
            return result.returncode == 0
        except:
            return False
    
    def _kill_browsers(self):
        """Kill existing browser instances."""
        try:
            subprocess.run(['pkill', '-f', 'chromium.*kiosk'], 
                         stderr=subprocess.DEVNULL)
            time.sleep(1)
        except:
            pass
    
    def run_kiosk(self):
        """Run full kiosk mode with browser."""
        logger.info("Starting AI Kiosk in fullscreen mode")
        
        # Start web server
        kiosk = self.start_web_server()
        if not kiosk:
            logger.error("Failed to start web server")
            return
        
        # Start browser
        if not self.start_browser():
            logger.warning("Running in console mode only")
        
        # Run main loop
        try:
            kiosk.start()
        finally:
            self.cleanup()
    
    def cleanup(self):
        """Clean up kiosk processes."""
        if self.process:
            self.process.terminate()
            try:
                self.process.wait(timeout=5)
            except:
                self.process.kill()
        
        self._kill_browsers()
        logger.info("Kiosk mode cleaned up")

# Simple function to start kiosk
def start_kiosk():
    """Start the kiosk application."""
    kiosk_mode = KioskMode()
    kiosk_mode.run_kiosk()

if __name__ == "__main__":
    start_kiosk()
