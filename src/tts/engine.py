"""Text-to-Speech engine with Microsoft Azure Neural Voices via edge-tts."""
import logging
import threading
import queue
import asyncio
import os
import tempfile
import subprocess
import platform
import time
import edge_tts

logger = logging.getLogger(__name__)

class TTSEngine:
    """Production-ready Neural TTS engine."""
    
    def __init__(self):
        self.speech_queue = queue.Queue()
        self.is_speaking = False
        self.speaking_thread = None
        self.current_process = None
        self.voice = "pl-PL-ZofiaNeural" 
        self.os_type = platform.system()
        
        self._start_worker()
        logger.info(f"TTS Engine initialized: {self.voice} on {self.os_type}")

    def _clean_text(self, text):
        import re
        text = re.sub(r'```.*?```', '', text, flags=re.DOTALL)
        text = re.sub(r'#.*$', '', text, flags=re.MULTILINE)
        text = re.sub(r'[<>]', '', text)
        return text.strip()

    async def _generate_audio(self, text, output_file):
        communicate = edge_tts.Communicate(text, self.voice, rate="+5%")
        await communicate.save(output_file)

    def _play_audio_sync(self, file_path):
        try:
            if self.os_type == "Darwin":
                cmd = ["afplay", file_path]
            elif self.os_type == "Linux":
                cmd = ["mpg123", "-q", file_path]
            else:
                cmd = ["powershell", "-c", f'(New-Object Media.SoundPlayer "{file_path}").PlaySync()']
                
            self.current_process = subprocess.Popen(cmd)
            
            while self.current_process.poll() is None and self.is_speaking:
                time.sleep(0.1)
                
            if not self.is_speaking and self.current_process.poll() is None:
                self.current_process.terminate()
        except Exception as e:
            logger.error(f"Playback error: {e}")
        finally:
            self.current_process = None

    def _speech_worker(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        while self.is_speaking:
            try:
                text = self.speech_queue.get(timeout=0.5)
                if not text:
                    continue

                cleaned = self._clean_text(text)
                if not cleaned:
                    self.speech_queue.task_done()
                    continue

                logger.info(f"Speaking: {cleaned[:50]}...")
                fd, temp_path = tempfile.mkstemp(suffix=".mp3")
                os.close(fd)

                try:
                    loop.run_until_complete(self._generate_audio(cleaned, temp_path))
                    self._play_audio_sync(temp_path)
                finally:
                    if os.path.exists(temp_path):
                        os.remove(temp_path)

                self.speech_queue.task_done()
            except queue.Empty:
                continue
            except Exception as e:
                logger.error(f"TTS Worker Error: {e}")

        loop.close()

    def _start_worker(self):
        self.is_speaking = True
        self.speaking_thread = threading.Thread(target=self._speech_worker, daemon=True)
        self.speaking_thread.start()

    def speak(self, text):
        if text:
            self.speech_queue.put(text)

    def speak_wait(self, text):
        if not text:
            return
        self.speak(text)
        self.speech_queue.join()

    def stop(self):
        self.is_speaking = False
        if self.current_process and self.current_process.poll() is None:
            self.current_process.terminate()
        
        while not self.speech_queue.empty():
            try:
                self.speech_queue.get_nowait()
                self.speech_queue.task_done()
            except queue.Empty:
                break

        if self.speaking_thread and self.speaking_thread.is_alive():
            self.speaking_thread.join(timeout=2)
        logger.info("TTS stopped")

    def __del__(self):
        self.stop()
