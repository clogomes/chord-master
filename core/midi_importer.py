"""Standard MIDI File (.mid/.midi) Parser and Song Importer in pure Python."""
import json
import os
import struct
from typing import List, Optional, Tuple
from core.notes import Note
from core.songs import Song, SongNote, SONG_LIBRARY
from core.guitar import find_note_positions, assign_guitar_coordinates
from core.fingering import assign_piano_fingerings


USER_SONGS_FILE = "user_songs.json"


def _read_vlq(data: bytes, offset: int) -> Tuple[int, int]:
    """Reads a variable-length quantity from MIDI byte stream. Returns (value, new_offset)."""
    val = 0
    while offset < len(data):
        b = data[offset]
        offset += 1
        val = (val << 7) | (b & 0x7F)
        if not (b & 0x80):
            break
    return val, offset


class MidiParser:
    """Lightweight pure-Python Standard MIDI File (SMF 0 & 1) parser."""

    def __init__(self, data: bytes):
        self.data = data
        self.format: int = 0
        self.num_tracks: int = 0
        self.division: int = 480  # ticks per quarter note
        self.tracks_raw: List[bytes] = []
        self._parse_header()

    def _parse_header(self):
        if len(self.data) < 14 or self.data[:4] != b"MThd":
            raise ValueError("Ficheiro MIDI inválido: Cabeçalho 'MThd' não encontrado.")
        header_len = struct.unpack(">I", self.data[4:8])[0]
        self.format, self.num_tracks, self.division = struct.unpack(">HHH", self.data[8:14])

        # Find track chunks
        offset = 8 + header_len
        while offset + 8 <= len(self.data):
            chunk_id = self.data[offset:offset+4]
            chunk_len = struct.unpack(">I", self.data[offset+4:offset+8])[0]
            offset += 8
            if chunk_id == b"MTrk":
                self.tracks_raw.append(self.data[offset:offset+chunk_len])
            offset += chunk_len

    def extract_monophonic_melody(self, track_index: int = 0) -> Tuple[List[Tuple[int, float, float]], int]:
        """
        Extracts note events from the given track.
        Returns:
            (List of (midi_pitch, start_beat, duration_beats), bpm)
        """
        if not self.tracks_raw:
            return [], 120

        t_idx = min(track_index, len(self.tracks_raw) - 1)
        track_data = self.tracks_raw[t_idx]

        offset = 0
        current_tick = 0
        running_status = 0
        active_notes = {}  # pitch -> start_tick
        finished_notes = []  # (pitch, start_tick, duration_ticks)
        bpm = 120

        while offset < len(track_data):
            delta_tick, offset = _read_vlq(track_data, offset)
            current_tick += delta_tick
            if offset >= len(track_data):
                break

            status = track_data[offset]
            if status >= 0x80:
                running_status = status
                offset += 1
            else:
                status = running_status

            msg_type = status & 0xF0

            if status == 0xFF:  # Meta Event
                if offset >= len(track_data):
                    break
                meta_type = track_data[offset]
                offset += 1
                meta_len, offset = _read_vlq(track_data, offset)
                meta_payload = track_data[offset:offset+meta_len]
                offset += meta_len

                if meta_type == 0x51 and meta_len == 3:  # Set Tempo
                    micros_per_quarter = struct.unpack(">I", b"\x00" + meta_payload)[0]
                    if micros_per_quarter > 0:
                        bpm = int(round(60_000_000 / micros_per_quarter))
                elif meta_type == 0x2F:  # End of Track
                    break
            elif status == 0xF0 or status == 0xF7:  # SysEx
                sysex_len, offset = _read_vlq(track_data, offset)
                offset += sysex_len
            elif msg_type == 0x90:  # Note On
                pitch = track_data[offset]
                vel = track_data[offset+1]
                offset += 2
                if vel > 0:
                    active_notes[pitch] = current_tick
                else:
                    if pitch in active_notes:
                        start_t = active_notes.pop(pitch)
                        finished_notes.append((pitch, start_t, max(1, current_tick - start_t)))
            elif msg_type == 0x80:  # Note Off
                pitch = track_data[offset]
                offset += 2
                if pitch in active_notes:
                    start_t = active_notes.pop(pitch)
                    finished_notes.append((pitch, start_t, max(1, current_tick - start_t)))
            elif msg_type in (0xA0, 0xB0, 0xE0):  # 2 data bytes
                offset += 2
            elif msg_type in (0xC0, 0xD0):  # 1 data byte
                offset += 1

        # Close any lingering active notes
        for pitch, start_t in list(active_notes.items()):
            finished_notes.append((pitch, start_t, max(1, current_tick - start_t)))

        # Sort by start_tick
        finished_notes.sort(key=lambda x: x[1])

        # Convert ticks to beats
        div = float(self.division if self.division > 0 else 480)
        events = []
        for pitch, s_tick, dur_tick in finished_notes:
            s_beat = s_tick / div
            dur_beat = max(0.25, round((dur_tick / div) * 4) / 4)  # quantize to 16th note
            events.append((pitch, s_beat, dur_beat))

        return events, bpm


def _assign_guitar_coordinates(notes: List[Note]) -> List[Tuple[int, int]]:
    """Assigns ergonomic guitar string and fret coordinates minimizing hand position shifts."""
    return assign_guitar_coordinates(notes)


def _assign_piano_fingerings(notes: List[Note]) -> List[int]:
    """Assigns standard 5-finger melodic heuristics for right hand."""
    return assign_piano_fingerings(notes)


def import_midi_as_song(
    filepath: str,
    title: Optional[str] = None,
    composer: Optional[str] = None,
    difficulty: str = "Iniciante",
    track_index: int = 0,
) -> Song:
    """Parses a .mid file and converts it into a full ChordMaster Song."""
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Ficheiro MIDI não encontrado: {filepath}")

    with open(filepath, "rb") as f:
        midi_bytes = f.read()

    parser = MidiParser(midi_bytes)
    events, bpm = parser.extract_monophonic_melody(track_index)

    if not events:
        raise ValueError("O ficheiro MIDI não contém notas reproduzíveis na pista selecionada.")

    base_name = os.path.splitext(os.path.basename(filepath))[0].replace("_", " ").title()
    song_title = title or base_name or "Música Importada"
    song_id = "user_" + "".join(c.lower() for c in song_title if c.isalnum())[:20]

    # Convert to Note objects
    note_objs = []
    durations = []
    for pitch, _, dur in events:
        clamped_pitch = max(40, min(84, pitch))  # E2 to C6
        note_objs.append(Note.from_midi(clamped_pitch))
        durations.append(dur)

    # Assign guitar and piano ergonomics
    guitar_pos = _assign_guitar_coordinates(note_objs)
    piano_fingers = _assign_piano_fingerings(note_objs)

    song_notes = []
    for i, n in enumerate(note_objs):
        g_str, g_fret = guitar_pos[i]
        p_finger = piano_fingers[i]
        song_notes.append(
            SongNote(
                note=n,
                duration_beats=durations[i],
                piano_finger=p_finger,
                piano_hand="direita",
                guitar_string=g_str,
                guitar_fret=g_fret,
                lyric_syllable=n.name_pt,
            )
        )

    return Song(
        id=song_id,
        title=f"📁 {song_title}",
        composer=composer or "Ficheiro MIDI Importado",
        difficulty=difficulty,
        bpm=bpm or 100,
        clef="treble",
        description=f"Partitura importada via MIDI ({len(song_notes)} notas, {bpm} BPM).",
        notes=song_notes,
    )


def save_user_song(song: Song, filepath: str = USER_SONGS_FILE):
    """Persists an imported user song to JSON."""
    user_songs_data = []
    if os.path.exists(filepath):
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                user_songs_data = json.load(f)
        except Exception:
            user_songs_data = []

    # Remove if duplicate ID
    user_songs_data = [s for s in user_songs_data if s.get("id") != song.id]

    # Serialize Song
    song_dict = {
        "id": song.id,
        "title": song.title,
        "composer": song.composer,
        "difficulty": song.difficulty,
        "bpm": song.bpm,
        "clef": song.clef,
        "description": song.description,
        "notes": [
            {
                "pitch": sn.note.pitch_with_octave,
                "duration_beats": sn.duration_beats,
                "piano_finger": sn.piano_finger,
                "piano_hand": sn.piano_hand,
                "guitar_string": sn.guitar_string,
                "guitar_fret": sn.guitar_fret,
                "lyric_syllable": sn.lyric_syllable,
            }
            for sn in song.notes
        ],
    }
    user_songs_data.append(song_dict)

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(user_songs_data, f, indent=2, ensure_ascii=False)


def load_user_songs(filepath: str = USER_SONGS_FILE) -> List[Song]:
    """Loads persisted user songs from JSON into Song objects."""
    if not os.path.exists(filepath):
        return []

    try:
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception:
        return []

    loaded_songs = []
    for item in data:
        song_notes = []
        for nd in item.get("notes", []):
            song_notes.append(
                SongNote(
                    note=Note(nd["pitch"]),
                    duration_beats=float(nd.get("duration_beats", 1.0)),
                    piano_finger=nd.get("piano_finger"),
                    piano_hand=nd.get("piano_hand", "direita"),
                    guitar_string=nd.get("guitar_string"),
                    guitar_fret=nd.get("guitar_fret"),
                    lyric_syllable=nd.get("lyric_syllable"),
                )
            )
        song = Song(
            id=item["id"],
            title=item["title"],
            composer=item.get("composer", "Desconhecido"),
            difficulty=item.get("difficulty", "Iniciante"),
            bpm=item.get("bpm", 100),
            clef=item.get("clef", "treble"),
            description=item.get("description", ""),
            notes=song_notes,
        )
        loaded_songs.append(song)

    return loaded_songs
