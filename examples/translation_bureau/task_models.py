from typing import List, Dict, Any, Optional # Added Optional
from dataclasses import dataclass, field
import datetime
from collections import defaultdict

@dataclass
class TranslationTask:
    task_id: str
    original_text: str
    source_language: str
    target_language: str
    current_state: str

    text_versions: Dict[str, str] = field(default_factory=dict)
    qa_feedback: List[Dict[str, Any]] = field(default_factory=list)
    history: List[Dict[str, Any]] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    retry_count: int = 0
    revision_counts: Dict[str, int] = field(default_factory=lambda: defaultdict(int))

    def __post_init__(self):
        if not self.text_versions:
            self.text_versions['original'] = self.original_text
        self.add_history_event(agent="System", action="TaskCreated", new_state=self.current_state,
                               details={"message": f"Task {self.task_id} initialized."})

    def update_state(self, new_state: str, agent_name: str = "SystemUpdate", action_details: Optional[str] = None, event_details: Optional[Dict[str, Any]] = None):
        previous_state = self.current_state
        self.current_state = new_state

        log_details: Dict[str, Any] = event_details if event_details is not None else {}
        log_details["message"] = f"State changed by {agent_name}."
        if action_details: # Simple string details
            log_details["action_summary"] = action_details

        self.add_history_event(agent=agent_name, action="StateChange", previous_state=previous_state, new_state=new_state, details=log_details)

    def add_text_version(self, version_name: str, text_content: str, agent_name: str):
        self.text_versions[version_name] = text_content
        self.add_history_event(agent=agent_name, action="TextVersionAdded",
                               details={"version_name": version_name, "agent": agent_name, "text_preview": text_content[:30]+"..."})

    def add_feedback(self, agent_role: str, feedback_type: str, comments: str, requested_action: str = "None", target_revision_stage: Optional[str] = None) -> None:
        feedback_item: Dict[str, Any] = { # Explicit typing for clarity
            "timestamp": datetime.datetime.utcnow().isoformat(),
            "agent_role": agent_role,
            "feedback_type": feedback_type,
            "comments": comments,
            "requested_action": requested_action
        }
        if target_revision_stage:
            feedback_item["target_revision_stage"] = target_revision_stage
        self.qa_feedback.append(feedback_item)
        self.add_history_event(agent=agent_role, action="FeedbackAdded",
                               details={"feedback_type": feedback_type, "agent": agent_role, "comments_preview": comments[:50]+"...", "requested_action": requested_action})

    def add_history_event(self, agent: str, action: str, previous_state: Optional[str] = None, new_state: Optional[str] = None, details: Optional[Dict[str, Any]] = None) -> None:
        event: Dict[str, Any] = { # Explicit typing
            "timestamp": datetime.datetime.utcnow().isoformat(),
            "agent": agent,
            "action": action,
        }
        if previous_state is not None: event["previous_state"] = previous_state
        if new_state is not None: event["new_state"] = new_state
        if details is not None: event["details"] = details
        else: event["details"] = {} # Ensure details key always exists
        self.history.append(event)

    def increment_retry_count(self, agent_name: str, step_details: str) -> int:
        self.retry_count += 1
        self.add_history_event(agent=agent_name, action="RetryIncremented",
                               details={"message": f"Retry count now {self.retry_count} for step: {step_details}.", "step": step_details, "new_retry_count": self.retry_count})
        return self.retry_count

    def reset_retry_count(self, agent_name: str, step_details: str):
        if self.retry_count > 0:
            old_retry_count = self.retry_count
            self.retry_count = 0
            self.add_history_event(agent=agent_name, action="RetryCountReset",
                                   details={"message": f"Retry count reset from {old_retry_count} after successful step: {step_details}.", "step": step_details, "previous_retry_count": old_retry_count})

    def increment_revision_count(self, stage_key: str, agent_name: str) -> int:
        self.revision_counts[stage_key] += 1
        self.add_history_event(agent=agent_name, action="RevisionIncremented",
                               details={"message": f"Revision count for stage '{stage_key}' is now {self.revision_counts[stage_key]}.", "stage": stage_key, "new_revision_count": self.revision_counts[stage_key]})
        return self.revision_counts[stage_key]

    def get_revision_count(self, stage_key: str) -> int:
        return self.revision_counts.get(stage_key, 0)

# Example Usage
if __name__ == '__main__':
    task = TranslationTask(
        task_id="task_log_001", original_text="Detailed logging test.", source_language="EN_CA", target_language="FR_CA",
        current_state="task_created", metadata={"project_code": "proj_log"}
    )
    task.update_state("EN_FRCA_INITIAL_TRANSLATION_PENDING", "PM_Dave", action_details="Sent for translation.", event_details={"priority": "high"})
    task.add_text_version("initial_draft", "C'est un brouillon.", "TranslatorBot")
    task.add_feedback("GrammarChecker", "Grammar", "Possible subject-verb agreement issue on line 3.", "RevisionRequired", target_revision_stage="FRCA_INITIAL_TRANSLATION_REVISION_PENDING")
    task.increment_retry_count("GrammarAPIHandler", "Grammar Check API Call")
    task.reset_retry_count("GrammarAPIHandler", "Grammar Check API Call")
    task.increment_revision_count("frca_grammar", "FinalReviewer")

    print(f"Task: {task.task_id}, State: {task.current_state}, Retries: {task.retry_count}, Revisions (frca_grammar): {task.get_revision_count('frca_grammar')}")
    print("\nHistory:")
    for entry in task.history:
       print(entry)
    print("\nFeedback:")
    for fb_entry in task.qa_feedback:
        print(fb_entry)
