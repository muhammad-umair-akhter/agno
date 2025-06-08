from typing import Any, Dict, Optional
import random
from examples.translation_bureau.task_models import TranslationTask
import examples.translation_bureau.workflow_states as ws
from examples.translation_bureau.apis import StyleToneAPI

class FRCA_StyleToneEditor:
    def __init__(self, name: str = "FRCA_StyleToneEditor_Default"):
        self.name = name
        print(f"Agent {self.name} initialized.")

    def edit_for_style_and_tone(self, task: TranslationTask, api: StyleToneAPI) -> bool:
        is_revision = task.current_state == ws.FRCA_STYLE_REVISION_PENDING
        step_details_str = "FRCA Style/Tone Edit" + (" (Revision)" if is_revision else "")

        # Determine input text: if revising, use the text version that Final Reviewer assessed,
        # which should be 'terminology_corrected_frca'. Otherwise, use 'nuance_corrected_frca'.
        # More robustly find the latest relevant version.
        text_version_keys_to_try = []
        if is_revision:
            # If Final Review sent it back, it would have reviewed 'terminology_corrected_frca' or its '..._rev' variant.
            # Style editor should work on what Final Reviewer saw.
            text_version_keys_to_try.extend(['terminology_corrected_frca_rev', 'terminology_corrected_frca'])
        text_version_keys_to_try.extend(['nuance_corrected_frca_rev', 'nuance_corrected_frca']) # Standard input if not revision from final

        current_text: Optional[str] = None
        processed_text_version_key: str = ""
        for key_to_try in text_version_keys_to_try:
            if task.text_versions.get(key_to_try):
                current_text = task.text_versions.get(key_to_try); processed_text_version_key = key_to_try; break

        # **Accessing Source Context Analysis**
        source_context = task.text_versions.get('source_context_analysis_frca', "Context: Unknown")
        event_base_details: Dict[str, Any] = {
            "agent": self.name, "task_id": task.task_id,
            "processed_version": processed_text_version_key, "is_revision": is_revision,
            "identified_source_context": source_context
        }
        print(f"Agent {self.name} (Task {task.task_id}): Processing {step_details_str} for '{processed_text_version_key}'. Source Context: {source_context}")

        if not current_text:
            err_msg = f"Missing text version for {step_details_str}"
            event_details = {**event_base_details, "error": err_msg, "looked_for_versions": text_version_keys_to_try}
            task.update_state(ws.TASK_ON_HOLD, self.name, err_msg, event_details); return False

        target_style = task.metadata.get("target_style", "neutral_formal")
        # Conceptually adjust target_style based on source_context if needed
        if "Technical/Software" in source_context and target_style == "neutral_informal":
            target_style = "neutral_formal" # Force formal for technical
            print(f"Agent {self.name} (Task {task.task_id}): Adjusted target style to '{target_style}' due to technical context.")
        event_base_details["target_style"] = target_style

        api_response = api.analyze_style_tone(current_text, task.target_language, expected_tone=target_style)
        event_base_details["api_response"] = api_response
        tone_match_score = api_response.get('tone_match_score', 0)

        # Simulate stricter check or specific adjustments if context demands it
        issues_found = tone_match_score < 0.75
        if "Technical/Software" in source_context and "buddy" in current_text.lower(): # "buddy" was from StyleToneAPI example
            issues_found = True
            event_base_details["contextual_style_flag"] = "Informal term 'buddy' clashed with technical context."
            tone_match_score = min(tone_match_score, 0.6) # Penalize further

        if is_revision and issues_found and random.random() < 0.8:
             print(f"Agent {self.name} (Task {task.task_id}): Simulated successful style/tone revision.")
             issues_found = False; tone_match_score = max(tone_match_score, 0.85)
             event_base_details["simulated_revision_fix"] = True; event_base_details["new_tone_match_score"] = tone_match_score

        feedback_comment = f"API Tone Match Score (for '{target_style}' given '{source_context}'): {tone_match_score}. Issues: {issues_found}."
        if event_base_details.get("contextual_style_flag"):
            feedback_comment += f" Contextual flag: {event_base_details['contextual_style_flag']}"
        task.add_feedback(self.name, "StyleToneFRCA" + ("_RevisionAttempt" if is_revision else ""), feedback_comment,
            "Proceed" if not issues_found else "FurtherRevisionNeeded")

        output_version_key = 'style_tone_corrected_frca' + ('_rev' if is_revision and not issues_found else '')
        edited_text = current_text + f" [FR-CA Style '{target_style}' {'OK' if not issues_found else 'NeedsImprovement'}{' (revised)' if is_revision else ''}]"
        task.add_text_version(output_version_key, edited_text, self.name)

        next_state = ws.FRCA_TERMINOLOGY_REVIEW_PENDING
        action_details = f"{step_details_str} completed"
        if is_revision:
            originating_feedback = next((fb for fb in reversed(task.qa_feedback) if fb.get("target_revision_stage") == task.current_state and fb.get("agent_role","").startswith("FinalQualityGate")), None)
            if originating_feedback:
                next_state = ws.FRCA_FINAL_REVIEW_PENDING
                event_base_details["routing_decision"] = f"Returning to Final Reviewer ({originating_feedback.get('agent_role')}) after style revision."
                action_details += f" (routing back to {originating_feedback.get('agent_role')})"


        if issues_found: action_summary = action_details + " with issues." # Use action_details which may contain routing info
        else: action_summary = action_details + " successfully."
        task.update_state(next_state, self.name, action_summary, event_base_details)
        return True

class ENCA_StyleToneEditor:
    def __init__(self, name: str = "ENCA_StyleToneEditor_Default"):
        self.name = name
        print(f"Agent {self.name} initialized.")

    def edit_for_style_and_tone(self, task: TranslationTask, api: StyleToneAPI) -> bool:
        is_revision = task.current_state == ws.ENCA_STYLE_REVISION_PENDING
        step_details_str = "ENCA Style/Tone Edit" + (" (Revision)" if is_revision else "")

        text_version_keys_to_try = ['nuance_corrected_enca_rev', 'nuance_corrected_enca'] if is_revision else ['nuance_corrected_enca']
        if is_revision and not task.text_versions.get(text_version_keys_to_try[0]):
             text_version_keys_to_try = ['terminology_corrected_enca', 'style_tone_corrected_enca', 'nuance_corrected_enca', 'grammar_corrected_enca']

        current_text: Optional[str] = None; processed_text_version_key: str = ""
        for key_to_try in text_version_keys_to_try:
            if task.text_versions.get(key_to_try):
                current_text = task.text_versions.get(key_to_try); processed_text_version_key = key_to_try; break

        source_context = task.text_versions.get('source_context_analysis_enca', "Context: Unknown") # Access ENCA context
        event_base_details: Dict[str, Any] = {"agent": self.name, "task_id": task.task_id, "processed_version": processed_text_version_key, "is_revision": is_revision, "identified_source_context": source_context}
        print(f"Agent {self.name} (Task {task.task_id}): Processing {step_details_str} for '{processed_text_version_key}'. Source Context: {source_context}")

        if not current_text:
            err_msg = f"Missing text for {step_details_str}"; event_details = {**event_base_details, "error": err_msg, "looked_for_versions": text_version_keys_to_try}
            task.update_state(ws.TASK_ON_HOLD, self.name, err_msg, event_details); return False

        target_style = task.metadata.get("target_style", "neutral_formal")
        event_base_details["target_style"] = target_style
        api_response = api.analyze_style_tone(current_text, task.target_language, expected_tone=target_style)
        event_base_details["api_response"] = api_response
        tone_match_score = api_response.get('tone_match_score', 0)

        issues_found = tone_match_score < 0.75
        if "Technical/Software" in source_context and "super informal term" in current_text.lower(): # Example
            issues_found = True
            event_base_details["contextual_style_flag"] = "Informal term clashed with technical context for ENCA."
            tone_match_score = min(tone_match_score, 0.6)

        if is_revision and issues_found and random.random() < 0.8:
             issues_found = False; tone_match_score = max(tone_match_score, 0.85)
             event_base_details["simulated_revision_fix"] = True; event_base_details["new_tone_match_score"] = tone_match_score
             print(f"Agent {self.name} (Task {task.task_id}): Simulated ENCA style/tone revision fix.")

        feedback_comment = f"API Tone Match Score (for '{target_style}' given '{source_context}'): {tone_match_score}. Issues: {issues_found}."
        if event_base_details.get("contextual_style_flag"):
            feedback_comment += f" Contextual flag: {event_base_details['contextual_style_flag']}"

        task.add_feedback(self.name, "StyleToneENCA" + ("_RevisionAttempt" if is_revision else ""), feedback_comment,
            "Proceed" if not issues_found else "FurtherRevisionNeeded")

        output_version_key = 'style_tone_corrected_enca' + ('_rev' if is_revision and not issues_found else '')
        edited_text = current_text + f" [EN-CA Style '{target_style}' {'OK' if not issues_found else 'NeedsImprovement'}{' (revised)' if is_revision else ''}]"
        task.add_text_version(output_version_key, edited_text, self.name)

        next_state = ws.ENCA_TERMINOLOGY_REVIEW_PENDING
        action_details = f"{step_details_str} completed"
        if is_revision:
            originating_feedback = next((fb for fb in reversed(task.qa_feedback) if fb.get("target_revision_stage") == task.current_state and fb.get("agent_role","").startswith("FinalQualityGate")), None)
            if originating_feedback:
                next_state = ws.ENCA_FINAL_REVIEW_PENDING
                event_base_details["routing_decision"] = f"Returning to Final Reviewer ({originating_feedback.get('agent_role')}) after style revision."
                action_details += f" (routing back to {originating_feedback.get('agent_role')})"

        if issues_found: action_summary = action_details + " with issues."
        else: action_summary = action_details + " successfully."
        task.update_state(next_state, self.name, action_summary, event_base_details)
        return True
