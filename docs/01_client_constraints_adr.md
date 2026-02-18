# Architecture Decision Record 01: Wymagania Targowe Karkandaki

## Zidentyfikowane Ryzyka i Nasze Rozwiązania Architektoniczne:

1. Latency (Opóźnienia): Strumieniowanie asynchroniczne, lokalny STT (Vosk), optymalizacja TTS.
2. Hałas (Chaos): Lokalny STT z twardym Voice Activity Detection (VAD) + kierunkowy mikrofon sprzętowy.
3. Halucynacje (Alergie): Deterministyczny silnik reguł (Python if/else) dla menu. LLM nie ma prawa zmyślać składników.
4. Brak internetu (Offline): Architektura Local-First. Rozważenie migracji z Edge-TTS na Piper TTS, lokalny STT (Vosk), lokalny LLM (Ollama).
5. Pamięć sesji: Lokalna baza SQLite do śledzenia kontekstu rozmowy klienta w czasie rzeczywistym.
6. Interfejs (Wizerunek): Natywna aplikacja desktopowa w trybie Kiosk (Fullscreen), zero przeglądarek.
7. CRM (Brak zysku): Wbudowany moduł SQLite do zbierania zgód i numerów telefonów (Lead Generation).
8. Koszty (Tokeny): Wykorzystanie lokalnych modeli (Ollama), brak paywalli po 2 godzinach.
9. Regulamin (<16 lat): Walidacja wieku na poziomie logiki biznesowej Pythona (hardcoded rules), a nie tylko promptu AI.
10. Kontrola (Awarie serwera): Pełna niezależność chmurowa, aplikacja uruchamiana jako usługa systemowa z auto-restartem.
