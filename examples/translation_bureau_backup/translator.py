# This file defines the Translator agent for the Translation Bureau.

from examples.translation_bureau.apis import TranslationAPI

class Translator:
    def __init__(self, name: str, language_pairs: list[tuple[str, str]]):
        self.name = name
        self.language_pairs = language_pairs  # e.g., [("en", "es"), ("en", "fr")]
        self.translation_api = TranslationAPI() # Using the mock API for now

    def translate_text(self, text: str, source_language: str, target_language: str) -> str:
        """
        Translates a single piece of text.
        This is a placeholder and will be implemented later using a real API.
        """
        if (source_language, target_language) not in self.language_pairs:
            return f"Error: Translator {self.name} does not support {source_language} to {target_language}."

        print(f"Translator {self.name} is translating '{text}' from {source_language} to {target_language}.")
        # Simulate using the translation API
        translated_text = self.translation_api.translate(text, source_language, target_language)
        return translated_text
