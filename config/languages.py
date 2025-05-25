# Importing Modules
import json
from pathlib import Path
from typing import Dict, Any


class LanguageManager:
    """Manages multilingual support for HealthIntuit"""
    
    def __init__(self):
        self.current_language = "en"
        self.translations = self._load_translations()
    
    def _load_translations(self) -> Dict[str, Dict[str, str]]:
        """Loads translation files"""
        translations = {}
        lang_dir = Path("languages")
        lang_dir.mkdir(exist_ok=True)
        
        for lang_file in ["en.json", "fr.json"]:
            lang_path = lang_dir / lang_file
            if lang_path.exists():
                with open(lang_path, 'r', encoding='utf-8') as f:
                    lang_code = lang_file.split('.')[0]
                    translations[lang_code] = json.load(f)
        
        return translations
    
    def set_language(self, lang_code: str):
        """Sets current language"""
        if lang_code in self.translations:
            self.current_language = lang_code
    
    def get_text(self, key: str) -> str:
        """Gets translated text for current language"""
        return self.translations.get(self.current_language, {}).get(key, key)
    
    def get_available_languages(self) -> Dict[str, str]:
        """Gets available languages"""
        return {
            "en": "English",
            "fr": "Français"
        }

# Singleton instance
_language_manager = None

def get_language_manager() -> LanguageManager:
    global _language_manager
    if _language_manager is None:
        _language_manager = LanguageManager()
    return _language_manager
