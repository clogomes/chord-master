"""Data model for Composition Studio."""
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from core.chords import CHORD_TYPES
from audio.backing_tracks import BACKING_TRACK_LIBRARY, RhythmPattern


@dataclass
class ChordEvent:
    root: str            # "C", "Bb", "F#", ...
    chord_type: str      # key of CHORD_TYPES ("major", "minor", "dom7", etc.)
    start_beat: float    # 0.0, 1.0, 2.5, ...
    duration_beats: float = 1.0
    instrument: str = "piano"  # "piano" | "guitar"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "root": self.root,
            "chord_type": self.chord_type,
            "start_beat": float(self.start_beat),
            "duration_beats": float(self.duration_beats),
            "instrument": self.instrument,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ChordEvent":
        return cls(
            root=str(data.get("root", "C")),
            chord_type=str(data.get("chord_type", "major")),
            start_beat=float(data.get("start_beat", 0.0)),
            duration_beats=float(data.get("duration_beats", 1.0)),
            instrument=str(data.get("instrument", "piano")),
        )


@dataclass
class RhythmTrack:
    steps_per_bar: int = 16
    grid: List[List[str]] = field(default_factory=list)   # Same shape as RhythmPattern.grid
    volume: float = 0.8
    muted: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return {
            "steps_per_bar": int(self.steps_per_bar),
            "grid": [list(step) for step in self.grid],
            "volume": float(self.volume),
            "muted": bool(self.muted),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "RhythmTrack":
        raw_grid = data.get("grid", [])
        clean_grid = [[str(inst) for inst in step] for step in raw_grid]
        return cls(
            steps_per_bar=int(data.get("steps_per_bar", 16)),
            grid=clean_grid,
            volume=float(data.get("volume", 0.8)),
            muted=bool(data.get("muted", False)),
        )

    @classmethod
    def from_pattern(cls, pattern: RhythmPattern, volume: float = 0.8, muted: bool = False) -> "RhythmTrack":
        """Adapter that converts a RhythmPattern into an editable RhythmTrack."""
        return cls(
            steps_per_bar=pattern.steps_per_bar,
            grid=[list(step) for step in pattern.grid],
            volume=volume,
            muted=muted,
        )


@dataclass
class Composition:
    id: str
    title: str
    bpm: int = 100
    time_signature: str = "4/4"
    bars: int = 4
    rhythm: RhythmTrack = field(default_factory=RhythmTrack)
    chords: List[ChordEvent] = field(default_factory=list)
    master_volume: float = 0.8
    schema_version: int = 1

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "title": self.title,
            "bpm": int(self.bpm),
            "time_signature": str(self.time_signature),
            "bars": int(self.bars),
            "rhythm": self.rhythm.to_dict() if self.rhythm else RhythmTrack().to_dict(),
            "chords": [c.to_dict() for c in self.chords],
            "master_volume": float(self.master_volume),
            "schema_version": int(self.schema_version),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Composition":
        rhythm_data = data.get("rhythm", {})
        rhythm = RhythmTrack.from_dict(rhythm_data) if isinstance(rhythm_data, dict) else RhythmTrack()
        
        chords_data = data.get("chords", [])
        chords = []
        if isinstance(chords_data, list):
            for c_item in chords_data:
                if isinstance(c_item, dict):
                    chords.append(ChordEvent.from_dict(c_item))

        return cls(
            id=str(data.get("id", "comp_default")),
            title=str(data.get("title", "Nova Composição")),
            bpm=int(data.get("bpm", 100)),
            time_signature=str(data.get("time_signature", "4/4")),
            bars=int(data.get("bars", 4)),
            rhythm=rhythm,
            chords=chords,
            master_volume=float(data.get("master_volume", 0.8)),
            schema_version=int(data.get("schema_version", 1)),
        )
