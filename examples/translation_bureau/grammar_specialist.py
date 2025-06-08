from typing import Any, Dict, Optional # Added Dict, Optional
# Import necessary models, states, and APIs
from examples.translation_bureau.task_models import TranslationTask
import examples.translation_bureau.workflow_states as ws
from examples.translation_bureau.apis import (
    CanadianFrenchGrammarAPI,
    CanadianEnglishGrammarAPI,
    APITimeoutError,
    APIServiceUnavailableError
)

class FRCA_GrammarSpecialist:
    def __init__(self, name: str = "FRCA_GrammarSpecialist_Default"):
        self.name = name
        print(f"Agent {self.name} initialized.") # Replace with log

    def review_grammar(self, task: TranslationTask, grammar_api: CanadianFrenchGrammarAPI) -> bool:
        is_revision = task.current_state == ws.FRCA_GRAMMAR_REVISION_PENDING
        step_details_str = "FRCA Grammar Review" + (" (Revision)" if is_revision else "")

        # Determine input text version: if revision, might be from translator again, else from initial translation
        current_text_version_key = 'initial_translation_frca' + ('_rev' if is_revision and task.text_versions.get('initial_translation_frca_rev') else '')
        if is_revision and not task.text_versions.get(current_text_version_key): # Fallback if specific _rev doesn't exist
            current_text_version_key = 'initial_translation_frca'
        current_text = task.text_versions.get(current_text_version_key)

        event_base_details: Dict[str, Any] = {"agent": self.name, "task_id": task.task_id, "processed_version": current_text_version_key, "is_revision": is_revision}
        print(f"Agent {self.name} (Task {task.task_id}): Processing {step_details_str} for '{current_text_version_key}'.") # Replace with log

        if not current_text:
            err_msg = f"Missing text version: {current_text_version_key} for {step_details_str}"
            event_details = {**event_base_details, "error": err_msg}
            task.update_state(ws.TASK_ON_HOLD, self.name, err_msg, event_details)
            task.add_feedback(self.name, "Error", err_msg)
            return False

        try:
            api_response = grammar_api.check_frca_grammar(current_text)
            task.reset_retry_count(self.name, step_details_str)
            event_base_details["api_response"] = api_response

            issues = api_response.get("issues_found", [])
            # If it's a revision, we might expect fewer or different issues. Simulate improvement.
            if is_revision and issues and random.random() < 0.75: # 75% chance issues are "fixed" by translator
                print(f"Agent {self.name} (Task {task.task_id}): Simulated improvement after translator's revision for grammar.") # Replace with log
                event_base_details["simulated_revision_improvement"] = True
                issues = [] # Clear issues

            task.add_feedback(
                self.name, "GrammarFRCA" + ("_RevisionAttempt" if is_revision else ""),
                f"API Score: {api_response.get('score', 'N/A')}, Issues found: {len(issues)}. Details: {issues}",
                "RevisionNeeded" if issues else "Proceed"
            )

            output_version_key = 'grammar_corrected_frca' + ('_rev' if is_revision and not issues else '')
            corrected_text = current_text + f" [FR Grammar {'OK' if not issues else 'IssuesFound'}{' (revised)' if is_revision else ''}]"
            task.add_text_version(output_version_key, corrected_text, self.name)

            action_summary = f"{step_details_str} completed"
            next_state = ws.FRCA_NUANCE_CONTEXT_REVIEW_PENDING
            if is_revision: # If this was a revision requested by Nuance expert, send it back to Nuance
                originating_feedback = next((fb for fb in reversed(task.qa_feedback) if fb.get("target_revision_stage") == task.current_state and fb.get("agent_role") == "FRCA_NuanceContextExpert_Default"), None)
                if originating_feedback: next_state = ws.FRCA_NUANCE_CONTEXT_REVIEW_PENDING
                # This routing could be more sophisticated based on who requested it.

            if issues: # If issues still exist (or new ones found)
                action_summary += " with issues."
                # Decide if it goes back for re-translation or to next step with issues flagged
                # For now, always proceed to Nuance, but could send to EN_FRCA_INITIAL_TRANSLATION_REVISION_PENDING
                task.update_state(next_state, self.name, action_summary, event_base_details)
            else:
                action_summary += " successfully."
                task.update_state(next_state, self.name, action_summary, event_base_details)
            return True

        except (APITimeoutError, APIServiceUnavailableError) as e:
            err_msg = f"API error during {step_details_str}: {type(e).__name__} - {str(e)}"
            event_details = {**event_base_details, "error": str(e), "error_type": type(e).__name__}
            task.update_state(ws.FRCA_GRAMMAR_API_ERROR_RETRY_PENDING, self.name, err_msg, event_details)
            return False
        except Exception as e:
            err_msg = f"Unexpected error during {step_details_str}: {type(e).__name__} - {str(e)}"
            event_details = {**event_base_details, "error": str(e), "error_type": type(e).__name__}
            task.update_state(ws.TASK_UNKNOWN_FAILURE, self.name, err_msg, event_details)
            return False

class ENCA_GrammarSpecialist: # Apply similar structured logging enhancements
    def __init__(self, name: str = "ENCA_GrammarSpecialist_Default"):
        self.name = name
        print(f"Agent {self.name} initialized.") # Replace with log

    def review_grammar(self, task: TranslationTask, grammar_api: CanadianEnglishGrammarAPI) -> bool:
        is_revision = task.current_state == ws.ENCA_GRAMMAR_REVISION_PENDING
        step_details_str = "ENCA Grammar Review" + (" (Revision)" if is_revision else "")

        current_text_version_key = 'initial_translation_enca' + ('_rev' if is_revision and task.text_versions.get('initial_translation_enca_rev') else '')
        if is_revision and not task.text_versions.get(current_text_version_key):
             current_text_version_key = 'initial_translation_enca'
        current_text = task.text_versions.get(current_text_version_key)

        event_base_details: Dict[str, Any] = {"agent": self.name, "task_id": task.task_id, "processed_version": current_text_version_key, "is_revision": is_revision}
        print(f"Agent {self.name} (Task {task.task_id}): Processing {step_details_str} for '{current_text_version_key}'.") # Replace with log

        if not current_text:
            err_msg = f"Missing text: {current_text_version_key}"
            event_details = {**event_base_details, "error": err_msg}
            task.update_state(ws.TASK_ON_HOLD, self.name, err_msg, event_details)
            return False

        try:
            api_response = grammar_api.check_enca_grammar(current_text)
            task.reset_retry_count(self.name, step_details_str)
            event_base_details["api_response"] = api_response
            issues = api_response.get("issues_found", [])
            if is_revision and issues and random.random() < 0.75:
                 event_base_details["simulated_revision_improvement"] = True; issues = []
                 print(f"Agent {self.name} (Task {task.task_id}): Simulated ENCA grammar improvement.") # Replace

            task.add_feedback(self.name, "GrammarENCA" + ("_RevisionAttempt" if is_revision else ""),
                f"API Score: {api_response.get('score', 'N/A')}, Issues: {len(issues)}. Details: {issues}",
                "RevisionNeeded" if issues else "Proceed")

            output_version_key = 'grammar_corrected_enca' + ('_rev' if is_revision and not issues else '')
            corrected_text = current_text + f" [EN Grammar {'OK' if not issues else 'IssuesFound'}{' (revised)' if is_revision else ''}]"
            task.add_text_version(output_version_key, corrected_text, self.name)

            next_state = ws.ENCA_NUANCE_CONTEXT_REVIEW_PENDING
            # Add logic for routing if it was a revision requested by a later stage
            action_summary = f"{step_details_str} completed"
            if issues: action_summary += " with issues."
            else: action_summary += " successfully."
            task.update_state(next_state, self.name, action_summary, event_base_details)
            return True

        except (APITimeoutError, APIServiceUnavailableError) as e:
            err_msg = f"API error in {step_details_str}: {type(e).__name__}"
            event_details = {**event_base_details, "error": str(e), "error_type": type(e).__name__}
            task.update_state(ws.ENCA_GRAMMAR_API_ERROR_RETRY_PENDING, self.name, err_msg, event_details)
            return False
        except Exception as e:
            err_msg = f"Unexpected error in {step_details_str}: {type(e).__name__}"
            event_details = {**event_base_details, "error": str(e), "error_type": type(e).__name__}
            task.update_state(ws.TASK_UNKNOWN_FAILURE, self.name, err_msg, event_details)
            return False
