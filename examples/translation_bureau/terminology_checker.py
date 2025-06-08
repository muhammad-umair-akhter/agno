from typing import Any, Dict, List, Optional # Added List
# Import necessary models, states, and APIs
from examples.translation_bureau.task_models import TranslationTask
import examples.translation_bureau.workflow_states as ws
from examples.translation_bureau.apis import (
    TerminologyDatabaseAPI,
    APITimeoutError,
    APIServiceUnavailableError,
    APIResourceNotFoundError
)

class TerminologyConsistencyChecker:
    def __init__(self, name: str = "TerminologyChecker_Default"):
        self.name = name
        print(f"Agent {self.name} initialized.")

    def check_terminology(self, task: TranslationTask, api: TerminologyDatabaseAPI) -> bool:
        step_details_str = f"{task.target_language} Terminology Review"
        # Determine input text version key: try revised style/tone corrected, then original style/tone corrected
        current_text_version_key_base = 'style_tone_corrected_'
        rev_suffix = '_rev'

        target_lang_suffix = task.target_language.lower().replace("_", "") # frca or enca

        # Try to get the revised version first, then the original
        possible_input_keys = [
            current_text_version_key_base + target_lang_suffix + rev_suffix, # e.g. style_tone_corrected_frca_rev
            current_text_version_key_base + target_lang_suffix # e.g. style_tone_corrected_frca
        ]

        current_text: Optional[str] = None
        processed_text_version_key: str = ""
        for key_to_try in possible_input_keys:
            if task.text_versions.get(key_to_try):
                current_text = task.text_versions.get(key_to_try)
                processed_text_version_key = key_to_try
                break

        event_base_details: Dict[str, Any] = {"agent": self.name, "task_id": task.task_id, "processed_version": processed_text_version_key}
        # print(f"Agent {self.name} (Task {task.task_id}): Processing {step_details_str} for '{processed_text_version_key}'.")

        if not current_text:
            err_msg = f"Missing suitable text version for {step_details_str}. Looked for {possible_input_keys}"
            event_details = {**event_base_details, "error": err_msg}
            task.update_state(ws.TASK_ON_HOLD, self.name, err_msg, event_details); return False

        project_id = task.metadata.get('project_code', 'unknown_proj')
        event_base_details["project_id"] = project_id

        next_state_if_ok = ""
        feedback_type = ""
        output_version_key = f'terminology_corrected_{target_lang_suffix}'
        current_retry_state = ""

        if task.target_language == "FR_CA":
            next_state_if_ok = ws.FRCA_FINAL_REVIEW_PENDING
            feedback_type = "TerminologyFRCA"
            current_retry_state = ws.FRCA_TERMINOLOGY_API_ERROR_RETRY_PENDING
        elif task.target_language == "EN_CA":
            next_state_if_ok = ws.ENCA_FINAL_REVIEW_PENDING
            feedback_type = "TerminologyENCA"
            current_retry_state = ws.ENCA_TERMINOLOGY_API_ERROR_RETRY_PENDING
        # No else needed here due to check at the start of the main.py loop for lang pair support.

        try:
            api_response = api.verify_terms(current_text, task.target_language, project_id, task.task_id)
            task.reset_retry_count(self.name, step_details_str)
            event_base_details["api_response"] = api_response

            api_issues: List[Dict[str, Any]] = api_response.get("issues_found", [])
            # Filter out "ok_acknowledged" universal names from being "issues" for terms_ok logic
            critical_issues = [iss for iss in api_issues if iss.get("severity") == "high" or iss.get("type") == "untranslated_term"]
            terms_ok = not critical_issues # Only critical issues make terms_ok False

            feedback_comments = f"Terms OK: {terms_ok}. Issues found: {len(api_issues)} (Critical: {len(critical_issues)}). Details: {api_issues}"
            task.add_feedback(
                self.name, feedback_type,
                feedback_comments,
                "RevisionNeeded" if not terms_ok else "Proceed"
            )

            checked_text = current_text + (f" [TermsOK {task.target_language}]" if terms_ok else f" [TermsIssue {task.target_language} - {len(critical_issues)} critical]")
            # If a revision happened at style/tone, the current key might be "..._rev". We want to create a new "terminology_corrected_..." without double _rev.
            task.add_text_version(output_version_key, checked_text, self.name)

            action_summary = f"{step_details_str} completed"
            if not terms_ok:
                action_summary += " with critical issues flagged."
            else: action_summary += " successfully."

            task.update_state(next_state_if_ok, self.name, action_summary, event_base_details)
            return True

        except (APITimeoutError, APIServiceUnavailableError, APIResourceNotFoundError) as e:
            err_msg = f"API error in {step_details_str}: {type(e).__name__} - {str(e)}"
            event_details = {**event_base_details, "error": str(e), "error_type": type(e).__name__}
            task.update_state(current_retry_state, self.name, err_msg, event_details)
            return False
        except Exception as e:
            err_msg = f"Unexpected error in {step_details_str}: {type(e).__name__} - {str(e)}"
            event_details = {**event_base_details, "error": str(e), "error_type": type(e).__name__}
            task.update_state(ws.TASK_UNKNOWN_FAILURE, self.name, err_msg, event_details)
            return False
