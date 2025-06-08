# This file implements the main workflow for the Translation Bureau.

from examples.translation_bureau.project_manager import ProjectManager
from examples.translation_bureau.translator import Translator
from examples.translation_bureau.quality_assurance import QualityAssurance
from examples.translation_bureau.apis import TranslationAPI
from examples.translation_bureau.original_text import ORIGINAL_TEXTS

def run_translation_workflow():
    print("--- Starting Translation Bureau Workflow ---")

    # 1. Instantiate Agents and API
    project_manager = ProjectManager(name="Alice")
    # Translator capable of en->es and en->fr
    translator = Translator(name="Bob", language_pairs=[("en", "es"), ("en", "fr")])
    qa_agent = QualityAssurance(name="Charlie")
    # The API is used by Translator and potentially QA
    # translation_api = TranslationAPI() # Translator already instantiates its own

    print(f"\n--- Agents Initialized ---")
    print(f"Project Manager: {project_manager.name}")
    print(f"Translator: {translator.name}, Languages: {translator.language_pairs}")
    print(f"Quality Assurance: {qa_agent.name}")

    # 2. Define a Sample Translation Project
    source_language = "en"
    target_language = "es"
    text_key_to_translate = "en_question" # "How are you today?" - expected error in Spanish mock
    # text_key_to_translate = "en_idiom" # "It's raining cats and dogs." - expected error in Spanish mock
    # text_key_to_translate = "en_greeting" # "Hello, world!" - expected correct mock

    original_text = ORIGINAL_TEXTS.get(text_key_to_translate)

    if not original_text:
        print(f"\nError: Original text for key '{text_key_to_translate}' not found.")
        return

    print(f"\n--- New Translation Project ---")
    print(f"Project Manager: {project_manager.name}")
    print(f"Original Text ({source_language}): '{original_text}' (Key: {text_key_to_translate})")
    print(f"Target Language: {target_language}")

    # 3. Workflow Steps
    # Step 1: Project Manager initiates project (simplified for now)
    print(f"\n--- Step 1: Project Initiation (PM: {project_manager.name}) ---")
    print(f"PM {project_manager.name}: Assigning translation of '{original_text}' from {source_language} to {target_language} to Translator {translator.name}.")
    # In a more complex scenario, PM would call its manage_project method.

    # Step 2: Translator performs the translation
    print(f"\n--- Step 2: Translation (Translator: {translator.name}) ---")
    translated_text = translator.translate_text(original_text, source_language, target_language)
    print(f"Translator {translator.name}: Received text '{original_text}'. Translated to ({target_language}): '{translated_text}'.")

    if "Error:" in translated_text:
        print(f"PM {project_manager.name}: Translation failed. Project halted.")
        print("\n--- Translation Bureau Workflow Ended ---")
        return

    # Step 3: Translator submits to Quality Assurance
    print(f"\n--- Step 3: Submission to QA (Translator: {translator.name} to QA: {qa_agent.name}) ---")
    print(f"Translator {translator.name}: Submitting translation '{translated_text}' for QA.")

    # Step 4: Quality Assurance reviews the translation
    print(f"\n--- Step 4: Quality Assurance Review (QA: {qa_agent.name}) ---")
    # QA might use API's validate_term, e.g., to check "mundo" vs "world"
    # For "en_greeting" -> "es_greeting": "Hello, world!" -> "[mock-es] Hola, mundo!"
    # Let's test term validation for "mundo" (Spanish for "world").
    # The glossary entry for "mundo" in Spanish is "Tierra".
    term_to_validate_in_translation = "mundo"
    expected_glossary_definition_in_target_lang = "Tierra" # Spanish glossary definition for "mundo"

    print(f"QA {qa_agent.name}: Attempting term validation for '{term_to_validate_in_translation}' in target language '{target_language}'.")
    print(f"QA {qa_agent.name}: Expected glossary definition for this term is '{expected_glossary_definition_in_target_lang}'.")

    # QA can use the translator's API instance or have its own.
    # For simplicity, using the translator's API instance here.
    term_is_valid_according_to_glossary = translator.translation_api.validate_term(
        term_to_validate_in_translation,
        target_language, # language of the term "mundo"
        expected_glossary_definition_in_target_lang # expected definition from es glossary
    )

    if term_is_valid_according_to_glossary:
        print(f"QA {qa_agent.name}: Term validation for '{term_to_validate_in_translation}' in '{target_language}': PASSED (matches expected glossary definition '{expected_glossary_definition_in_target_lang}').")
    else:
        # This 'else' could mean the term is not in the glossary, or its definition doesn't match.
        print(f"QA {qa_agent.name}: Term validation for '{term_to_validate_in_translation}' in '{target_language}': FAILED (term not in glossary or definition does not match '{expected_glossary_definition_in_target_lang}').")

    qa_passes = qa_agent.review_translation(original_text, translated_text, source_language, target_language)
    # print(f"QA Agent {qa_agent.name}: Review completed. Translation approved: {qa_passes}.") # This is now printed inside review_translation

    # Step 5: Quality Assurance reports findings
    if qa_passes:
        print(f"QA Agent {qa_agent.name}: Translation is approved.")
    else:
        print(f"QA Agent {qa_agent.name}: Translation has issues. Requesting revision.")
        # Here, a revision loop could be implemented. For now, we just report.

    # Step 6: Project Manager receives the final status
    print(f"\n--- Step 6: Final Status to Project Manager (PM: {project_manager.name}) ---")
    if qa_passes:
        print(f"PM {project_manager.name}: Project for '{original_text}' completed successfully. Final translation: '{translated_text}'.")
    else:
        print(f"PM {project_manager.name}: Project for '{original_text}' requires revision. QA rejected the translation.")

    print("\n--- Translation Bureau Workflow Ended ---")

if __name__ == "__main__":
    run_translation_workflow()
