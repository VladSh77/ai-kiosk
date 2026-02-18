"""Configuration settings for AI Kiosk with security best practices."""
import os
from pathlib import Path

# Base paths
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / 'data'
LOGS_DIR = BASE_DIR / 'logs'
AUDIO_DIR = DATA_DIR / 'audio'
TRANSCRIPTS_DIR = DATA_DIR / 'transcripts'

# Ensure directories exist with correct permissions
for dir_path in [DATA_DIR, LOGS_DIR, AUDIO_DIR, TRANSCRIPTS_DIR]:
    dir_path.mkdir(mode=0o750, exist_ok=True)

# Kiosk settings
KIOSK_MODE = os.getenv('KIOSK_MODE', 'True').lower() == 'true'
KIOSK_FULLSCREEN = True
KIOSK_DEBUG = False  # Never enable in production

# Audio settings
SAMPLE_RATE = 16000
CHANNELS = 1
CHUNK_SIZE = 1024
SILENCE_THRESHOLD = 500  # ms
MAX_RECORDING_TIME = 10  # seconds

# STT (Speech-to-Text) settings
STT_ENGINE = 'google'  # fallback: 'sphinx' for offline
STT_LANGUAGE = 'uk-UA'  # Ukrainian primary, Russian secondary

# TTS (Text-to-Speech) settings
TTS_ENGINE = 'pyttsx3'
TTS_VOICE = 'ukrainian'  # Will try to find, fallback to default
TTS_RATE = 150
TTS_VOLUME = 0.9

# NLP settings
UNKNOWN_RESPONSE = "I don't know, ask operator"
MAX_QUERY_LENGTH = 500

# Logging
LOG_LEVEL = 'INFO'
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
LOG_FILE = LOGS_DIR / 'kiosk.log'
AUDIO_LOG_FILE = LOGS_DIR / 'audio_interactions.log'

# Security
SECRETS_FILE = BASE_DIR / 'config' / 'secrets.env'
ALLOWED_ORIGINS = ["http://localhost", "http://127.0.0.1"]
SESSION_TIMEOUT = 300  # seconds

# Menu data (will be loaded from JSON)
MENU_FILE = DATA_DIR / 'menu.json'
QA_FILE = DATA_DIR / 'qa.json'
