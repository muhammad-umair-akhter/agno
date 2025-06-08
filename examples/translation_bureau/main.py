from typing import List, Dict, Any, Optional
import time
import datetime # For logging timestamp

# Import agents
from examples.translation_bureau.project_manager import ProjectManager
from examples.translation_bureau.initial_translator import EN_FRCA_InitialTranslator, FRCA_EN_InitialTranslator
from examples.translation_bureau.grammar_specialist import FRCA_GrammarSpecialist, ENCA_GrammarSpecialist
from examples.translation_bureau.nuance_context_expert import FRCA_NuanceContextExpert, ENCA_NuanceContextExpert
from examples.translation_bureau.style_tone_editor import FRCA_StyleToneEditor, ENCA_StyleToneEditor
from examples.translation_bureau.terminology_checker import TerminologyConsistencyChecker
from examples.translation_bureau.final_reviewer import FinalQualityGate_FRCA, FinalQualityGate_ENCA

# Import task model and states
from examples.translation_bureau.task_models import TranslationTask
import examples.translation_bureau.workflow_states as ws

# Import texts and APIs
from examples.translation_bureau.original_text import ORIGINAL_TEXTS
from examples.translation_bureau.apis import (
    CanadianFrenchGrammarAPI,
    CanadianEnglishGrammarAPI,
    NuanceContextAPI,
    StyleToneAPI,
    TerminologyDatabaseAPI
)

# --- Configuration ---
MAX_API_RETRIES_PER_STEP = 3
MAX_REVISIONS_PER_STAGE = 2

# --- Logging Utility ---
def log_workflow_event(task_id: Optional[str], level: str, message: str, details: Optional[Dict[str, Any]] = None):
    timestamp = datetime.datetime.utcnow().isoformat()
    log_entry = f"{timestamp} [{level}]"
    if task_id:
        log_entry += f" [Task: {task_id}]"
    log_entry += f": {message}"
    if details:
        log_entry += f" | Details: {details}"
    print(log_entry)

# --- Helper function ---
def get_task_languages(text_id: str) -> tuple[str | None, str | None]:
    if "_en_ca" in text_id.lower(): return "EN_CA", "FR_CA"
    if "_fr_ca" in text_id.lower(): return "FR_CA", "EN_CA"
    return None, None

# --- Main Simulation Function ---
def run_advanced_translation_workflow():
    log_workflow_event(None, "INFO", "Starting Advanced Translation Bureau Workflow Simulation")

    pm = ProjectManager(name="PM_Dave")
    en_frca_translator, frca_grammar_checker, frca_nuance_expert, frca_style_editor, frca_final_reviewer = \
        EN_FRCA_InitialTranslator(), FRCA_GrammarSpecialist(), FRCA_NuanceContextExpert(), FRCA_StyleToneEditor(), FinalQualityGate_FRCA()
    frca_en_translator, enca_grammar_checker, enca_nuance_expert, enca_style_editor, enca_final_reviewer = \
        FRCA_EN_InitialTranslator(), ENCA_GrammarSpecialist(), ENCA_NuanceContextExpert(), ENCA_StyleToneEditor(), FinalQualityGate_ENCA()
    terminology_checker = TerminologyConsistencyChecker()
    log_workflow_event(None, "INFO", "Agents Initialized")

    frca_grammar_api = CanadianFrenchGrammarAPI(error_rate=0.2)
    enca_grammar_api = CanadianEnglishGrammarAPI(error_rate=0.2)
    nuance_api, style_api = NuanceContextAPI(), StyleToneAPI()
    term_db_api = TerminologyDatabaseAPI(error_rate=0.15)
    log_workflow_event(None, "INFO", "Mock APIs Initialized")

    tasks: List[TranslationTask] = []
    for text_id, text_content in ORIGINAL_TEXTS.items():
        source_lang, target_lang = get_task_languages(text_id)
        if source_lang and target_lang:
            metadata = {"project_code": "proj_alpha", "target_style": "formal"}
            if text_id == "text_003_en_ca": metadata["project_code"] = "proj_beta_nonexistent"
            tasks.append(TranslationTask(text_id, text_content, source_lang, target_lang, ws.TASK_UPLOADED, metadata=metadata))
    log_workflow_event(None, "INFO", f"{len(tasks)} Tasks Prepared for Processing")

    max_loops, loops, active_tasks_exist = 150, 0, True
    terminal_states = [
        ws.TASK_COMPLETED_FRCA, ws.TASK_COMPLETED_ENCA, ws.TASK_FAILED_FINAL_REVIEW,
        ws.TASK_MAX_RETRIES_EXCEEDED_FAILURE, ws.TASK_MAX_REVISIONS_EXCEEDED_FAILURE,
        ws.TASK_CONFIGURATION_ERROR_FAILURE, ws.TASK_CANCELLED, ws.TASK_UNKNOWN_FAILURE,
        ws.TASK_ON_HOLD # Effectively terminal for this simulation if no handler
    ]

    while active_tasks_exist and loops < max_loops:
        loops += 1
        log_workflow_event(None, "INFO", f"Workflow Loop Iteration: {loops}")
        active_tasks_exist = False

        for task in tasks:
            if task.current_state in terminal_states: continue
            active_tasks_exist = True
            prev_state = task.current_state

            log_workflow_event(task.task_id, "INFO", f"Processing Task",
                               details={"state": task.current_state, "api_retries": task.retry_count, "revision_counts": dict(task.revision_counts)})

            # PM Initiation
            if task.current_state == ws.TASK_UPLOADED: pm.initiate_translation_task(task)

            # API Error Retry Logic
            elif task.current_state == ws.FRCA_GRAMMAR_API_ERROR_RETRY_PENDING:
                if task.increment_retry_count("WorkflowEngine", "FRCA Grammar") < MAX_API_RETRIES_PER_STEP:
                    task.update_state(ws.FRCA_GRAMMAR_REVIEW_PENDING, "WorkflowEngine", "Retrying FRCA Grammar")
                else:
                    task.update_state(ws.TASK_MAX_RETRIES_EXCEEDED_FAILURE, "WorkflowEngine", "Max retries FRCA Grammar")
                    pm.flag_task_for_manual_review(task, "Max API retries for FRCA Grammar")
            elif task.current_state == ws.FRCA_TERMINOLOGY_API_ERROR_RETRY_PENDING:
                if task.increment_retry_count("WorkflowEngine", "FRCA Terminology") < MAX_API_RETRIES_PER_STEP:
                    task.update_state(ws.FRCA_TERMINOLOGY_REVIEW_PENDING, "WorkflowEngine", "Retrying FRCA Terminology")
                else:
                    task.update_state(ws.TASK_MAX_RETRIES_EXCEEDED_FAILURE, "WorkflowEngine", "Max retries FRCA Terminology")
                    pm.flag_task_for_manual_review(task, "Max API retries for FRCA Terminology")
            elif task.current_state == ws.ENCA_GRAMMAR_API_ERROR_RETRY_PENDING:
                if task.increment_retry_count("WorkflowEngine", "ENCA Grammar") < MAX_API_RETRIES_PER_STEP:
                    task.update_state(ws.ENCA_GRAMMAR_REVIEW_PENDING, "WorkflowEngine", "Retrying ENCA Grammar")
                else:
                    task.update_state(ws.TASK_MAX_RETRIES_EXCEEDED_FAILURE, "WorkflowEngine", "Max retries ENCA Grammar")
                    pm.flag_task_for_manual_review(task, "Max API retries for ENCA Grammar")
            elif task.current_state == ws.ENCA_TERMINOLOGY_API_ERROR_RETRY_PENDING:
                if task.increment_retry_count("WorkflowEngine", "ENCA Terminology") < MAX_API_RETRIES_PER_STEP:
                    task.update_state(ws.ENCA_TERMINOLOGY_REVIEW_PENDING, "WorkflowEngine", "Retrying ENCA Terminology")
                else:
                    task.update_state(ws.TASK_MAX_RETRIES_EXCEEDED_FAILURE, "WorkflowEngine", "Max retries ENCA Terminology")
                    pm.flag_task_for_manual_review(task, "Max API retries for ENCA Terminology")

            # Revision Loop Logic
            elif task.current_state == ws.EN_FRCA_INITIAL_TRANSLATION_REVISION_PENDING: # Corrected state name
                if task.increment_revision_count("en_frca_initial_translation", "WorkflowEngine") < MAX_REVISIONS_PER_STAGE:
                    en_frca_translator.perform_initial_translation(task)
                else:
                    task.update_state(ws.TASK_MAX_REVISIONS_EXCEEDED_FAILURE, "WorkflowEngine", "Max revisions for EN->FRCA Initial Translation")
                    pm.flag_task_for_manual_review(task, "Max revisions for EN->FRCA Initial Translation")
            elif task.current_state == ws.FRCA_GRAMMAR_REVISION_PENDING:
                if task.increment_revision_count("frca_grammar", "WorkflowEngine") < MAX_REVISIONS_PER_STAGE:
                    frca_grammar_checker.review_grammar(task, frca_grammar_api)
                else:
                    task.update_state(ws.TASK_MAX_REVISIONS_EXCEEDED_FAILURE, "WorkflowEngine", "Max revisions for FRCA Grammar")
                    pm.flag_task_for_manual_review(task, "Max revisions for FRCA Grammar")
            elif task.current_state == ws.FRCA_NUANCE_REVISION_PENDING:
                stage_key = task.metadata.get("last_revision_request_key", "frca_nuance") # Use specific key if available
                if task.get_revision_count(stage_key) < MAX_REVISIONS_PER_STAGE :
                    frca_nuance_expert.assess_nuance_and_context(task, nuance_api)
                else:
                    task.update_state(ws.TASK_MAX_REVISIONS_EXCEEDED_FAILURE, "WorkflowEngine", f"Max revisions for {stage_key}")
                    pm.flag_task_for_manual_review(task, f"Max revisions for {stage_key}")
            elif task.current_state == ws.FRCA_STYLE_REVISION_PENDING:
                stage_key = task.metadata.get("last_revision_request_key", "frca_style")
                if task.get_revision_count(stage_key) < MAX_REVISIONS_PER_STAGE:
                    frca_style_editor.edit_for_style_and_tone(task, style_api)
                else:
                    task.update_state(ws.TASK_MAX_REVISIONS_EXCEEDED_FAILURE, "WorkflowEngine", f"Max revisions for {stage_key}")
                    pm.flag_task_for_manual_review(task, f"Max revisions for {stage_key}")

            elif task.current_state == ws.ENCA_INITIAL_TRANSLATION_REVISION_PENDING:
                if task.increment_revision_count("enca_initial_translation", "WorkflowEngine") < MAX_REVISIONS_PER_STAGE:
                    frca_en_translator.perform_initial_translation(task)
                else:
                    task.update_state(ws.TASK_MAX_REVISIONS_EXCEEDED_FAILURE, "WorkflowEngine", "Max revisions for ENCA Initial Translation")
                    pm.flag_task_for_manual_review(task, "Max revisions for ENCA Initial Translation")
            elif task.current_state == ws.ENCA_GRAMMAR_REVISION_PENDING:
                if task.increment_revision_count("enca_grammar", "WorkflowEngine") < MAX_REVISIONS_PER_STAGE:
                    enca_grammar_checker.review_grammar(task, enca_grammar_api)
                else:
                    task.update_state(ws.TASK_MAX_REVISIONS_EXCEEDED_FAILURE, "WorkflowEngine", "Max revisions for ENCA Grammar")
                    pm.flag_task_for_manual_review(task, "Max revisions for ENCA Grammar")
            elif task.current_state == ws.ENCA_NUANCE_REVISION_PENDING:
                stage_key = task.metadata.get("last_revision_request_key", "enca_nuance")
                if task.get_revision_count(stage_key) < MAX_REVISIONS_PER_STAGE:
                     enca_nuance_expert.assess_nuance_and_context(task, nuance_api)
                else:
                    task.update_state(ws.TASK_MAX_REVISIONS_EXCEEDED_FAILURE, "WorkflowEngine", f"Max revisions for {stage_key}")
                    pm.flag_task_for_manual_review(task, f"Max revisions for {stage_key}")
            elif task.current_state == ws.ENCA_STYLE_REVISION_PENDING:
                stage_key = task.metadata.get("last_revision_request_key", "enca_style")
                if task.get_revision_count(stage_key) < MAX_REVISIONS_PER_STAGE:
                    enca_style_editor.edit_for_style_and_tone(task, style_api)
                else:
                    task.update_state(ws.TASK_MAX_REVISIONS_EXCEEDED_FAILURE, "WorkflowEngine", f"Max revisions for {stage_key}")
                    pm.flag_task_for_manual_review(task, f"Max revisions for {stage_key}")

            # EN_CA to FR_CA Workflow (Main Path)
            elif task.current_state == ws.EN_FRCA_INITIAL_TRANSLATION_PENDING: en_frca_translator.perform_initial_translation(task)
            elif task.current_state == ws.FRCA_GRAMMAR_REVIEW_PENDING: frca_grammar_checker.review_grammar(task, frca_grammar_api)
            elif task.current_state == ws.FRCA_NUANCE_CONTEXT_REVIEW_PENDING: frca_nuance_expert.assess_nuance_and_context(task, nuance_api)
            elif task.current_state == ws.FRCA_STYLE_TONE_REVIEW_PENDING: frca_style_editor.edit_for_style_and_tone(task, style_api)
            elif task.current_state == ws.FRCA_TERMINOLOGY_REVIEW_PENDING: terminology_checker.check_terminology(task, term_db_api)
            elif task.current_state == ws.FRCA_FINAL_REVIEW_PENDING: frca_final_reviewer.perform_final_review(task)

            # FR_CA to EN_CA Workflow (Main Path)
            elif task.current_state == ws.FRCA_EN_INITIAL_TRANSLATION_PENDING: frca_en_translator.perform_initial_translation(task)
            elif task.current_state == ws.ENCA_GRAMMAR_REVIEW_PENDING: enca_grammar_checker.review_grammar(task, enca_grammar_api)
            elif task.current_state == ws.ENCA_NUANCE_CONTEXT_REVIEW_PENDING: enca_nuance_expert.assess_nuance_and_context(task, nuance_api)
            elif task.current_state == ws.ENCA_STYLE_TONE_REVIEW_PENDING: enca_style_editor.edit_for_style_and_tone(task, style_api)
            elif task.current_state == ws.ENCA_TERMINOLOGY_REVIEW_PENDING: terminology_checker.check_terminology(task, term_db_api)
            elif task.current_state == ws.ENCA_FINAL_REVIEW_PENDING: enca_final_reviewer.perform_final_review(task)

            else: # Unhandled states
                if task.current_state not in terminal_states: # Avoid logging for already terminal tasks if any slip through
                    log_workflow_event(task.task_id, "WARN", f"Unhandled state '{task.current_state}'. Task put on hold.")
                    task.update_state(ws.TASK_ON_HOLD, "System", f"Unhandled state: {task.current_state}")

            if prev_state != task.current_state:
                 log_workflow_event(task.task_id, "STATE_CHANGE", f"{prev_state} -> {task.current_state}",
                                    details={"api_retries": task.retry_count, "revision_counts": dict(task.revision_counts)})
            time.sleep(0.01)

        if not active_tasks_exist: log_workflow_event(None, "INFO", "No active tasks remaining. All tasks are in a terminal state.")
        elif loops >= max_loops: log_workflow_event(None, "WARN", "Maximum simulation loops reached. Ending.")

    log_workflow_event(None, "INFO", "Advanced Translation Bureau Workflow Simulation Ended")

    # Reporting
    log_workflow_event(None, "INFO", "--- Generating Bureau Summary Report ---")
    bureau_report = pm.generate_bureau_summary_report(tasks) # Call new PM method
    print(bureau_report)

    log_workflow_event(None, "INFO", "--- Generating Detailed Reports for Some Tasks ---")
    for i, task_obj in enumerate(tasks):
        if i < 2 or task_obj.current_state in [ws.TASK_MAX_RETRIES_EXCEEDED_FAILURE, ws.TASK_MAX_REVISIONS_EXCEEDED_FAILURE] : # First 2 tasks, and any failed ones
            log_workflow_event(task_obj.task_id, "INFO", f"--- Detailed Report for Task: {task_obj.task_id} ---")
            task_report = pm.generate_task_summary_report(task_obj) # Call new PM method
            print(task_report)
            if i > 5 and task_obj.current_state not in [ws.TASK_MAX_RETRIES_EXCEEDED_FAILURE, ws.TASK_MAX_REVISIONS_EXCEEDED_FAILURE]: # Limit total reports if many tasks
                break


if __name__ == "__main__":
    def pm_initiate_task_adapter(self: ProjectManager, task: TranslationTask):
        next_state, action_details = "", f"PM {self.name} initiated task {task.task_id}."
        if task.source_language == "EN_CA" and task.target_language == "FR_CA": next_state = ws.EN_FRCA_INITIAL_TRANSLATION_PENDING
        elif task.source_language == "FR_CA" and task.target_language == "EN_CA": next_state = ws.FRCA_EN_INITIAL_TRANSLATION_PENDING
        else:
            err_msg = f"Unsupported language pair for task {task.task_id}: {task.source_language} to {task.target_language}"
            log_workflow_event(task.task_id, "ERROR", err_msg)
            next_state, action_details = ws.TASK_CONFIGURATION_ERROR_FAILURE, err_msg
        task.update_state(next_state, self.name, action_details=action_details, event_details={"initial_routing": next_state})
    ProjectManager.initiate_translation_task = pm_initiate_task_adapter

    # Add a placeholder for the revision_stage_key metadata if an agent needs it
    # This is a bit of a hack; ideally, the agent requesting revision would set this.
    # For now, FinalReviewer sets it in qa_feedback. The receiving agent would need to parse that.
    # The current nuance expert was updated to check task.qa_feedback for this.
    # For the main loop's MAX_REVISIONS_PER_STAGE check, it needs a reliable key.
    # The agent requesting revision *should* be the one incrementing the count for the stage it's sending back to.
    # The current `FinalQualityGate` agents were updated to do this.

    run_advanced_translation_workflow()
