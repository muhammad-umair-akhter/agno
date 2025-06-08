from typing import Any, List, Tuple, Optional, Dict
import random
from examples.translation_bureau.task_models import TranslationTask
import examples.translation_bureau.workflow_states as ws

MAX_REVISIONS_PER_STAGE_BY_FINAL_REVIEW = 1

class FinalQualityGate_FRCA:
    def __init__(self, name: str = "FinalQualityGate_FRCA_Default", revision_request_rate: float = 0.35): # Increased rate for testing
        self.name = name
        self.revision_request_rate = revision_request_rate
        print(f"Agent {self.name} initialized: Final Quality Gate for FR-CA. Revision rate: {self.revision_request_rate}")

    def _check_for_unresolved_major_qa_issues(self, task: TranslationTask) -> Optional[str]:
        """
        Simulates checking if significant prior QA issues remain unresolved.
        Returns a comment string if issues found, else None.
        """
        # Example: Look for critical feedback from earlier stages that hasn't been addressed.
        # This is a simplified check. A real system might look for specific tags or severity.
        for feedback in task.qa_feedback:
            # Check feedback from agents other than self
            if feedback.get("agent_role") != self.name:
                # Check for feedback indicating issues that should have been resolved by now
                # For example, if grammar checker flagged something critical and it's still apparently there.
                # This mock will use a placeholder check.
                if "critical_grammar_issue_unresolved_placeholder" in task.text_versions.get('terminology_corrected_frca',''): # Check latest text
                    return f"Unresolved critical grammar issue: {feedback.get('comments')}"
                if feedback.get("feedback_type") == "TerminologyFRCA" and "TermsIssue" in task.text_versions.get('terminology_corrected_frca',''):
                     # Check if the TerminologyChecker flagged an issue that is still present in the text version it produced.
                     # The text_version includes "[TermsIssue FR_CA]" if problems were found by TerminologyChecker
                    if "[TermsIssue FR_CA]" in task.text_versions.get('terminology_corrected_frca',''):
                        return f"Terminology issues previously flagged by {feedback.get('agent_role')} seem unresolved. Feedback: {feedback.get('comments')}"
        return None

    def _check_contextual_cohesion(self, task: TranslationTask, current_text: str) -> Optional[str]:
        """
        Simulates checking for contextual cohesion based on source context analysis.
        Returns a comment string if issues found, else None.
        """
        source_context = task.text_versions.get('source_context_analysis_frca', "Context: Unknown")

        # Example heuristic:
        if "Technical/Software" in source_context:
            # Look for overly informal language in the translated text (very simplified)
            informal_terms = ["trop cool", "genre", "super le fun"] # "le fun" is already an anglicism
            for term in informal_terms:
                if term in current_text.lower():
                    return f"Cohesion issue: Text has technical source context ('{source_context}') but contains informal phrase: '{term}'."

        if "Strong Canadian cultural references" in source_context:
            # Example: if a very formal, non-Canadian term was used for something typically Canadian.
            if "bagnole" in current_text.lower() and "char" not in current_text.lower(): # bagnole = very informal France French for car
                 return f"Cohesion issue: Strong Canadian context, but 'bagnole' used instead of more typical 'char' or 'auto'."
        return None

    def perform_final_review(self, task: TranslationTask) -> bool:
        step_details_str = "FRCA Final Review"
        print(f"Agent {self.name} (Task {task.task_id}): Processing {step_details_str} for 'terminology_corrected_frca'.")

        current_text_version_key = 'terminology_corrected_frca' # This agent always reviews the output of terminology check
        current_text = task.text_versions.get(current_text_version_key)

        event_base_details: Dict[str, Any] = {"agent": self.name, "task_id": task.task_id, "processed_version": current_text_version_key}

        if not current_text:
            err_msg = f"Missing text version: {current_text_version_key} for {step_details_str}"
            print(f"Error: {err_msg}")
            task.update_state(ws.TASK_ON_HOLD, agent_name=self.name, action_details=err_msg, event_details={"error": err_msg, **event_base_details})
            task.add_feedback(agent_role=self.name, feedback_type="Error", comments=err_msg)
            return False

        checklist: List[str] = task.metadata.get('final_checklist_frca', ["completeness", "accuracy", "formatting", "nuance_check", "style_guide", "cohesion_context"])
        event_base_details["checklist_used"] = checklist
        approved = True
        issues_found_comments: List[str] = []
        revision_target_state: Optional[str] = None
        revision_stage_key: str = ""

        # 1. Basic Formatting/Completeness (example from before)
        if "formatting" in checklist and "[FR Style/Tone Checked]" not in current_text and "[FR Terminology Checked]" not in current_text : # If a prior marker is missing
            approved = False; issue_comment = "Failed formatting/completeness: Expected markers from Style or Terminology stages are missing."
            issues_found_comments.append(issue_comment); event_base_details.setdefault("findings", []).append({"check": "formatting", "outcome": "failed", "comment": issue_comment})
            if not revision_target_state: revision_target_state = ws.FRCA_STYLE_REVISION_PENDING; revision_stage_key = "frca_style_by_final"

        # 2. Check for unresolved prior QA issues (simulated)
        if approved and "accuracy" in checklist: # Using "accuracy" to gate this conceptual check
            unresolved_issue_comment = self._check_for_unresolved_major_qa_issues(task)
            if unresolved_issue_comment:
                approved = False; issues_found_comments.append(unresolved_issue_comment)
                event_base_details.setdefault("findings", []).append({"check": "unresolved_qa", "outcome": "failed", "comment": unresolved_issue_comment})
                # Decide where to send it back - could be complex. For now, maybe style or nuance.
                if not revision_target_state: revision_target_state = ws.FRCA_STYLE_REVISION_PENDING; revision_stage_key = "frca_style_by_final"

        # 3. Check for Cohesion and Contextual Accuracy (simulated)
        if approved and "cohesion_context" in checklist:
            cohesion_issue_comment = self._check_contextual_cohesion(task, current_text)
            if cohesion_issue_comment:
                approved = False; issues_found_comments.append(cohesion_issue_comment)
                event_base_details.setdefault("findings", []).append({"check": "cohesion_context", "outcome": "failed", "comment": cohesion_issue_comment})
                if not revision_target_state: revision_target_state = ws.FRCA_NUANCE_REVISION_PENDING; revision_stage_key = "frca_nuance_by_final"

        # 4. Generic random chance for other issues leading to revision (as before)
        if approved and "nuance_check" in checklist and random.random() < self.revision_request_rate : # Generic overall quality check
            # Only trigger this if no specific issues were found above, to simulate a "gut feeling" or minor missed point
            if task.get_revision_count('frca_overall_quality_by_final') < MAX_REVISIONS_PER_STAGE_BY_FINAL_REVIEW:
                approved = False; issue_comment = "Simulated: Final reviewer found a subtle overall quality concern (e.g. flow, nuance)."
                issues_found_comments.append(issue_comment)
                event_base_details.setdefault("findings", []).append({"check": "overall_quality", "outcome": "failed_revision_requested", "comment": issue_comment})
                if not revision_target_state: # Default to nuance if no other target picked
                    revision_target_state = ws.FRCA_NUANCE_REVISION_PENDING
                    revision_stage_key = "frca_overall_quality_by_final" # Use a distinct key for this type of revision
                print(f"Agent {self.name} (Task {task.task_id}): SIMULATING revision request for overall quality/nuance.")
            else:
                issue_comment = "Overall quality/nuance concern, but max revisions for this category by final reviewer reached."
                issues_found_comments.append(issue_comment + " (Marking as fail instead of revision)")
                event_base_details.setdefault("findings", []).append({"check": "overall_quality", "outcome": "failed_max_revisions", "comment": issue_comment})
                approved = False
                if not revision_target_state: revision_target_state = None

        task.add_feedback(
            self.name, "FinalReviewFRCA",
            f"Final review. Approved: {approved}. Issues: {'; '.join(issues_found_comments) if issues_found_comments else 'None'}",
            "Finalized" if approved else (f"RevisionTo:{revision_target_state}" if revision_target_state else "FailedHard"),
            target_revision_stage=revision_target_state if not approved and revision_target_state else None
        )

        action_summary = f"{step_details_str} "
        if approved:
            task.add_text_version('final_approved_frca', current_text, self.name)
            task.update_state(ws.TASK_COMPLETED_FRCA, self.name, action_summary + "PASSED.", event_base_details)
        else:
            if revision_target_state and revision_stage_key:
                # Check if this specific revision_stage_key has exceeded max revisions
                # The increment for THIS attempt at revision for THIS stage_key should happen here
                # The check in main.py is for the *next* attempt if it comes back to this state.
                current_rev_count_for_stage = task.increment_revision_count(revision_stage_key, agent_name=self.name)
                if current_rev_count_for_stage > MAX_REVISIONS_PER_STAGE_BY_FINAL_REVIEW: # Check if this attempt makes it exceed
                    action_summary += f"FAILED. Max revisions ({MAX_REVISIONS_PER_STAGE_BY_FINAL_REVIEW}) for stage '{revision_stage_key}' exceeded."
                    event_base_details["max_revisions_exceeded_for_stage"] = revision_stage_key
                    task.update_state(ws.TASK_MAX_REVISIONS_EXCEEDED_FAILURE, self.name, action_summary, event_base_details)
                    # PM flag will be called by main loop for TASK_MAX_REVISIONS_EXCEEDED_FAILURE
                else:
                    task.metadata["last_revision_request_key"] = revision_stage_key
                    action_summary += f"FAILED, sending for revision to {revision_target_state} (Attempt {current_rev_count_for_stage} for {revision_stage_key})."
                    event_base_details["revision_target_state"] = revision_target_state
                    event_base_details["revision_stage_key"] = revision_stage_key
                    task.update_state(revision_target_state, self.name, action_summary, event_base_details)
            else:
                action_summary += "FAILED. No clear revision path or specific issue maxed out revisions."
                task.update_state(ws.TASK_FAILED_FINAL_REVIEW, self.name, action_summary, event_base_details)
        return approved

class FinalQualityGate_ENCA: # (Apply similar, more detailed review logic)
    def __init__(self, name: str = "FinalQualityGate_ENCA_Default", revision_request_rate: float = 0.25):
        self.name = name
        self.revision_request_rate = revision_request_rate
        print(f"Agent {self.name} initialized: Final Quality Gate for EN-CA. Revision rate: {self.revision_request_rate}")

    def _identify_source_text_context(self, task: TranslationTask) -> str: # Helper for ENCA
        text_lower = task.original_text.lower()
        if any(term in text_lower for term in ["hockey", "poutine", "eh?", "dépanneur", "toque", "chum", "ringuette", "skidoo", "glorieux"]):
            return "Identified context: Strong Canadian cultural references."
        elif any(term in text_lower for term in ["software", "system", "interface", "application", "framework", "database", "logiciel"]):
            return "Identified context: Technical/Software."
        elif any(term in text_lower for term in ["le client veut", "rapport doit être impeccable"]):
            return "Identified context: Business/Formal."
        return "Identified context: General conversation."

    def perform_final_review(self, task: TranslationTask) -> bool:
        step_details_str = "ENCA Final Review"
        print(f"Agent {self.name} (Task {task.task_id}): Processing {step_details_str} for 'terminology_corrected_enca'.")
        current_text_version_key = 'terminology_corrected_enca'
        current_text = task.text_versions.get(current_text_version_key)
        source_context = self._identify_source_text_context(task) # Get source context

        event_base_details: Dict[str, Any] = {"agent": self.name, "task_id": task.task_id, "processed_version": current_text_version_key, "source_context": source_context}

        if not current_text:
            err_msg = f"Missing text: {current_text_version_key} for {step_details_str}"
            task.update_state(ws.TASK_ON_HOLD, self.name, err_msg, {"error": err_msg, **event_base_details}); return False

        checklist: List[str] = task.metadata.get('final_checklist_enca', ["consistency", "readability", "style_check", "cohesion_context"])
        approved = True; issues_found_comments: List[str] = []; revision_target_state: Optional[str] = None; revision_stage_key: str = ""
        event_base_details["checklist_used"] = checklist

        # Simplified cohesion check for ENCA
        if "cohesion_context" in checklist and "Technical/Software" in source_context and "super chill" in current_text.lower():
            approved = False; issue_comment = "Cohesion: Technical source, but text sounds too informal ('super chill')."
            issues_found_comments.append(issue_comment); event_base_details.setdefault("findings", []).append({"check": "cohesion_context", "outcome": "failed", "comment": issue_comment})
            if not revision_target_state: revision_target_state = ws.ENCA_STYLE_REVISION_PENDING; revision_stage_key = "enca_style_by_final"

        if approved and "style_check" in checklist and random.random() < self.revision_request_rate:
            if task.get_revision_count('enca_overall_quality_by_final') < MAX_REVISIONS_PER_STAGE_BY_FINAL_REVIEW:
                approved = False; issue_comment = "Simulated: Final reviewer found a subtle style/flow issue."
                issues_found_comments.append(issue_comment); event_base_details.setdefault("findings", []).append({"check": "overall_quality", "outcome": "failed_revision_requested", "comment": issue_comment})
                if not revision_target_state: revision_target_state = ws.ENCA_STYLE_REVISION_PENDING; revision_stage_key = "enca_overall_quality_by_final"
            else:
                approved = False; issues_found_comments.append("Overall style/flow concern, but max revisions reached.")
                if not revision_target_state: revision_target_state = None


        task.add_feedback(self.name, "FinalReviewENCA", f"Approved: {approved}. Issues: {'; '.join(issues_found_comments) if issues_found_comments else 'None'}",
            "Finalized" if approved else (f"RevisionTo:{revision_target_state}" if revision_target_state else "FailedHard"),
            target_revision_stage=revision_target_state if not approved and revision_target_state else None)

        action_summary = f"{step_details_str} "
        if approved:
            task.add_text_version('final_approved_enca', current_text, self.name)
            task.update_state(ws.TASK_COMPLETED_ENCA, self.name, action_summary + "PASSED.", event_base_details)
        else:
            if revision_target_state and revision_stage_key:
                current_rev_count_for_stage = task.increment_revision_count(revision_stage_key, agent_name=self.name)
                if current_rev_count_for_stage > MAX_REVISIONS_PER_STAGE_BY_FINAL_REVIEW:
                    action_summary += f"FAILED. Max revisions ({MAX_REVISIONS_PER_STAGE_BY_FINAL_REVIEW}) for stage '{revision_stage_key}' exceeded."
                    event_base_details["max_revisions_exceeded_for_stage"] = revision_stage_key
                    task.update_state(ws.TASK_MAX_REVISIONS_EXCEEDED_FAILURE, self.name, action_summary, event_base_details)
                else:
                    task.metadata["last_revision_request_key"] = revision_stage_key
                    action_summary += f"FAILED, sending for revision to {revision_target_state} (Attempt {current_rev_count_for_stage} for {revision_stage_key})."
                    event_base_details["revision_target_state"] = revision_target_state; event_base_details["revision_stage_key"] = revision_stage_key
                    task.update_state(revision_target_state, self.name, action_summary, event_base_details)
            else:
                action_summary += "FAILED. No clear revision path or specific issue maxed out revisions."
                task.update_state(ws.TASK_FAILED_FINAL_REVIEW, self.name, action_summary, event_base_details)
        return approved
