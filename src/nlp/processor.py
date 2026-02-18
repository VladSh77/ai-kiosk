"""Natural Language Processing for menu and QA matching."""
import json
import logging
import re
from difflib import SequenceMatcher
from pathlib import Path

from config.settings import MENU_FILE, QA_FILE, UNKNOWN_RESPONSE

logger = logging.getLogger(__name__)

class NLPProcessor:
    """Process user queries against menu and QA database."""
    
    def __init__(self):
        self.menu_data = self._load_json(MENU_FILE)
        self.qa_data = self._load_json(QA_FILE)
        
        # Nowa baza wiedzy z knowledge.json
        self.knowledge = self._load_json(Path('data/knowledge.json'))
        
        self.unknown_response = UNKNOWN_RESPONSE
        
        logger.info(f"NLP Processor initialized with {self._count_menu_items()} menu items")
    
    def _load_json(self, file_path: Path) -> dict:
        """Load JSON data from file."""
        try:
            if file_path.exists():
                with open(file_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                logger.warning(f"File not found: {file_path}")
                return {}
        except Exception as e:
            logger.error(f"Error loading {file_path}: {e}")
            return {}
    
    def _count_menu_items(self) -> int:
        """Count total menu items."""
        count = 0
        for category in self.menu_data.get('categories', []):
            count += len(category.get('items', []))
        return count
    
    def _normalize_text(self, text: str) -> str:
        """Normalize text for matching."""
        text = text.lower()
        text = re.sub(r'[^\w\s]', '', text)
        return text.strip()
    
    def _extract_keywords(self, text: str) -> list:
        """Extract keywords from text."""
        stop_words = {'co', 'to', 'jest', 'na', 'w', 'i', 'lub', 'czy', 'ma', 'pan', 'pani'}
        words = self._normalize_text(text).split()
        return [w for w in words if w not in stop_words and len(w) > 2]
    
    def process_query(self, query: str) -> str:
        """Process user query and return appropriate response."""
        if not query or len(query) > 500:
            logger.warning(f"Invalid query: {query}")
            return self.unknown_response
        
        logger.info(f"Processing query: {query}")
        query_norm = self._normalize_text(query)
        
        # 1. Sprawdź w FAQ z knowledge.json
        if self.knowledge and 'faq' in self.knowledge:
            for key, answer in self.knowledge['faq'].items():
                if key in query_norm or any(word in query_norm for word in key.split('_')):
                    logger.info(f"Found FAQ match: {key}")
                    return answer
        
        # 2. Sprawdź w daniach z knowledge.json
        if self.knowledge and 'dishes' in self.knowledge:
            for dish in self.knowledge['dishes']:
                dish_name_norm = self._normalize_text(dish['name'])
                if dish_name_norm in query_norm or any(word in dish_name_norm for word in query_norm.split()):
                    logger.info(f"Found dish match: {dish['name']}")
                    return f"{dish['name']} – {dish['description']} Cena: {dish['price']} zł."
        
        # 3. Sprawdź w restauracji z knowledge.json
        if self.knowledge and 'restaurant' in self.knowledge:
            rest = self.knowledge['restaurant']
            if 'godzin' in query_norm or 'czynne' in query_norm or 'otwar' in query_norm:
                return rest.get('hours', self.unknown_response)
            if 'adres' in query_norm or 'gdzie' in query_norm or 'znajduje' in query_norm:
                return rest.get('address', self.unknown_response)
            if 'dowóz' in query_norm or 'dostaw' in query_norm or 'transport' in query_norm:
                return rest.get('delivery', self.unknown_response)
            if 'polecacie' in query_norm or 'dobre' in query_norm or 'specjały' in query_norm:
                if 'faq' in self.knowledge and 'polecacie' in self.knowledge['faq']:
                    return self.knowledge['faq']['polecacie']
        
        # 4. Jeśli nic nie znaleziono
        logger.info(f"No match found for: {query}")
        return self.unknown_response
    
    def get_all_menu(self) -> str:
        """Get full menu as response."""
        if not self.knowledge or 'dishes' not in self.knowledge:
            return "Przepraszam, menu niedostępne."
        
        response = "Nasze menu:\n"
        for dish in self.knowledge['dishes']:
            response += f"• {dish['name']} - {dish['price']} zł\n"
        
        return response
