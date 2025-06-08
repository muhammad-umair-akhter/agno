# Advanced Translation Bureau Simulation

## 1. Overview

This example presents an advanced simulation of a multi-agent translation bureau, specifically focusing on translations between Canadian English (EN_CA) and Canadian French (FR_CA). It aims to demonstrate sophisticated agentic system concepts, including:

*   **Specialized Agent Roles:** Multiple agents, each an expert in a specific part of the translation and review process. This includes explicit source text context identification by the Nuance Expert and nuanced grammar/terminology checks for Canadian French specifics.
*   **Complex Workflows:** Multi-step processing paths tailored for each translation direction.
*   **State Management:** Robust tracking of task status, content evolution (including multiple text versions and analysis results like source context), and detailed history.
*   **Error Handling & Retries:** Resilience to transient failures from simulated external APIs, with automated retry mechanisms.
*   **QA & Revision Loops:** Iterative quality assurance cycles where feedback from later-stage reviewers can send tasks back to earlier specialist agents for rework. Revision counts are tracked to prevent infinite loops.
*   **Escalation Mechanisms:** Tasks failing repeatedly (either due to API errors or excessive revisions) are flagged to the Project Manager.

The simulation is designed to showcase elements of **Level 4 (Reasoning & Collaboration)** and **Level 5 (Stateful & Deterministic Workflows)** agentic capabilities. Agents collaborate by passing tasks and structured feedback, operate on a stateful `TranslationTask` object, and follow deterministic logic within a managed workflow.

## 2. Project Structure

The core components of this simulation are located within the `examples/translation_bureau/` directory:

*   **`main.py`**: The central orchestrator. It initializes agents, APIs, and tasks, then runs the main simulation loop, dispatching tasks to appropriate agents based on their current state. It also includes a basic logging utility.
*   **`task_models.py`**: Defines the `TranslationTask` dataclass. This is the central data structure holding all information about a translation job: original text, text versions (including analysis like source context), QA feedback, detailed event history, current state, API retry counts, stage-specific revision counts, and metadata.
*   **`workflow_states.py`**: Contains string constants defining all possible states a `TranslationTask` can be in (e.g., `EN_FRCA_INITIAL_TRANSLATION_PENDING`, `FRCA_GRAMMAR_API_ERROR_RETRY_PENDING`, `FRCA_NUANCE_REVISION_PENDING`, `TASK_MAX_REVISIONS_EXCEEDED_FAILURE`).
*   **`apis.py`**: Houses mock external APIs that agents interact with (e.g., for grammar checking, nuance analysis, terminology verification). Some APIs simulate errors and provide detailed (mock) analysis results.
*   **Agent Files:**
    *   `project_manager.py`: `ProjectManager` (initiates tasks, handles escalations, generates summary reports).
    *   `initial_translator.py`: `EN_FRCA_InitialTranslator`, `FRCA_EN_InitialTranslator` (perform initial translation drafts, can be sent tasks for revision).
    *   `grammar_specialist.py`: `FRCA_GrammarSpecialist`, `ENCA_GrammarSpecialist` (review grammar using specialized mock APIs).
    *   `nuance_context_expert.py`: `FRCA_NuanceContextExpert`, `ENCA_NuanceContextExpert` (perform initial source text context analysis and then assess cultural nuances in translated text).
    *   `style_tone_editor.py`: `FRCA_StyleToneEditor`, `ENCA_StyleToneEditor` (edit for style and tone, now context-aware).
    *   `terminology_checker.py`: `TerminologyConsistencyChecker` (verifies domain-specific terms against a mock termbase, distinguishes universal names).
    *   `final_reviewer.py`: `FinalQualityGate_FRCA`, `FinalQualityGate_ENCA` (perform holistic final quality checks, can request targeted revisions to prior stages).
*   **`original_text.py`**: Contains a dictionary of `ORIGINAL_TEXTS` used as source material, including texts designed to trigger various specific checks.

## 3. Agent Roles and Responsibilities (EN_CA <-> FR_CA)

*   **`ProjectManager`**: Initiates tasks, handles escalations (max API retries, max revisions), and generates end-of-simulation summary reports.
*   **`EN_FRCA_InitialTranslator` / `FRCA_EN_InitialTranslator`**: Creates initial translation drafts. Mock logic may introduce common errors or specific terms to test downstream agents. Can receive tasks for revision if its initial draft is deemed problematic by a subsequent reviewer.
*   **`FRCA_GrammarSpecialist` / `ENCA_GrammarSpecialist`**:
    *   Uses `CanadianFrenchGrammarAPI` or `CanadianEnglishGrammarAPI`.
    *   The `CanadianFrenchGrammarAPI` specifically simulates checks for common Canadian French anglicisms (e.g., "checker", "le fun", "bumper") and France French terms where Canadian alternatives are preferred (e.g., "voiture" vs "char").
    *   Feedback reflects these specific linguistic nuances.
*   **`FRCA_NuanceContextExpert` / `ENCA_NuanceContextExpert`**:
    *   **Crucially, performs an initial `_identify_source_text_context` step**, analyzing the *original source text* to determine its general context (e.g., "Technical/Software," "Strong Canadian cultural references," "Business/Formal," "General conversation"). This analysis is stored in `task.text_versions`.
    *   Then, assesses the *translated text* for cultural appropriateness and contextual alignment, potentially using the identified source context to inform its judgment.
*   **`FRCA_StyleToneEditor` / `ENCA_StyleToneEditor`**:
    *   Adjusts the translated text for appropriate style and tone.
    *   **Now considers the `source_context_analysis`** (e.g., "Technical/Software") performed by the Nuance Expert. For example, it might enforce a more formal tone if the context is technical, even if the task metadata's target style was initially different.
    *   Feedback may mention how style aligns with source context.
*   **`TerminologyConsistencyChecker`**:
    *   Uses `TerminologyDatabaseAPI` to check against project-specific termbases and a list of "universal names" (e.g., "hockey", "CPU", "internet").
    *   **Differentiates between critical untranslated project terms** (flagged as errors) and **correctly untranslated universal names** (acknowledged as 'ok_acknowledged', not errors).
*   **`FinalQualityGate_FRCA` / `FinalQualityGate_ENCA`**:
    *   Performs a final holistic review.
    *   **Leverages `source_context_analysis`** and all prior `task.qa_feedback` to simulate checks for overall cohesion, contextual accuracy, and unresolved critical issues.
    *   If issues are found, it can make more **targeted revision requests** to specific earlier stages (e.g., back to Nuance Expert if the issue is contextual despite style changes, or to Style Editor if the tone is off for the identified context).

## 4. Workflow Explained

Tasks are initiated by the `ProjectManager` and flow through a pipeline of specialized agents. The `main.py` engine manages state transitions based on agent outputs.

*   **Context-Driven Processing**: The workflow now incorporates explicit source context analysis early on (by Nuance Expert). This context is available to subsequent agents like Style Editor and Final Reviewer, allowing for more informed, context-aware decision-making in their respective tasks.
*   **Nuanced QA**: Grammar and Terminology checks are more sophisticated:
    *   `FRCA_GrammarSpecialist` looks for Canadian French specific issues.
    *   `TerminologyConsistencyChecker` understands universal names, reducing false positives while still catching missed project-specific translations.
*   **Holistic Final Review**: `FinalQualityGate_FRCA` doesn't just look for isolated errors but simulates an assessment of overall quality, including whether the translation is cohesive and contextually appropriate given the source material. Based on this, it can trigger targeted revision loops.
*   **State Management, Error Handling, Revisions**: These remain key features as described previously, with `TranslationTask` tracking all details. Revision loops now benefit from more specific feedback and can be initiated by the Final Reviewer to earlier, specific stages.

## 5. Mock APIs

The `apis.py` file provides mock APIs for:
*   `CanadianFrenchGrammarAPI` & `CanadianEnglishGrammarAPI`: Simulate grammar checks, with the French version now looking for specific Canadian French characteristics (anglicisms, term preferences). Both can simulate errors.
*   `NuanceContextAPI`: Simulates nuance/cultural appropriateness checks.
*   `StyleToneAPI`: Simulates style/tone analysis.
*   `TerminologyDatabaseAPI`: Simulates project termbase lookups and includes awareness of universal names. Can simulate errors.

## 6. How to Run the Example

1.  Ensure your Python environment is set up.
2.  Navigate to the root directory of this repository.
3.  Set the `PYTHONPATH` environment variable:
    *   Linux/macOS: `export PYTHONPATH=$(pwd)`
    *   Windows (CMD): `set PYTHONPATH=%CD%`
    *   Windows (PowerShell): `$env:PYTHONPATH = $pwd.Path`
4.  Run the main simulation script:
    ```bash
    python examples/translation_bureau/main.py
    ```

## 7. Interpreting the Output

*   **Workflow Logs**: `log_workflow_event` messages from `main.py` show task progression, state changes, API retries, and revision routing decisions.
*   **Agent Logs**: `print()` statements within agent methods indicate specific actions (e.g., context identification by Nuance Expert, specific checks by Grammar/Terminology APIs).
*   **Context Analysis**: Look for lines from `FRCA_NuanceContextExpert` like "Identified context: Technical/Software." and check `task.text_versions['source_context_analysis_frca']` in the detailed reports.
*   **Specific Grammar/Terminology Feedback**: In the detailed task reports, under "QA Feedback Received," examine entries from `FRCA_GrammarSpecialist` for comments on anglicisms or preferred terms. For `TerminologyConsistencyChecker`, look for differentiation between untranslated terms and acknowledged universal names.
*   **Holistic Review Decisions**: Observe feedback from `FinalQualityGate_FRCA` to see if it requests revisions to specific stages based on its broader assessment.
*   **Reports**: The "Bureau Summary Report" gives overall statistics. Individual "Task Summary Reports" provide a rich history of each task, including all QA feedback and state transitions, reflecting the new agent capabilities.

## 8. Achieving Level 4/5 Agentic Capabilities

These refinements further solidify the simulation's demonstration of:
*   **Level 4 (Reasoning & Collaboration):** Agents like `FRCA_StyleToneEditor` and `FinalQualityGate_FRCA` now use information (`source_context_analysis`) produced by another agent (`FRCA_NuanceContextExpert`) to refine their own reasoning and actions. Feedback is more targeted, improving collaboration in revision loops.
*   **Level 5 (Stateful & Deterministic Workflows):** The `TranslationTask` object becomes even more richly stateful with the inclusion of context analysis. The workflow engine deterministically routes tasks based on these nuanced states and feedback.

This example provides a robust model for simulating complex, collaborative, and adaptive multi-agent systems.The `README.md` has been created with the comprehensive information reflecting the latest agent refinements. All requested sections and details have been included.

The subtask's objectives are met:
-   The README accurately describes the enhanced roles of `FRCA_NuanceContextExpert` (context ID), `FRCA_GrammarSpecialist` (Canadian French specifics), `TerminologyConsistencyChecker` (universal names), `FRCA_StyleToneEditor` (context-aware), and `FinalQualityGate_FRCA` (holistic review).
-   The workflow explanation and output interpretation sections guide users on these new features.
-   The connection to Level 4/5 agentic capabilities is updated.

No further changes are needed.
