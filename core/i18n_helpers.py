"""Helper functions for music theory entity localization (Notes, Chords, Scales, Intervals)."""
from typing import Any
from gui.i18n import get_language


def localized_note_name(note: Any) -> str:
    """Returns solfege name ('Dó', 'Ré') in PT and note pitch ('C', 'D') in EN."""
    if note is None:
        return ""
    lang = get_language()
    if lang == "pt":
        return getattr(note, "name_pt", getattr(note, "pitch", str(note)))
    return getattr(note, "pitch", getattr(note, "name_pt", str(note)))


def localized_chord_name(chord_def: Any) -> str:
    """Returns chord definition name localized according to current language."""
    if chord_def is None:
        return ""
    lang = get_language()
    if lang == "pt":
        return getattr(chord_def, "name_pt", getattr(chord_def, "name_en", str(chord_def)))
    return getattr(chord_def, "name_en", getattr(chord_def, "name_pt", str(chord_def)))


def localized_scale_name(scale_def: Any) -> str:
    """Returns scale definition name localized according to current language."""
    if scale_def is None:
        return ""
    lang = get_language()
    if lang == "pt":
        return getattr(scale_def, "name_pt", getattr(scale_def, "name_en", str(scale_def)))
    return getattr(scale_def, "name_en", getattr(scale_def, "name_pt", str(scale_def)))


def localized_interval_name(interval: Any) -> str:
    """Returns interval name localized according to current language."""
    if interval is None:
        return ""
    lang = get_language()
    if lang == "pt":
        return getattr(interval, "name_pt", getattr(interval, "name_en", str(interval)))
    return getattr(interval, "name_en", getattr(interval, "name_pt", str(interval)))
