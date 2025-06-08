# This file stores original texts to be translated for the advanced bureau.

ORIGINAL_TEXTS = {
    "text_001_en_ca": "The early bird gets the worm, eh? My car needs a new bumper. We should head to the lake before it gets too crowded. Let's check the CPU usage on the internet.",
    "text_002_en_ca": "I'm going to the dépanneur to grab a poutine and a few pops for the cottage this weekend. Make sure to pack your toque! It's going to be a fun party.",
    "text_003_en_ca": "For this project (proj_alpha), the application framework and the main computer software needs to be robust. Please check the colour-coded documentation for 'Style Guide A'.",
    "text_004_fr_ca": "Salut mon chum! On va-tu checker le match des Glorieux à soir ou t'es game pour une game de ringuette? C'est le fun de watcher le hockey.",
    "text_005_fr_ca": "J'ai besoin d'un nouveau skidoo pour l'hiver qui s'en vient. Peut-être un modèle avec une meilleure chenille pour la poudreuse. On prendra le dîner plus tard.",
    "text_006_fr_ca": "Le client veut une interface utilisateur conviviale pour son logiciel (proj_alpha). Assurez-vous que la terminologie est conforme au glossaire. C'est une application critique.",
    "text_007_en_ca": "My buddy from out west said, 'That's a real gitchy setup you got there!' but I think my hoser-style solution for the internet parking validation is pretty clever, actually.",
    "text_008_fr_ca": "Attention à ne pas commettre un anglicisme flagrant. Le rapport doit être impeccable. N'oublie pas de vérifier chaque détail, n'est-ce pas? Ce weekend, c'est la fin de semaine."
}

# Changes made:
# - text_001_en_ca: Added "car needs a new bumper" (to trigger 'voiture' vs 'char' and 'bumper' anglicism). Added "CPU" and "internet" (universal names) and "check" (for "checker" anglicism).
# - text_002_en_ca: Added "fun party" to ensure "le fun" and "party" anglicisms can be triggered.
# - text_003_en_ca: Added "(proj_alpha)" to explicitly link to termbase, and "computer software" to ensure "computer" and "application" are present for TerminologyChecker test.
# - text_004_fr_ca: Added "C'est le fun de watcher le hockey." to include more FR anglicisms for EN translation context.
# - text_005_fr_ca: Added "On prendra le dîner plus tard." to test France-French term detection.
# - text_006_fr_ca: Added "(proj_alpha)" to link to termbase.
# - text_007_en_ca: Added "internet parking" (universal names).
# - text_008_fr_ca: Added "Ce weekend" to test France-French term.

# Notes on some terms:
# EN_CA:
# "eh?" - Canadian interjection
# "dépanneur" - Quebec French term for convenience store, often used in English in Quebec/nearby regions.
# "poutine" - Quebec dish
# "pops" - common Canadian term for sodas/soft drinks
# "cottage" - common Canadian term for a summer/vacation home
# "toque" - Canadian term for a winter hat (tuque in French)
# "colour" - Canadian/British spelling
# "application framework" - technical term
# "buddy" - informal
# "gitchy/gotch" - (prairies slang for underwear, contextually can mean makeshift/poorly made, depending on region) - very informal, regional
# "hoser" - Canadian slang, can be pejorative or endearing depending on context
# "bumper" - common term, but API checks for it as anglicism in FR_CA if directly used.

# FR_CA:
# "mon chum" - my friend (Quebec)
# "On va-tu" - common Quebecois informal future tense construction ("are we going to...")
# "checker" - to check (anglicism, common in Quebec French)
# "Glorieux" - nickname for Montreal Canadiens NHL team
# "t'es game" - are you game/up for it (anglicism)
# "ringuette" - ringette (sport)
# "skidoo" - brand name, often used generically for snowmobile
# "chenille" - track (of a snowmobile)
# "poudreuse" - powder snow
# "conviviale" - user-friendly
# "logiciel" - software
# "anglicisme" - anglicism
# "n'est-ce pas?" - common phrase, can be similar to "eh?" or "right?"
# "char" - car (Quebec, informal)
# "souper" - supper/dinner (Quebec, evening meal)
# "déjeuner" - lunch (Quebec, midday meal) / breakfast (France)
# "fin de semaine" - weekend (Quebec)
