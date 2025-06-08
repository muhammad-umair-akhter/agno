# This file will contain API definitions for the Translation Bureau.

class TranslationAPI:
    def __init__(self):
        self.mock_translations = {
            "en": {
                "es": lambda text: f"[mock-es] {text.replace('Hello', 'Hola').replace('world', 'mundo').replace('How are you', 'Cómo estás')}",
                "fr": lambda text: f"[mock-fr] {text.replace('Hello', 'Bonjour').replace('world', 'monde').replace('How are you', 'Comment ça va')}",
            },
            "es": {
                "en": lambda text: f"[mock-en] {text.replace('Hola', 'Hello').replace('mundo', 'world').replace('Cómo estás', 'How are you')}",
            },
            "fr": {
                "en": lambda text: f"[mock-en] {text.replace('Bonjour', 'Hello').replace('monde', 'world').replace('Comment ça va', 'How are you')}",
            }
        }
        self.glossary = {
            "en": {"world": "Earth", "hello": "greeting"},
            "es": {"mundo": "Tierra", "hola": "saludo"},
            "fr": {"monde": "Terre", "bonjour": "salutation"},
        }

    def translate(self, text: str, source_language: str, target_language: str) -> str:
        """
        Simulates translation between supported languages.
        """
        if source_language in self.mock_translations and \
           target_language in self.mock_translations[source_language]:
            translation_func = self.mock_translations[source_language][target_language]
            return translation_func(text)
        return f"Error: Translation from '{source_language}' to '{target_language}' not supported (mock)."

    def validate_term(self, term: str, language: str, expected_meaning: str) -> bool:
        """
        Simulates glossary lookup or term validation.
        Returns True if the term has the expected meaning in the glossary for the given language.
        """
        if language in self.glossary and term.lower() in self.glossary[language]:
            return self.glossary[language][term.lower()].lower() == expected_meaning.lower()
        return False
