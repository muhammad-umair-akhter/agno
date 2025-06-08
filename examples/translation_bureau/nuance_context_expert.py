from typing import Any, Dict, Optional
import random
from examples.translation_bureau.task_models import TranslationTask
import examples.translation_bureau.workflow_states as ws
from examples.translation_bureau.apis import NuanceContextAPI

class FRCA_NuanceContextExpert:
    def __init__(self, name: str = "FRCA_NuanceContextExpert_Default"):
        self.name = name
        print(f"Agent {self.name} initialized: French (Canada) Nuance and Context Expert.")

    def _identify_source_text_context(self, task: TranslationTask) -> str:
        """Simulates identifying the context of the source text."""
        text_lower = task.original_text.lower()
        if any(term in text_lower for term in ["hockey", "poutine", "eh?", "dépanneur", "toque", "chum", "ringuette", "skidoo"]):
            return "Identified context: Strong Canadian cultural references."
        elif any(term in text_lower for term in ["software", "system", "interface", "application", "framework", "database"]):
            return "Identified context: Technical/Software."
        elif any(term in text_lower for term in ["le client veut", "rapport doit être impeccable"]): # from fr_ca samples
            return "Identified context: Business/Formal."
        return "Identified context: General conversation."

    def assess_nuance_and_context(self, task: TranslationTask, api: NuanceContextAPI) -> bool:
        is_revision = task.current_state == ws.FRCA_NUANCE_REVISION_PENDING
        step_details_str = "FRCA Nuance/Context Review" + (" (Revision)" if is_revision else "")

        # **New: Context Identification**
        context_analysis_result = self._identify_source_text_context(task)
        # Storing context analysis as a text version for visibility in reports.
        # Could also be added to task.metadata or a dedicated field if preferred.
        task.add_text_version(version_name='source_context_analysis_frca',
                              text_content=context_analysis_result,
                              agent_name=self.name)
                              # Details for this specific add_text_version are now in the method in task_models.py
        print(f"Agent {self.name} (Task {task.task_id}): {context_analysis_result}") # Replace with log

        text_version_keys_to_try = [
            'terminology_corrected_frca', 'style_tone_corrected_frca',
            'nuance_corrected_frca',
            'grammar_corrected_frca'
        ] if is_revision else ['grammar_corrected_frca']

        current_text: Optional[str] = None
        processed_text_version_key: str = ""
        for key_to_try in text_version_keys_to_try:
            if task.text_versions.get(key_to_try):
                current_text = task.text_versions.get(key_to_try)
                processed_text_version_key = key_to_try
                break

        event_base_details: Dict[str, Any] = {
            "agent": self.name, "task_id": task.task_id,
            "processed_version": processed_text_version_key,
            "identified_source_context": context_analysis_result # Adding context to event details
        }

        if not current_text:
            err_msg = f"Suitable text version not found for {step_details_str}. Looked for {text_version_keys_to_try}."
            print(f"Error: {err_msg}")
            event_details = {**event_base_details, "error": err_msg, "looked_for_versions": text_version_keys_to_try}
            task.update_state(ws.TASK_ON_HOLD, agent_name=self.name, action_details=err_msg, event_details=event_details)
            task.add_feedback(agent_role=self.name, feedback_type="Error", comments=err_msg)
            return False

        print(f"Agent {self.name} (Task {task.task_id}): Processing {step_details_str} for text version '{processed_text_version_key}'.")

        api_response = api.analyze_nuance(current_text, f"{task.source_language}_{task.target_language}")
        appropriateness_score = api_response.get('appropriateness_score', 0)
        event_base_details["api_response"] = api_response

        issues_found = appropriateness_score < 0.7
        if is_revision and issues_found and random.random() < 0.75:
            print(f"Agent {self.name} (Task {task.task_id}): Simulated successful revision for nuance. Score improved.")
            issues_found = False
            appropriateness_score = max(appropriateness_score, 0.8)
            event_base_details["simulated_revision_fix"] = True
            event_base_details["new_appropriateness_score"] = appropriateness_score

        task.add_feedback(
            agent_role=self.name,
            feedback_type="NuanceFRCA" + ("_RevisionAttempt" if is_revision else ""),
            comments=f"API Appropriateness Score: {appropriateness_score}. Issues found: {issues_found}. Source Context: {context_analysis_result}",
            requested_action="Proceed" if not issues_found else "FurtherRevisionNeeded"
        )

        output_version_name = 'nuance_corrected_frca' + ('_rev' if is_revision and not issues_found else '')
        refined_text = current_text
        if not issues_found:
            refined_text += f" [FR-CA Nuance OK{' (revised)' if is_revision else ''}]"
        else:
            refined_text += f" [FR-CA Nuance Needs Review - Score: {appropriateness_score}{' (revised attempt)' if is_revision else ''}]"

        task.add_text_version(version_name=output_version_name, text_content=refined_text, agent_name=self.name)

        next_state_if_ok = ws.FRCA_STYLE_TONE_REVIEW_PENDING
        if is_revision:
            originating_feedback = next((fb for fb in reversed(task.qa_feedback)
                                         if fb.get("target_revision_stage") == task.current_state and
                                            fb.get("requested_action", "").startswith("RevisionTo:")), None)
            if originating_feedback and originating_feedback.get("agent_role", "").startswith("FinalQualityGate"):
                 next_state_if_ok = ws.FRCA_FINAL_REVIEW_PENDING
                 event_base_details["routing_decision"] = f"Returning to Final Reviewer ({originating_feedback.get('agent_role')}) after nuance revision."
            else:
                 event_base_details["routing_decision"] = "Proceeding to Style/Tone after nuance revision (not from Final Reviewer, or no specific feedback found)."

        action_summary = f"{step_details_str} completed"
        if issues_found:
            action_summary += " with issues."
            task.update_state(next_state_if_ok, agent_name=self.name, action_details=action_summary, event_details=event_base_details)
        else:
            action_summary += " successfully."
            if not is_revision: task.reset_retry_count(self.name, step_details_str)
            task.update_state(new_state=next_state_if_ok, agent_name=self.name, action_details=action_summary, event_details=event_base_details)
        return True

class ENCA_NuanceContextExpert:
    def __init__(self, name: str = "ENCA_NuanceContextExpert_Default"):
        self.name = name
        print(f"Agent {self.name} initialized: English (Canada) Nuance and Context Expert.")

    def _identify_source_text_context(self, task: TranslationTask) -> str: # Added for ENCA path too
        """Simulates identifying the context of the source text."""
        text_lower = task.original_text.lower() # Should be task.original_text
        if any(term in text_lower for term in ["hockey", "poutine", "eh?", "dépanneur", "toque", "chum", "ringuette", "skidoo", "glorieux"]):
            return "Identified context: Strong Canadian cultural references."
        elif any(term in text_lower for term in ["software", "system", "interface", "application", "framework", "database", "logiciel"]):
            return "Identified context: Technical/Software."
        elif any(term in text_lower for term in ["le client veut", "rapport doit être impeccable"]):
            return "Identified context: Business/Formal."
        return "Identified context: General conversation."

    def assess_nuance_and_context(self, task: TranslationTask, api: NuanceContextAPI) -> bool:
        is_revision = task.current_state == ws.ENCA_NUANCE_REVISION_PENDING
        step_details_str = "ENCA Nuance/Context Review" + (" (Revision)" if is_revision else "")

        context_analysis_result = self._identify_source_text_context(task)
        task.add_text_version(version_name='source_context_analysis_enca', text_content=context_analysis_result, agent_name=self.name)
        print(f"Agent {self.name} (Task {task.task_id}): {context_analysis_result}") # Replace with log

        text_version_keys_to_try = ['terminology_corrected_enca', 'style_tone_corrected_enca', 'nuance_corrected_enca', 'grammar_corrected_enca'] if is_revision else ['grammar_corrected_enca']
        current_text: Optional[str] = None
        processed_text_version_key: str = ""
        for key_to_try in text_version_keys_to_try:
            if task.text_versions.get(key_to_try):
                current_text = task.text_versions.get(key_to_try); processed_text_version_key = key_to_try; break

        event_base_details: Dict[str, Any] = {"agent": self.name, "task_id": task.task_id, "processed_version": processed_text_version_key, "identified_source_context": context_analysis_result}

        if not current_text:
            err_msg = f"Suitable text version not found for {step_details_str}. Looked for {text_version_keys_to_try}."
            print(f"Error: {err_msg}")
            event_details = {**event_base_details, "error": err_msg, "looked_for_versions": text_version_keys_to_try}
            task.update_state(ws.TASK_ON_HOLD, agent_name=self.name, action_details=err_msg, event_details=event_details)
            return False

        print(f"Agent {self.name} (Task {task.task_id}): Processing {step_details_str} for '{processed_text_version_key}'.")
        api_response = api.analyze_nuance(current_text, f"{task.source_language}_{task.target_language}")
        appropriateness_score = api_response.get('appropriateness_score', 0)
        event_base_details["api_response"] = api_response

        issues_found = appropriateness_score < 0.7
        if is_revision and issues_found and random.random() < 0.75:
            issues_found = False; appropriateness_score = max(appropriateness_score, 0.8)
            event_base_details["simulated_revision_fix"] = True; event_base_details["new_appropriateness_score"] = appropriateness_score
            print(f"Agent {self.name} (Task {task.task_id}): Simulated successful ENCA nuance revision.")

        task.add_feedback(self.name, "NuanceENCA" + ("_RevisionAttempt" if is_revision else ""),
                          f"Score: {appropriateness_score}. Issues: {issues_found}. Source Context: {context_analysis_result}")

        output_version_name = 'nuance_corrected_enca' + ('_rev' if is_revision and not issues_found else '')
        refined_text = current_text + f" [EN-CA Nuance OK{' (revised)' if is_revision and not issues_found else ''}]"
        task.add_text_version(output_version_name, refined_text, self.name)

        next_state_if_ok = ws.ENCA_STYLE_TONE_REVIEW_PENDING
        if is_revision:
            originating_feedback = next((fb for fb in reversed(task.qa_feedback) if fb.get("target_revision_stage") == task.current_state and fb.get("requested_action","").startswith("RevisionTo:")), None)
            if originating_feedback and originating_feedback.get("agent_role", "").startswith("FinalQualityGate"):
                 next_state_if_ok = ws.ENCA_FINAL_REVIEW_PENDING
                 event_base_details["routing_decision"] = f"Returning to Final Reviewer after nuance revision for {originating_feedback.get('agent_role')}"

        action_summary = f"{step_details_str} completed"
        if issues_found:
            action_summary += " with issues."
            task.update_state(next_state_if_ok, agent_name=self.name, action_details=action_summary, event_details=event_base_details)
        else:
            action_summary += " successfully."
            if not is_revision: task.reset_retry_count(self.name, step_details_str)
            task.update_state(next_state_if_ok, agent_name=self.name, action_details=action_summary, event_details=event_base_details)
        return True
