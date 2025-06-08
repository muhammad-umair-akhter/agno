# Defines string constants for all anticipated workflow states in the advanced bureau.

# General Task States
TASK_CREATED = "task_created"
TASK_UPLOADED = "task_uploaded"
TASK_INITIATED_BY_PM = "task_initiated_by_pm"
TASK_QUEUED_FOR_TRANSLATION = "task_queued_for_translation"
TASK_ON_HOLD = "task_on_hold"
TASK_CANCELLED = "task_cancelled"

# English to French (Canada) Workflow States
EN_FRCA_INITIAL_TRANSLATION_PENDING = "en_frca_initial_translation_pending"
# EN_FRCA_INITIAL_TRANSLATION_IN_PROGRESS = "en_frca_initial_translation_in_progress" # Not strictly needed if agent completes in one go
# EN_FRCA_INITIAL_TRANSLATION_COMPLETED = "en_frca_initial_translation_completed" # Implied by next state

FRCA_GRAMMAR_REVIEW_PENDING = "frca_grammar_review_pending"
FRCA_GRAMMAR_API_ERROR_RETRY_PENDING = "frca_grammar_api_error_retry_pending"
EN_FRCA_INITIAL_TRANSLATION_REVISION_PENDING = "en_frca_initial_translation_revision_pending" # For issues found in grammar that need re-translation

FRCA_NUANCE_CONTEXT_REVIEW_PENDING = "frca_nuance_context_review_pending"
FRCA_GRAMMAR_REVISION_PENDING = "frca_grammar_revision_pending" # If nuance expert finds grammar issue after grammar check passed (less common)

FRCA_STYLE_TONE_REVIEW_PENDING = "frca_style_tone_review_pending"
FRCA_NUANCE_REVISION_PENDING = "frca_nuance_revision_pending" # If style editor finds nuance issue

FRCA_TERMINOLOGY_REVIEW_PENDING = "frca_terminology_review_pending"
FRCA_TERMINOLOGY_API_ERROR_RETRY_PENDING = "frca_terminology_api_error_retry_pending"
FRCA_STYLE_REVISION_PENDING = "frca_style_revision_pending" # If terminology finds style issue

FRCA_FINAL_REVIEW_PENDING = "frca_final_review_pending"
# Final reviewer can send back to any prior stage, e.g.
# FRCA_TERMINOLOGY_REVISION_PENDING_BY_FINAL = "frca_terminology_revision_pending_by_final"
# FRCA_NUANCE_REVISION_PENDING_BY_FINAL = "frca_nuance_revision_pending_by_final"
# etc. For simplicity, can reuse existing revision states or create specific "by_final" ones.
# Let's use generic ones first and specify source of feedback in task.qa_feedback

TASK_COMPLETED_FRCA = "task_completed_frca"

# French (Canada) to English Workflow States (mirroring EN_FRCA)
FRCA_EN_INITIAL_TRANSLATION_PENDING = "frca_en_initial_translation_pending"

ENCA_GRAMMAR_REVIEW_PENDING = "enca_grammar_review_pending"
ENCA_GRAMMAR_API_ERROR_RETRY_PENDING = "enca_grammar_api_error_retry_pending"
ENCA_INITIAL_TRANSLATION_REVISION_PENDING = "enca_initial_translation_revision_pending"

ENCA_NUANCE_CONTEXT_REVIEW_PENDING = "enca_nuance_context_review_pending"
ENCA_GRAMMAR_REVISION_PENDING = "enca_grammar_revision_pending"

ENCA_STYLE_TONE_REVIEW_PENDING = "enca_style_tone_review_pending"
ENCA_NUANCE_REVISION_PENDING = "enca_nuance_revision_pending"

ENCA_TERMINOLOGY_REVIEW_PENDING = "enca_terminology_review_pending"
ENCA_TERMINOLOGY_API_ERROR_RETRY_PENDING = "enca_terminology_api_error_retry_pending"
ENCA_STYLE_REVISION_PENDING = "enca_style_revision_pending"

ENCA_FINAL_REVIEW_PENDING = "enca_final_review_pending"
TASK_COMPLETED_ENCA = "task_completed_enca"

# General Revision States (simpler to manage than per-step "requested_by_X")
# The specific feedback in task.qa_feedback will indicate who requested it and why.
# The PM or workflow engine can then route to the correct PENDING state of the stage to be revised.
# Example: If Final Reviewer FRCA finds a nuance issue, they add feedback, and state might become FRCA_NUANCE_REVIEW_PENDING.

# Failure States
TASK_FAILED_QA = "task_failed_qa"
TASK_FAILED_FINAL_REVIEW = "task_failed_final_review" # If final review explicitly fails without revision
TASK_MAX_RETRIES_EXCEEDED_FAILURE = "task_max_retries_exceeded_failure"
TASK_MAX_REVISIONS_EXCEEDED_FAILURE = "task_max_revisions_exceeded_failure" # New
TASK_CONFIGURATION_ERROR_FAILURE = "task_configuration_error_failure"
TASK_UNKNOWN_FAILURE = "task_unknown_failure"
