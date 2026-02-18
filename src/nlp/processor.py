"""Natural Language Processing - naturalna rozmowa."""
import json
import logging
import re
from pathlib import Path

from config.settings import UNKNOWN_RESPONSE

logger = logging.getLogger(__name__)

class NLPProcessor:
    """Natural language processing dla restauracji Karkandaki."""
    
    def __init__(self):
        self.knowledge = self._load_json(Path('data/knowledge.json'))
        self.unknown = UNKNOWN_RESPONSE
        logger.info("NLP Processor gotowy do naturalnej rozmowy")
    
    def _load_json(self, path):
        try:
            if path.exists():
                with open(path, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except: pass
        return {}
    
    def _normalize(self, text):
        """Normalizacja tekstu - małe litery, bez znaków."""
        text = text.lower()
        text = re.sub(r'[^\w\s]', '', text)
        return text.strip()
    
    def _contains_any(self, text, words):
        """Sprawdza czy tekst zawiera któreś ze słów."""
        text = self._normalize(text)
        for word in words:
            if word in text:
                return True
        return False
    
    def process_query(self, query):
        """Przetwarzanie zapytania - naturalna rozmowa."""
        if not query:
            return self.unknown
        
        q = query.lower().strip()
        logger.info(f"🤔 Rozmówca: {q}")
        
        # Powitania
        if self._contains_any(q, ['cześć', 'witam', 'dzień dobry', 'hej', 'siema']):
            return "Dzień dobry! Miło Cię widzieć w Karkandaki. Nazywam się Arax i chętnie opowiem o naszej ormiańskiej kuchni. Może powiesz, na co masz ochotę? Mamy pyszne Karkandaki wytrawne i słodkie."
        
        # Jak się masz?
        if self._contains_any(q, ['jak leci', 'co słychać', 'jak się masz']):
            return "U mnie świetnie! Właśnie przygotowujemy świeże Karkandaki w kuchni. A Ty jak się masz? Może masz ochotę na coś pysznego?"
        
        # Co polecacie?
        if self._contains_any(q, ['polecacie', 'co dobre', 'specjały', 'najlepsze']):
            if 'faq' in self.knowledge and 'polecacie' in self.knowledge['faq']:
                return self.knowledge['faq']['polecacie']
            return "Najbardziej polecamy naszego Karkandaka ormiańskiego - to tradycyjny przepis z ziemniakami i ziołami. Ale jeśli lubisz mięso, to z wołowiną też jest pyszny! A może wolisz coś słodkiego?"
        
        # Karkandak (ogólnie)
        if 'karkandak' in q and not self._contains_any(q, ['ormiański', 'mięsem', 'kapustą', 'grzybami', 'nutellą', 'twarogiem']):
            return "Karkandak to nasze popisowe danie! To takie cieniutkie ciasto z różnymi nadzieniami. Mamy wytrawne: z ziemniakami (ormiański), z mięsem, z kapustą i grzybami. I słodkie: z nutellą oraz z twarogiem i miodem. Który Cię najbardziej interesuje?"
        
        # Konkretne dania
        if self.knowledge and 'dishes' in self.knowledge:
            for dish in self.knowledge['dishes']:
                dish_name = dish['name'].lower()
                if dish_name in q:
                    return f"{dish['name']} – {dish['description']} Cena: {dish['price']} zł. {dish.get('recommendation', 'Polecam!')}"
        
        # Ceny
        if self._contains_any(q, ['cena', 'ceny', 'ile kosztuje', 'drogo']):
            return "Nasze ceny są bardzo przystępne! Karkandak ormiański 28 zł, z mięsem 35 zł, z kapustą 24 zł, z grzybami 29 zł, a słodkie z nutellą 22 zł i z twarogiem 24 zł. Wszystkie dania są duże i sycące. Który brzmi zachęcająco?"
        
        # Godziny
        if self._contains_any(q, ['godziny', 'otwarcia', 'czynne', 'kiedy']):
            if 'restaurant' in self.knowledge:
                return self.knowledge['restaurant'].get('hours', "Jesteśmy czynni codziennie 8:00-22:00. Zapraszamy!")
        
        # Adres
        if self._contains_any(q, ['adres', 'gdzie', 'znajduje']):
            if 'restaurant' in self.knowledge:
                addr = self.knowledge['restaurant'].get('address', "ul. Kolejowa 41, Ostrów Wielkopolski")
                return f"Znajdziesz nas pod adresem: {addr}. To w samym centrum, łatwo trafić!"
        
        # Dowóz
        if self._contains_any(q, ['dowóz', 'dostawa', 'transport']):
            if 'restaurant' in self.knowledge:
                return self.knowledge['restaurant'].get('delivery', "Dowozimy na terenie miasta za 10 zł. Wystarczy zadzwonić pod 530 324 239!")
        
        # Dziękuję
        if self._contains_any(q, ['dziękuję', 'dzięki', 'thx']):
            return "Cała przyjemność po mojej stronie! Gdybyś miał jeszcze jakieś pytania, jestem tutaj. Smacznego i do usłyszenia!"
        
        # Nie wiem / nie rozumiem
        logger.info(f"Nie zrozumiałem: {q}")
        return "Hmm, nie jestem pewien czy dobrze zrozumiałem. Czy możesz powiedzieć inaczej? Możesz zapytać o polecane dania, ceny, godziny otwarcia, adres albo dowóz. Albo po prostu powiedz 'co polecacie' – chętnie doradzę!"
