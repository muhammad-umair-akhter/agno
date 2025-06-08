# This file defines the QualityAssurance agent for the Translation Bureau.

class QualityAssurance:
    def __init__(self, name: str):
        self.name = name

    def review_translation(self, original_text: str, translated_text: str, source_language: str, target_language: str) -> bool:
        """
        Reviews a translated text for quality.
        This is a placeholder and will be implemented with more sophisticated checks.
        Returns True if quality is acceptable, False otherwise.
        """
        print(f"QA Agent {self.name} is reviewing the translation of '{original_text}' ({source_language}) to '{translated_text}' ({target_language}).")

        # Basic check: ensure translation is not empty
        if not translated_text:
            print(f"QA {self.name}: FAILED - Translation is empty.")
            return False

        # Mock error detection:
        # For the specific example "en_question" -> "es_question"
        # ("How are you today?" -> "[mock-es] Cómo estás today?")
        # check for the untranslated "today?".
        if target_language == "es" and "today?" in translated_text and "How are you today?" in original_text:
            print(f"QA {self.name}: FAILED - Detected untranslated 'today?' in Spanish translation.")
            return False

        # Mock check for literal idiom translation (example)
        # "It's raining cats and dogs."
        if "raining cats and dogs" in original_text.lower():
            if target_language == "es" and "perros y gatos" in translated_text.lower():
                print(f"QA {self.name}: FAILED - Detected literal translation of idiom 'raining cats and dogs' to Spanish.")
                return False
            if target_language == "fr" and "chats et des chiens" in translated_text.lower():
                print(f"QA {self.name}: FAILED - Detected literal translation of idiom 'raining cats and dogs' to French.")
                return False

        # If no specific errors are caught, assume it passes for now.
        print(f"QA {self.name}: PASSED - No obvious errors detected in this mock review.")
        return True
