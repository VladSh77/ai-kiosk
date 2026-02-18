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
        self.unknown_response = UNKNOWN_RESPONSE
        
        logger.info(f"NLP Processor initialized with {self._count_menu_items()} menu items and {len(self.qa_data.get('questions', []))} QA items")
    
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
        # Convert to lowercase, remove punctuation
        text = text.lower()
        text = re.sub(r'[^\w\s]', '', text)
        return text.strip()
    
    def _extract_keywords(self, text: str) -> list:
        """Extract keywords from text."""
        # Remove common stop words
        stop_words = {'де', 'і', 'в', 'на', 'з', 'до', 'та', 'але', 'чи', 'як', 'що', 'це', 'є', 'меню'}
        words = self._normalize_text(text).split()
        return [w for w in words if w not in stop_words and len(w) > 2]
    
    def _similarity(self, a: str, b: str) -> float:
        """Calculate string similarity ratio."""
        return SequenceMatcher(None, self._normalize_text(a), self._normalize_text(b)).ratio()
    
    def process_query(self, query: str) -> str:
        """Process user query and return appropriate response."""
        if not query or len(query) > 500:
            logger.warning(f"Invalid query: {query}")
            return self.unknown_response
        
        logger.info(f"Processing query: {query}")
        
        # Try QA matching first
        qa_response = self._match_qa(query)
        if qa_response:
            return qa_response
        
        # Try menu matching
        menu_response = self._match_menu(query)
        if menu_response:
            return menu_response
        
        # No match found
        logger.info(f"No match found for: {query}")
        return self.unknown_response
    
    def _match_qa(self, query: str) -> str:
        """Match query against QA database."""
        keywords = self._extract_keywords(query)
        
        for qa in self.qa_data.get('questions', []):
            # Check keyword overlap
            qa_keywords = qa.get('keywords', [])
            if not qa_keywords:
                continue
            
            # Count matching keywords
            matches = sum(1 for kw in keywords if kw in qa_keywords)
            if matches >= 2 or matches >= len(qa_keywords) * 0.5:
                logger.debug(f"QA match found: {qa.get('question')}")
                return qa.get('answer')
            
            # Check question similarity
            if self._similarity(query, qa.get('question', '')) > 0.6:
                logger.debug(f"QA similarity match: {qa.get('question')}")
                return qa.get('answer')
        
        return None
    
    def _match_menu(self, query: str) -> str:
        """Match query against menu items."""
        keywords = self._extract_keywords(query)
        best_match = None
        best_score = 0
        
        for category in self.menu_data.get('categories', []):
            for item in category.get('items', []):
                # Check item name
                name_score = self._similarity(query, item.get('name', ''))
                
                # Check keywords in name and description
                item_text = f"{item.get('name', '')} {item.get('description', '')}"
                item_text_norm = self._normalize_text(item_text)
                
                keyword_score = 0
                for kw in keywords:
                    if kw in item_text_norm:
                        keyword_score += 1
                
                keyword_score = keyword_score / max(len(keywords), 1)
                
                # Combined score
                score = max(name_score, keyword_score * 0.8)
                
                if score > best_score and score > 0.3:
                    best_score = score
                    best_match = item
        
        if best_match:
            logger.debug(f"Menu match found: {best_match.get('name')} (score: {best_score:.2f})")
            return self._format_menu_response(best_match)
        
        return None
    
    def _format_menu_response(self, item: dict) -> str:
        """Format menu item as response."""
        name = item.get('name', '')
        description = item.get('description', '')
        price = item.get('price', '')
        
        response = f"{name}. {description}"
        if price:
            response += f" Ціна: {price} грн."
        
        if 'weight' in item:
            response += f" Вага: {item['weight']}г."
        elif 'volume' in item:
            response += f" Об'єм: {item['volume']}мл."
        
        return response
    
    def get_all_menu(self) -> str:
        """Get full menu as response."""
        response = "Наше меню:\n"
        
        for category in self.menu_data.get('categories', []):
            response += f"\n{category.get('name')}:\n"
            for item in category.get('items', []):
                price = item.get('price', '')
                response += f"  • {item.get('name')} - {price} грн\n"
        
        return response
