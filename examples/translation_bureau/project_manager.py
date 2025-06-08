from typing import Any, List, Dict, Optional # Added List, Dict, Optional for reporting methods
# Assuming TranslationTask and workflow_states might be useful for type hinting or logic here
from examples.translation_bureau.task_models import TranslationTask
import examples.translation_bureau.workflow_states as ws
import datetime
from collections import defaultdict # Added import


class ProjectManager:
    def __init__(self, name: str):
        self.name = name
        # print(f"ProjectManager {self.name} initialized.") # Will be logged by main simulation

    def initiate_translation_task(self, task: TranslationTask) -> None:
        # This method is monkey-patched in main.py for the simulation.
        # The adapter in main.py should handle logging rich details.
        # This original method is here for conceptual completeness or if used differently.
        original_details = {"message": f"PM {self.name}: (Original method) Initiating for task {task.task_id}.",
                            "source_language": task.source_language, "target_language": task.target_language}
        if task.current_state == ws.TASK_UPLOADED:
            task.update_state(ws.TASK_ON_HOLD, agent_name=self.name,
                              action_details="Awaiting specific workflow assignment by adapter.",
                              event_details=original_details)

    def flag_task_for_manual_review(self, task: TranslationTask, reason: str) -> None:
        """Flags a task for manual intervention or review."""
        # This print will be replaced by log_workflow_event in main.py when called
        # print(f"ALERT - PM {self.name}: Task {task.task_id} (State: {task.current_state}) requires MANUAL REVIEW. Reason: {reason}")

        event_details: Dict[str, Any] = {
            "reason": reason,
            "task_id": task.task_id,
            "current_task_state": task.current_state,
            "message": f"Task {task.task_id} escalated for manual review due to: {reason}."
        }
        task.add_history_event(agent=self.name, action="EscalationForManualReview", details=event_details)
        # The task state (e.g., TASK_MAX_RETRIES_EXCEEDED_FAILURE) is set by the workflow engine before calling this.

    def generate_task_summary_report(self, task: TranslationTask) -> str:
        report_parts = [f"--- Task Summary Report for Task ID: {task.task_id} ---"]
        report_parts.append(f"  Original Text: '{task.original_text[:100]}...'")
        report_parts.append(f"  Source Language: {task.source_language}, Target Language: {task.target_language}")
        report_parts.append(f"  Current Status: {task.current_state}")
        report_parts.append(f"  Metadata: {task.metadata}")
        report_parts.append(f"  API Call Retry Count: {task.retry_count}")
        report_parts.append(f"  Revision Counts by Stage: {dict(task.revision_counts)}")

        report_parts.append("\n  Workflow History:")
        for event in task.history:
            timestamp = event.get("timestamp", "N/A")
            actor = event.get("agent", "System")
            action = event.get("action", "UnknownAction")
            details_str = str(event.get("details", {})) # Convert dict to string for basic report
            log_line = f"    - {timestamp} | {actor} | {action}"
            if event.get("previous_state") and event.get("new_state"):
                log_line += f" | StateChange: {event['previous_state']} -> {event['new_state']}"
            log_line += f" | Details: {details_str[:150]}{'...' if len(details_str)>150 else ''}" # Truncate long details
            report_parts.append(log_line)

        report_parts.append("\n  QA Feedback Received:")
        if task.qa_feedback:
            for fb in task.qa_feedback:
                timestamp = fb.get("timestamp", "N/A")
                role = fb.get("agent_role", "UnknownRole")
                fb_type = fb.get("feedback_type", "General")
                comments = fb.get("comments", "")
                action_req = fb.get("requested_action", "None")
                target_rev_stage = fb.get("target_revision_stage", "N/A")
                report_parts.append(f"    - {timestamp} | {role} ({fb_type}): {comments} [Action: {action_req}, Target Stage for Rev: {target_rev_stage}]")
        else:
            report_parts.append("    - No QA feedback recorded.")

        report_parts.append("--- End of Report ---")
        return "\n".join(report_parts)

    def generate_bureau_summary_report(self, tasks: List[TranslationTask]) -> str:
        report_parts = [f"--- Bureau Summary Report ({datetime.datetime.utcnow().isoformat()}) ---"]
        report_parts.append(f"Total Tasks Processed: {len(tasks)}")

        status_counts: Dict[str, int] = defaultdict(int)
        completed_frca = 0
        completed_enca = 0

        for task in tasks:
            status_counts[task.current_state] += 1
            if task.current_state == ws.TASK_COMPLETED_FRCA:
                completed_frca += 1
            elif task.current_state == ws.TASK_COMPLETED_ENCA:
                completed_enca += 1

        report_parts.append("\n  Tasks by Final Status:")
        for status, count in status_counts.items():
            report_parts.append(f"    - {status}: {count}")

        report_parts.append(f"\n  Successfully Completed (FR_CA target): {completed_frca}")
        report_parts.append(f"  Successfully Completed (EN_CA target): {completed_enca}")

        failed_max_retries = status_counts.get(ws.TASK_MAX_RETRIES_EXCEEDED_FAILURE, 0)
        failed_max_revisions = status_counts.get(ws.TASK_MAX_REVISIONS_EXCEEDED_FAILURE, 0)
        failed_other = status_counts.get(ws.TASK_FAILED_FINAL_REVIEW, 0) + \
                       status_counts.get(ws.TASK_CONFIGURATION_ERROR_FAILURE, 0) + \
                       status_counts.get(ws.TASK_UNKNOWN_FAILURE, 0)

        report_parts.append(f"  Failed (Max API Retries): {failed_max_retries}")
        report_parts.append(f"  Failed (Max Revisions): {failed_max_revisions}")
        report_parts.append(f"  Failed (Other reasons): {failed_other}")

        report_parts.append("\n--- End of Bureau Summary ---")
        return "\n".join(report_parts)
