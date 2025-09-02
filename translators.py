# translators.py

import deepl
from googletrans import Translator
from abc import ABC, abstractmethod
import traceback

# ======================================================================
# АБСТРАКТНИЙ БАЗОВИЙ КЛАС
# ======================================================================
class BaseTranslator(ABC):
    @abstractmethod
    def translate_batch(self, items: list[dict], src_lang: str, dest_lang: str) -> list[dict]:
        pass

# ======================================================================
# РЕАЛІЗАЦІЯ ДЛЯ GOOGLE TRANSLATE
# ======================================================================
class GoogleTranslator(BaseTranslator):
    def __init__(self):
        self.translator = Translator()

    def translate_batch(self, items: list[dict], src_lang: str, dest_lang: str) -> list[dict]:
        for item in items:
            if item['text'].strip():
                try:
                    translated_obj = self.translator.translate(item['text'], src=src_lang, dest=dest_lang)
                    item['translated'] = translated_obj.text
                except Exception as e:
                    print(f"Error translating with Google '{item['text']}': {e}")
                    item['translated'] = "ПОМИЛКА ПЕРЕКЛАДУ"
            else:
                item['translated'] = ''
        return items

# ======================================================================
# РЕАЛІЗАЦІЯ ДЛЯ DEEPL API
# ======================================================================
class DeepLTranslator(BaseTranslator):
    SUPPORTED_SOURCE_LANGS = {
        "Arabic": "AR", "Bulgarian": "BG", "Czech": "CS", "Danish": "DA",
        "German": "DE", "Greek": "EL", "English": "EN", "Spanish": "ES",
        "Estonian": "ET", "Finnish": "FI", "French": "FR", "Hebrew": "HE",
        "Hungarian": "HU", "Indonesian": "ID", "Italian": "IT", "Japanese": "JA",
        "Korean": "KO", "Lithuanian": "LT", "Latvian": "LV", "Norwegian (Bokmål)": "NB",
        "Dutch": "NL", "Polish": "PL", "Portuguese": "PT", "Romanian": "RO",
        "Russian": "RU", "Slovak": "SK", "Slovenian": "SL", "Swedish": "SV",
        "Thai": "TH", "Turkish": "TR", "Ukrainian": "UK", "Vietnamese": "VI",
        "Chinese": "ZH"
    }

    SUPPORTED_TARGET_LANGS = {
        "Arabic": "AR", "Bulgarian": "BG", "Czech": "CS", "Danish": "DA",
        "German": "DE", "Greek": "EL", "English (British)": "EN-GB",
        "English (American)": "EN-US", "Spanish": "ES", "Spanish (Latin American)": "ES-419",
        "Estonian": "ET", "Finnish": "FI", "French": "FR", "Hebrew": "HE",
        "Hungarian": "HU", "Indonesian": "ID", "Italian": "IT", "Japanese": "JA",
        "Korean": "KO", "Lithuanian": "LT", "Latvian": "LV", "Norwegian (Bokmål)": "NB",
        "Dutch": "NL", "Polish": "PL", "Portuguese (Brazilian)": "PT-BR",
        "Portuguese (European)": "PT-PT", "Romanian": "RO", "Russian": "RU",
        "Slovak": "SK", "Slovenian": "SL", "Swedish": "SV", "Thai": "TH",
        "Turkish": "TR", "Ukrainian": "UK", "Vietnamese": "VI",
        "Chinese (Simplified)": "ZH-HANS", "Chinese (Traditional)": "ZH-HANT"
    }
    
    def __init__(self, api_key: str):
        if not api_key:
            raise ValueError("API ключ для DeepL не може бути порожнім.")
        self.api_key = api_key
        try:
            self.translator = deepl.Translator(api_key)
            self.translator.get_usage()
        except Exception as e:
            raise ConnectionError(f"Не вдалося ініціалізувати DeepL. Перевірте API ключ та з'єднання. Помилка: {e}")

    def translate_batch(self, items: list[dict], src_lang: str, dest_lang: str) -> list[dict]:
        source_language = src_lang.upper() if src_lang != 'auto' else None
        target_language = dest_lang.upper() # ВИПРАВЛЕНО: гарантуємо верхній регістр

        texts_to_translate = [item['text'] for item in items if item['text'].strip()]
        
        if not texts_to_translate:
            return items 

        try:
            results = self.translator.translate_text(
                texts_to_translate,
                source_lang=source_language,
                target_lang=target_language
            )
            result_iter = iter(results)
            for item in items:
                if item['text'].strip():
                    item['translated'] = next(result_iter).text
                else:
                    item['translated'] = ''

        except deepl.DeepLException as e:
            print(f"Помилка API DeepL: {e}")
            error_message = f"ПОМИЛКА DEEPL: {e}"
            if "source_lang" in str(e) or "target_lang" in str(e):
                 error_message = f"ПОМИЛКА: Мова не підтримується вашим API."
            for item in items:
                item['translated'] = error_message
        except Exception as e:
            print(f"Загальна помилка під час перекладу: {e}")
            for item in items:
                item['translated'] = "ПОМИЛКА ПЕРЕКЛАДУ"

        return items