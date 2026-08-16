"""Internationalization (i18n) module for PT/EN language localization and UI dictionary."""
import json
import os
from typing import Callable, Dict, List, Optional

_CURRENT_LANGUAGE = "pt"
_SETTINGS_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "app_settings.json")

_LISTENERS: List[Callable[[str], None]] = []

UI_STRINGS: Dict[str, Dict[str, str]] = {
    "pt": {
        # App / Navigation
        "app_title": "ChordMaster",
        "app_subtitle": "Estúdio & Academia Musical",
        "nav_main_menu": "🏠 Menu Principal",
        "nav_theory": "📖 Teoria Musical (16 Cap)",
        "nav_practice_song": "🎶 Tocar Repertório",
        "nav_practice_scales": "🎼 Prática de Escalas",
        "nav_lamire": "🎙️ Lamiré & Afinador",
        "nav_practice_instrument": "🎯 Prática c/ Microfone",
        "nav_practice_ear": "🎧 Treino Auditivo",
        "nav_practice_staff": "🎼 Leitura de Pauta",
        "nav_glossary": "📚 Glossário Musical",
        "nav_stats": "📊 Estatísticas & Alunos",
        "glossary_title": "Glossário Musical Interativo",
        "glossary_search_placeholder": "Pesquisar termo, fórmula, conceito ou instrumento...",
        "glossary_empty_search": "Nenhum termo encontrado.",
        "glossary_not_found": "Termo não encontrado no glossário.",
        "btn_hear_concept": "🔊 Ouvir Conceito Sonoro",
        "lbl_category": "Categoria:",
        "theme_label": "Tema Visual:",
        "language_label": "Idioma / Language:",
        "reset_progress": "↺ Reiniciar Progresso",
        "confirm_reset_title": "Confirmar Reinício",
        "confirm_reset_msg": "Tens a certeza de que desejas reiniciar todo o progresso do utilizador ativo?",

        # Common Actions
        "btn_back": "← Voltar ao Menu",
        "btn_play": "▶ Ouvir",
        "btn_stop": "⏹ Parar",
        "btn_restart": "↺ Reiniciar",
        "btn_next": "Próxima Pergunta →",
        "btn_export": "📥 Exportar Progresso",
        "btn_save": "Guardar",
        "btn_cancel": "Cancelar",
        "btn_close": "Fechar",
        "btn_switch_user": "Trocar de Perfil",
        "btn_new_user": "Novo Aluno",
        "btn_start_mic": "🎙️ Ativar Microfone",
        "btn_stop_mic": "⏹ Parar Microfone",
        "btn_import_midi": "📂 Importar Música (.mid)",

        # Main Menu & Dashboards
        "menu_welcome": "Bem-vindo à Academia ChordMaster",
        "menu_summary": "Escolhe um módulo para iniciar o teu treino diário.",
        "level_title": "Nível",
        "xp_title": "XP Total",
        "streak_title": "Dias Seguidos (Streak)",
        "accuracy_title": "Precisão Geral",
        "lessons_done": "Lições Concluídas",
        "weak_areas_title": "Áreas a Melhorar",

        # Studio / Instruments
        "instrument_label": "Instrumento:",
        "piano": "Piano",
        "guitar": "Viola / Guitarra",
        "both": "Ambos em Simultâneo",
        "tempo_label": "Tempo (BPM):",
        "speed_ramp": "⚡ Rampa de Tempo Automática",
        "backing_track": "🥁 Acompanhamento Rítmico",
        "metronome": "⏱️ Metrónomo",
        "root_note": "Tónica:",
        "scale_type": "Escala / Modo:",
        "direction": "Sentido:",
        "dir_asc_desc": "Ascendente & Descendente",
        "dir_asc": "Apenas Ascendente",
        "dir_desc": "Apenas Descendente",

        # Theory Screen
        "theory_title": "📖 Academia de Teoria Musical",
        "theory_course_chapters": "Capítulos do Curso",
        "theory_mark_completed": "✓ Marcar Lição como Concluída (+50 XP)",
        "theory_lesson_completed": "✅ Lição Concluída (+50 XP)",
        "theory_piano_tab": "🎹 No Piano",
        "theory_guitar_tab": "🎸 Na Viola / Guitarra",
        "theory_quiz_tab": "❓ Testar Conhecimentos",

        # Tuner & Pitch
        "tuner_title": "🎙️ Lamiré & Afinador Cromático",
        "tuner_in_tune": "✓ AFINADO (No Ponto Perfeito!)",
        "tuner_too_low": "▲ Muito Grave — Estica a corda",
        "tuner_too_high": "▼ Muito Agudo — Afrouxa a corda",
        "tuner_cents": "cents",
        "tuner_ref_pitch": "Lá Central (A4 - 440 Hz)",

        # Ear Training & Quizzes
        "ear_training_title": "🎧 Treino Auditivo & Solfejo",
        "staff_reading_title": "🎼 Leitura de Pauta",
        "adaptive_mode": "🧠 Modo Adaptativo (foca pontos fracos)",
        "difficulty": "Dificuldade:",
        "diff_beginner": "Iniciante",
        "diff_intermediate": "Intermédio",
        "diff_advanced": "Avançado",
        "clef_label": "Clave:",
        "clef_treble": "Clave de Sol (𝄞)",
        "clef_bass": "Clave de Fá (𝄢)",
        "include_accidentals": "Incluir Acidentes (♯/♭)",

        # Stats & Profiles
        "stats_title": "📊 Estatísticas & Análise de Progresso",
        "achievements_title": "🏆 Medalhas & Conquistas",
        "profiles_title": "👥 Gestão de Alunos & Utilizadores",
    },
    "en": {
        # App / Navigation
        "app_title": "ChordMaster",
        "app_subtitle": "Music Studio & Academy",
        "nav_main_menu": "🏠 Main Menu",
        "nav_theory": "📖 Music Theory (16 Chaps)",
        "nav_practice_song": "🎶 Song Play-Along",
        "nav_practice_scales": "🎼 Scale Practice",
        "nav_lamire": "🎙️ Pitch Pipe & Tuner",
        "nav_practice_instrument": "🎯 Microphone Practice",
        "nav_practice_ear": "🎧 Ear Training",
        "nav_practice_staff": "🎼 Sight Reading",
        "nav_glossary": "📚 Musical Glossary",
        "nav_stats": "📊 Stats & Students",
        "glossary_title": "Interactive Musical Glossary",
        "glossary_search_placeholder": "Search term, formula, concept or instrument...",
        "glossary_empty_search": "No terms found.",
        "glossary_not_found": "Term not found in glossary.",
        "btn_hear_concept": "🔊 Play Sound Concept",
        "lbl_category": "Category:",
        "theme_label": "Visual Theme:",
        "language_label": "Language / Idioma:",
        "reset_progress": "↺ Reset Progress",
        "confirm_reset_title": "Confirm Reset",
        "confirm_reset_msg": "Are you sure you want to reset all progress for the active student?",

        # Common Actions
        "btn_back": "← Back to Menu",
        "btn_play": "▶ Play",
        "btn_stop": "⏹ Stop",
        "btn_restart": "↺ Restart",
        "btn_next": "Next Question →",
        "btn_export": "📥 Export Progress",
        "btn_save": "Save",
        "btn_cancel": "Cancel",
        "btn_close": "Close",
        "btn_switch_user": "Switch Profile",
        "btn_new_user": "New Student",
        "btn_start_mic": "🎙️ Start Microphone",
        "btn_stop_mic": "⏹ Stop Microphone",
        "btn_import_midi": "📂 Import Song (.mid)",

        # Main Menu & Dashboards
        "menu_welcome": "Welcome to ChordMaster Academy",
        "menu_summary": "Choose a module below to start your daily practice.",
        "level_title": "Level",
        "xp_title": "Total XP",
        "streak_title": "Daily Streak",
        "accuracy_title": "Overall Accuracy",
        "lessons_done": "Completed Lessons",
        "weak_areas_title": "Areas to Improve",

        # Studio / Instruments
        "instrument_label": "Instrument:",
        "piano": "Piano",
        "guitar": "Guitar / Viola",
        "both": "Both Instruments",
        "tempo_label": "Tempo (BPM):",
        "speed_ramp": "⚡ Auto Speed Ramp",
        "backing_track": "🥁 Rhythm Backing Track",
        "metronome": "⏱️ Metronome",
        "root_note": "Root Note:",
        "scale_type": "Scale / Mode:",
        "direction": "Direction:",
        "dir_asc_desc": "Ascending & Descending",
        "dir_asc": "Ascending Only",
        "dir_desc": "Descending Only",

        # Theory Screen
        "theory_title": "📖 Music Theory Academy",
        "theory_course_chapters": "Course Chapters",
        "theory_mark_completed": "✓ Mark Lesson as Completed (+50 XP)",
        "theory_lesson_completed": "✅ Lesson Completed (+50 XP)",
        "theory_piano_tab": "🎹 On Piano",
        "theory_guitar_tab": "🎸 On Guitar",
        "theory_quiz_tab": "❓ Test Knowledge",

        # Tuner & Pitch
        "tuner_title": "🎙️ Pitch Pipe & Chromatic Tuner",
        "tuner_in_tune": "✓ IN TUNE (Spot On!)",
        "tuner_too_low": "▲ Too Flat — Tighten string",
        "tuner_too_high": "▼ Too Sharp — Loosen string",
        "tuner_cents": "cents",
        "tuner_ref_pitch": "Concert Pitch (A4 - 440 Hz)",

        # Ear Training & Quizzes
        "ear_training_title": "🎧 Ear Training & Solfege",
        "staff_reading_title": "🎼 Sight Reading",
        "adaptive_mode": "🧠 Adaptive Mode (focus weak spots)",
        "difficulty": "Difficulty:",
        "diff_beginner": "Beginner",
        "diff_intermediate": "Intermediate",
        "diff_advanced": "Advanced",
        "clef_label": "Clef:",
        "clef_treble": "Treble Clef (𝄞)",
        "clef_bass": "Bass Clef (𝄢)",
        "include_accidentals": "Include Accidentals (♯/♭)",

        # Stats & Profiles
        "stats_title": "📊 Statistics & Progress Analysis",
        "achievements_title": "🏆 Badges & Achievements",
        "profiles_title": "👥 Student & Profile Management",
    }
}


def _load_persisted_language():
    global _CURRENT_LANGUAGE
    if os.path.exists(_SETTINGS_FILE):
        try:
            with open(_SETTINGS_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                lang = data.get("language", "pt")
                if lang in UI_STRINGS:
                    _CURRENT_LANGUAGE = lang
        except Exception:
            _CURRENT_LANGUAGE = "pt"


def _save_persisted_language():
    try:
        os.makedirs(os.path.dirname(_SETTINGS_FILE), exist_ok=True)
        data = {}
        if os.path.exists(_SETTINGS_FILE):
            try:
                with open(_SETTINGS_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
            except Exception:
                data = {}
        data["language"] = _CURRENT_LANGUAGE
        with open(_SETTINGS_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
    except Exception:
        pass


def get_language() -> str:
    """Returns the current active language ('pt' or 'en')."""
    return _CURRENT_LANGUAGE


def set_language(lang: str) -> None:
    """Sets the active language ('pt' or 'en') and notifies registered listeners."""
    global _CURRENT_LANGUAGE
    if lang in UI_STRINGS and lang != _CURRENT_LANGUAGE:
        _CURRENT_LANGUAGE = lang
        _save_persisted_language()
        for cb in _LISTENERS:
            try:
                cb(lang)
            except Exception:
                pass


def toggle_language() -> str:
    """Toggles language between 'pt' and 'en' and returns the newly active language."""
    new_lang = "en" if _CURRENT_LANGUAGE == "pt" else "pt"
    set_language(new_lang)
    return new_lang


def t(key: str, default: Optional[str] = None) -> str:
    """Retrieves localized text for the given translation key."""
    lang_dict = UI_STRINGS.get(_CURRENT_LANGUAGE, UI_STRINGS["pt"])
    if key in lang_dict:
        return lang_dict[key]
    # Fallback to pt dictionary
    if key in UI_STRINGS["pt"]:
        return UI_STRINGS["pt"][key]
    return default if default is not None else key


def register_language_listener(callback: Callable[[str], None]) -> None:
    """Registers a callback to be invoked whenever language is switched."""
    if callback not in _LISTENERS:
        _LISTENERS.append(callback)


# Initialize persisted state on import
_load_persisted_language()
