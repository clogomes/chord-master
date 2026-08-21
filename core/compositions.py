"""Storage and template management for user compositions."""
import json
import os
from typing import Dict, List, Optional
from core.composition import Composition, ChordEvent, RhythmTrack
from audio.backing_tracks import BACKING_TRACK_LIBRARY, RhythmPattern

USER_COMPOSITIONS_FILE = "user_compositions.json"


def get_template_composition(pattern_id: str = "rock_basic") -> Composition:
    """
    Creates a new Composition pre-loaded with a template rhythm pattern from the library.
    """
    pattern = BACKING_TRACK_LIBRARY.get(pattern_id) or BACKING_TRACK_LIBRARY.get("rock_basic")
    rhythm = RhythmTrack.from_pattern(pattern, bars=4) if pattern else RhythmTrack()
    title = f"Composição ({pattern.name_pt})" if pattern else "Nova Composição"
    ts = pattern.time_signature if pattern else "4/4"
    return Composition(
        id=f"comp_{pattern_id}",
        title=title,
        bpm=100,
        time_signature=ts,
        bars=4,
        rhythm=rhythm,
        chords=[],
        notes=[],
        master_volume=0.8,
        schema_version=2,
    )


def save_user_composition(composition: Composition, filepath: str = USER_COMPOSITIONS_FILE):
    """
    Saves or updates a composition in the JSON storage file.
    """
    compositions = load_user_compositions(filepath=filepath)
    # Replace existing by ID or append
    updated = False
    for i, c in enumerate(compositions):
        if c.id == composition.id:
            compositions[i] = composition
            updated = True
            break
    if not updated:
        compositions.append(composition)

    data = [c.to_dict() for c in compositions]
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def load_user_compositions(filepath: str = USER_COMPOSITIONS_FILE) -> List[Composition]:
    """
    Loads all user compositions from JSON storage file.
    Gracefully handles missing files, malformed data, and schema defaults.
    """
    if not os.path.exists(filepath):
        return []

    try:
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception:
        return []

    if not isinstance(data, list):
        return []

    results = []
    for item in data:
        if isinstance(item, dict):
            try:
                results.append(Composition.from_dict(item))
            except Exception:
                pass
    return results


def delete_user_composition(composition_id: str, filepath: str = USER_COMPOSITIONS_FILE) -> bool:
    """
    Deletes a composition by ID. Returns True if deleted, False otherwise.
    """
    compositions = load_user_compositions(filepath=filepath)
    initial_len = len(compositions)
    compositions = [c for c in compositions if c.id != composition_id]
    if len(compositions) < initial_len:
        data = [c.to_dict() for c in compositions]
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return True
    return False
