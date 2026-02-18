import sys
import os
import time
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.stt.engine import STTEngine

def main():
    print("🎤 Uruchamianie testu STT (Vosk)...")
    try:
        stt = STTEngine()
        stt.start_listening()
        print("\n" + "="*50)
        print(">>> Mów teraz do mikrofonu (masz 10 sekund) <<<")
        print("="*50 + "\n")
        
        start_time = time.time()
        while time.time() - start_time < 10:
            text = stt.get_text(block=False)
            if text:
                print(f"✅ Rozpoznano: {text}")
            time.sleep(0.2)
            
        stt.stop_listening()
        print("\n✅ Test STT zakończony.")
    except Exception as e:
        print(f"\n❌ Błąd STT: {e}")

if __name__ == "__main__":
    main()
