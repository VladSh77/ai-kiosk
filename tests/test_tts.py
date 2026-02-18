import sys
import os
import time
import logging

# Налаштування логування для тесту
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# Додаємо корінь проєкту до sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.tts.engine import TTSEngine

def main():
    print("🚀 Запуск тесту TTS...")
    tts = TTSEngine()
    
    # Тестова фраза для ресторану Karkandaki
    test_text = "Dzień dobry! Test systemu głosowego Karkandaki zakończony sukcesem. W czym mogę pomóc?"
    print(f"🔊 Відтворюю текст: {test_text}")
    
    # Використовуємо блокуючий виклик, щоб дочекатися завершення аудіо
    tts.speak_wait(test_text)
    
    print("✅ Тест успішно завершено.")

if __name__ == "__main__":
    main()
