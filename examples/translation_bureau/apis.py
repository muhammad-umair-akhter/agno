from typing import Any, Dict, List
import random
import re # For regex-based search of terms

# Custom API Exceptions
class APITimeoutError(Exception):
    """Simulates an API timeout error."""
    pass

class APIServiceUnavailableError(Exception):
    """Simulates a temporary API service unavailability."""
    pass

class APIResourceNotFoundError(Exception):
    """Simulates a resource not found error."""
    pass

class CanadianFrenchGrammarAPI:
    def __init__(self, error_rate: float = 0.15):
        self.error_rate = error_rate
        self.common_anglicisms = {
            "le fun": "du plaisir (ou un contexte plus spécifique comme 'c'est amusant')",
            "checker": "vérifier (ou consulter, regarder selon le contexte)",
            "watcher": "regarder (surtout pour la télévision, un film)",
            "party": "fête (ou soirée)",
            "anyway": "de toute façon (ou en tout cas, bref)",
            "bumper": "pare-chocs",
            "flat": "crevaison (pour un pneu) (ou appartement, logement)",
            "appointment": "rendez-vous"
        }
        self.generic_grammar_patterns = {
            r"\b(il les a (donner|manger|voir|prendre|faire))\b": "Potential past participle agreement error with 'avoir' and preceding direct object.",
            r"\bsi j'aurais\b": "Incorrect conditional: 'si j'avais' is generally preferred for past unreal conditions.",
            r"\bc'est les (filles|gars|livres)\b": "Potential agreement error: 'ce sont les...' might be preferred in formal writing."
        }
        self.france_to_canada_terms = {
            "voiture": {"suggestion": "char (familier) / auto", "note": "Bien que 'voiture' soit compris, 'char' est une option familière au Québec."},
            "dîner": {"suggestion": "souper (pour le repas du soir)", "note": "'Dîner' au Québec réfère typiquement au repas de midi."},
            "petit déjeuner": {"suggestion": "déjeuner (pour le repas du matin)", "note": "'Déjeuner' au Québec est le repas du matin."},
            "soixante-dix": {"suggestion": "septante", "note": "Bien que 'soixante-dix' soit standard, 'septante' est une alternative régionale dans certaines parties de la francophonie."},
            "weekend": {"suggestion": "fin de semaine", "note": "'Fin de semaine' est une expression courante et souvent préférée au Québec."}
        }

    def check_frca_grammar(self, text: str) -> Dict[str, Any]:
        print(f"API (FRCA_Grammar): Checking grammar for text: '{text[:50]}...'")
        if random.random() < self.error_rate:
            error_type = random.choice([APITimeoutError, APIServiceUnavailableError])
            print(f"API (FRCA_Grammar): SIMULATING ERROR: {error_type.__name__}")
            raise error_type(f"Simulated {error_type.__name__} in FRCA_Grammar API")

        issues = []
        text_lower = text.lower()
        for anglicism, suggestion in self.common_anglicisms.items():
            if re.search(r"\b" + re.escape(anglicism) + r"\b", text_lower, flags=re.IGNORECASE):
                issues.append({"type": "Anglicism (Canadian French)", "token": anglicism, "suggestion": suggestion, "details": "Anglicism detected."})
        for france_term, canada_suggestion_info in self.france_to_canada_terms.items():
            if re.search(r"\b" + re.escape(france_term) + r"\b", text_lower, flags=re.IGNORECASE):
                issues.append({"type": "Preferred Term Violation (Canadian French)", "token": france_term, "suggestion": canada_suggestion_info["suggestion"], "details": canada_suggestion_info["note"]})
        for pattern, description in self.generic_grammar_patterns.items():
            for match in re.finditer(pattern, text, flags=re.IGNORECASE):
                issues.append({"type": "Generic Grammar", "token": match.group(0), "suggestion": description, "offset": match.start()})

        score = 1.0
        notes = "Good adherence to Canadian French grammar and usage."
        if issues:
            score = max(0.3, 1.0 - len(issues) * 0.08)
            note_parts = [f"{len(issues)} issue(s) found."]
            if any(i["type"] == "Anglicism (Canadian French)" for i in issues): note_parts.append("Anglicisms present.")
            if any(i["type"] == "Preferred Term Violation (Canadian French)" for i in issues): note_parts.append("France-French terms used.")
            notes = " ".join(note_parts)
        return {"issues_found": issues, "score": round(score,2), "language": "FR-CA", "notes": notes}

class CanadianEnglishGrammarAPI: # (Content as before, with error simulation)
    def __init__(self, error_rate: float = 0.15):
        self.error_rate = error_rate
    def check_enca_grammar(self, text: str) -> Dict[str, Any]:
        print(f"API (ENCA_Grammar): Checking grammar for text: '{text[:50]}...'")
        if random.random() < self.error_rate:
            error_type = random.choice([APITimeoutError, APIServiceUnavailableError])
            print(f"API (ENCA_Grammar): SIMULATING ERROR: {error_type.__name__}")
            raise error_type(f"Simulated {error_type.__name__} in ENCA_Grammar API")
        issues = []
        if "color" in text.lower() and "colour" not in text.lower():
             issues.append({"type": "Spelling (Canadian English)", "token": "color", "suggestion": "Consider Canadian spelling 'colour'."})
        ize_matches = re.findall(r"\b(\w+)ize\b", text.lower())
        for match_root in ize_matches:
            issues.append({"type": "Spelling Preference (Canadian English)", "token": f"{match_root}ize", "suggestion": f"Consider using '{match_root}ise' if project style guide prefers it (e.g., 'organise' vs 'organize')."})
        score = 0.95; notes = "Good adherence to Canadian English grammar."
        if issues: score = max(0.5, 0.95 - len(issues) * 0.1); notes = "Review for Canadian English spelling and grammar points."
        return {"issues_found": issues, "score": round(score,2), "language": "EN-CA", "notes": notes}

class NuanceContextAPI: # (Content as before)
    def analyze_nuance(self, text: str, language_pair: str) -> Dict[str, Any]:
        print(f"API (NuanceContext): Analyzing nuance for lang pair '{language_pair}' in text: '{text[:50]}...'")
        appropriateness_score = 0.88
        if "faux pas example" in text: appropriateness_score = 0.5
        return {"appropriateness_score": appropriateness_score, "cultural_references_ok": True, "language_pair": language_pair}

class StyleToneAPI: # (Content as before)
    def analyze_style_tone(self, text: str, language: str, expected_tone: str = "neutral") -> Dict[str, Any]:
        print(f"API (StyleTone): Analyzing style/tone for lang '{language}', expected '{expected_tone}' in: '{text[:50]}...'")
        tone_match_score = 0.92
        if expected_tone == "formal" and "buddy" in text.lower(): tone_match_score = 0.6
        return {"tone_match_score": tone_match_score, "style_consistency": 0.85, "language": language}

class TerminologyDatabaseAPI:
    def __init__(self, error_rate: float = 0.1):
        self.error_rate = error_rate
        self.glossaries = {
            "EN_CA_FR_CA": {"eh": "n'est-ce pas", "dépanneur": "convenience store", "poutine": "poutine", "toque": "tuque"},
            "FR_CA_EN_CA": {"n'est-ce pas": "eh / right", "dépanneur": "convenience store", "poutine": "poutine", "tuque": "toque"}
        }
        self.term_bases = {
            "proj_alpha": {
                "EN_CA": {"application": "software program", "framework": "system architecture", "computer": "personal computer"},
                "FR_CA": {"application": "logiciel", "framework": "cadre d'architecture", "computer": "ordinateur"}
            }
        }
        # Universal names that should ideally remain untranslated or handled specific way
        self.universal_names = {
            "poutine", "igloo", "wi-fi", "tsunami", "hockey", "parking", "stop",
            "jeans", "sandwich", "internet", "email", "cpu", "usb", "ceo", "cto",
            "québec" # Proper noun example
        }

    def verify_terms(self, text: str, language: str, project_id: str, task_id: str) -> Dict[str, Any]:
        print(f"API (TerminologyDB): Verifying terms for lang '{language}', project '{project_id}', task '{task_id}' in: '{text[:50]}...'")

        if project_id == "proj_beta_nonexistent" and random.random() < self.error_rate * 2:
            print(f"API (TerminologyDB): SIMULATING ERROR: APIResourceNotFoundError for project {project_id}")
            raise APIResourceNotFoundError(f"Simulated: Termbase for project '{project_id}' not found.")

        if random.random() < self.error_rate:
            error_type = random.choice([APITimeoutError, APIServiceUnavailableError])
            print(f"API (TerminologyDB): SIMULATING ERROR: {error_type.__name__}")
            raise error_type(f"Simulated {error_type.__name__} in TerminologyDatabaseAPI")

        issues: List[Dict[str, Any]] = [] # Changed from suggestions to issues for consistency

        # 1. Check project-specific term base
        # For FR_CA target: if an EN_CA term_base key is found, it's an issue (should have been translated to FR_CA value)
        # For EN_CA target: if an FR_CA term_base key is found, it's an issue (should have been translated to EN_CA value)
        source_lang_for_term_base_check = "EN_CA" if language == "FR_CA" else "FR_CA"

        project_term_base_for_source_lang = self.term_bases.get(project_id, {}).get(source_lang_for_term_base_check, {})
        project_term_base_for_target_lang = self.term_bases.get(project_id, {}).get(language, {})

        if project_term_base_for_source_lang:
            for source_term, expected_source_form in project_term_base_for_source_lang.items(): # e.g. source_term="computer", expected_source_form="personal computer"
                # Find the corresponding target term for this source_term
                # This requires finding which FR_CA key corresponds to the EN_CA value "computer" or vice versa
                # This is complex. Simplified: if source_term (e.g. "computer") is in FR text, it's an error.

                # Simplified: if the English term_base key is found in a French text.
                if language == "FR_CA" and re.search(r"\b" + re.escape(source_term) + r"\b", text, flags=re.IGNORECASE):
                    expected_translation = project_term_base_for_target_lang.get(source_term) # Find translation for this key
                    if not expected_translation: # If source_term itself is not a key in target_lang term_base, look up via EN_CA value
                         # This part of logic is tricky without a bilingual map of the term_base.
                         # Assume for now term_key is consistent across languages for lookup.
                         pass # For now, this case might not be perfectly handled.

                    if expected_translation and not re.search(r"\b" + re.escape(expected_translation) + r"\b", text, flags=re.IGNORECASE):
                         issues.append({
                            "type": "untranslated_term",
                            "term": source_term,
                            "expected": expected_translation,
                            "reason": f"Term '{source_term}' from project glossary should have been translated to '{expected_translation}'.",
                            "severity": "high"
                        })
        else:
            if project_id in self.term_bases:
                 print(f"API (TerminologyDB): No {source_lang_for_term_base_check} terms defined for project '{project_id}'.")
            else:
                 print(f"API (TerminologyDB): No specific termbase found for project '{project_id}'.")


        # 2. Universal Name Handling (Simplified)
        # If text is FR_CA, universal names are generally OK if present in original form.
        # If text is EN_CA, they are also generally OK.
        # The main point is NOT to flag them as "untranslated" if they come from the source.
        # This logic is more about *not adding* an issue if a universal name is found.
        # If a universal name *should have been* translated by specific project guideline, that's a term_base rule.

        # Let's refine: if a universal term is found, and it's *not* in the term_base for forced translation, it's OK.
        # If it *is* in term_base with a specific translation, that rule takes precedence.
        words_in_text = set(re.findall(r"\b\w+\b", text.lower()))
        for uni_name in self.universal_names:
            if uni_name in words_in_text:
                # Check if this universal name was supposed to be translated by term_base
                is_in_term_base_as_source = project_term_base_for_source_lang.get(uni_name)
                if not is_in_term_base_as_source: # If not in term_base with a specific translation rule
                    issues.append({
                        "type": "universal_name_present",
                        "term": uni_name,
                        "status": "ok_acknowledged", # Acknowledged its presence, not an error.
                        "details": "Universal name correctly present in its original form.",
                        "severity": "info"
                    })

        terms_ok = not any(issue.get("severity") == "high" for issue in issues)

        return {"terms_ok": terms_ok, "issues_found": issues, "checked_against": f"project_{project_id}_{language}_terms"}

    def get_glossary(self, language_pair: str) -> Dict[str, str]:
        print(f"API (TerminologyDB): Retrieving glossary for '{language_pair}'.")
        if random.random() < self.error_rate / 2:
            print(f"API (TerminologyDB): SIMULATING ERROR: APIServiceUnavailableError for get_glossary")
            raise APIServiceUnavailableError("Simulated service unavailability for get_glossary")
        return self.glossaries.get(language_pair, {})
