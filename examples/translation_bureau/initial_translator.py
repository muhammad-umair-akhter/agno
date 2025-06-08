from typing import Any, Dict
import random
from examples.translation_bureau.task_models import TranslationTask
import examples.translation_bureau.workflow_states as ws

class EN_FRCA_InitialTranslator:
    def __init__(self, name: str = "EN_FRCA_InitialTranslator_Default"):
        self.name = name
        print(f"Agent {self.name} initialized: English to French (Canada) Initial Translator.")

    def perform_initial_translation(self, task: TranslationTask) -> bool:
        is_revision = task.current_state == ws.EN_FRCA_INITIAL_TRANSLATION_REVISION_PENDING
        step_details_str = "EN->FR-CA Initial Translation" + (" (Revision)" if is_revision else "")

        print(f"Agent {self.name} (Task {task.task_id}): Processing {step_details_str} for: '{task.original_text[:50]}...'")

        revision_feedback_summary = ""
        if is_revision:
            revision_feedback_summary = " (addressing feedback: " + "; ".join(fb['comments'][:20]+"..." for fb in task.qa_feedback[-1:]) + ")"
            print(f"Agent {self.name} (Task {task.task_id}): Revising initial translation based on feedback.")

        base_translation = f"Le texte source était: '{task.original_text[:30]}...'. Traduction initiale par {self.name}."

        # Simulate inclusion of universal names and potential untranslated terms
        # This is a very basic simulation. A real scenario would be more complex.
        original_lower = task.original_text.lower()

        # Include a universal name if present in source
        if "hockey" in original_lower:
            base_translation += " Le hockey est populaire."
        elif "cpu" in original_lower:
            base_translation += " Le CPU est rapide."
        elif "internet" in original_lower:
            base_translation += " L'accès internet est essentiel."

        # Simulate forgetting to translate a term from a mock term_base
        # (The term_base in apis.py has {'computer': 'ordinateur'} for FR_CA if project is proj_alpha)
        if "computer" in original_lower and task.metadata.get("project_code") == "proj_alpha":
            if random.random() < 0.5: # 50% chance of "forgetting"
                base_translation += " J'ai un nouveau computer." # Untranslated
                print(f"Agent {self.name} (Task {task.task_id}): SIMULATING forgotten translation for 'computer'.")
            else:
                base_translation += " J'ai un nouvel ordinateur." # Correctly translated
        elif "application" in original_lower and task.metadata.get("project_code") == "proj_alpha":
             if random.random() < 0.3: # 30% chance of "forgetting" for another term
                base_translation += " Cette application est utile." # Untranslated english term
                print(f"Agent {self.name} (Task {task.task_id}): SIMULATING forgotten translation for 'application'.")
             else:
                base_translation += " Ce logiciel est utile." # Correctly translated "application" to "logiciel"

        # Conditionally add terms that the CanadianFrenchGrammarAPI checks for (anglicisms, France-French)
        if "check" in original_lower or "verify" in original_lower:
            base_translation += " Il faut checker ça."
        elif "fun" in original_lower:
            base_translation += " C'est vraiment le fun."
        elif "car" in original_lower and "auto" not in original_lower :
             base_translation += " La voiture (ou char) est rouge."

        translated_text = f"{base_translation}{' (révisé)' if is_revision else ''}{revision_feedback_summary}"

        version_key = 'initial_translation_frca' + ('_rev' if is_revision and not task.text_versions.get('initial_translation_frca_rev') else '')
        task.add_text_version(version_name=version_key, text_content=translated_text, agent_name=self.name)

        next_state = ws.FRCA_GRAMMAR_REVIEW_PENDING

        event_details: Dict[str, Any] = {"agent": self.name, "task_id": task.task_id, "is_revision": is_revision, "output_version_key": version_key}
        task.update_state(new_state=next_state, agent_name=self.name,
                          action_details=f"{step_details_str} complete.",
                          event_details=event_details)
        return True

class FRCA_EN_InitialTranslator: # Keep ENCA translator simpler for now
    def __init__(self, name: str = "FRCA_EN_InitialTranslator_Default"):
        self.name = name
        print(f"Agent {self.name} initialized: French (Canada) to English Initial Translator.")

    def perform_initial_translation(self, task: TranslationTask) -> bool:
        is_revision = task.current_state == ws.ENCA_INITIAL_TRANSLATION_REVISION_PENDING
        step_details_str = "FR-CA->EN Initial Translation" + (" (Revision)" if is_revision else "")
        print(f"Agent {self.name} (Task {task.task_id}): Processing {step_details_str} for: '{task.original_text[:50]}...'")

        revision_feedback_summary = ""
        if is_revision:
            revision_feedback_summary = " (addressing feedback)"
            print(f"Agent {self.name} (Task {task.task_id}): Revising initial translation based on feedback.")

        base_translation = f"[EN Mock Translation of: {task.original_text[:30]}... by {self.name}"
        if "organize" in task.original_text.lower() or "realize" in task.original_text.lower():
            base_translation += " We will organize and realize the color of the program."
        else:
            base_translation += " We will use proper Canadian spelling like colour and analyse."

        translated_text = f"{base_translation}{' rev' if is_revision else ''}{revision_feedback_summary}]"

        version_key = 'initial_translation_enca' + ('_rev' if is_revision and not task.text_versions.get('initial_translation_enca_rev') else '')
        task.add_text_version(version_name=version_key, text_content=translated_text, agent_name=self.name)

        next_state = ws.ENCA_GRAMMAR_REVIEW_PENDING
        event_details: Dict[str, Any] = {"agent": self.name, "task_id": task.task_id, "is_revision": is_revision, "output_version_key": version_key}
        task.update_state(new_state=next_state, agent_name=self.name, action_details=f"{step_details_str} complete.", event_details=event_details)
        return True
