"""Unit tests for the Standard MIDI File (.mid) parser and Song Importer."""
import os
import struct
import tempfile
import unittest
from core.notes import Note
from core.songs import Song, SongNote
from core.midi_importer import (
    MidiParser,
    import_midi_as_song,
    save_user_song,
    load_user_songs,
    _read_vlq,
)


def _encode_vlq(val: int) -> bytes:
    """Encodes integer to MIDI variable-length quantity bytes."""
    buf = val & 0x7F
    raw = [buf]
    while (val := val >> 7):
        buf = (val & 0x7F) | 0x80
        raw.insert(0, buf)
    return bytes(raw)


def build_synthetic_midi(events: list, division: int = 480) -> bytes:
    """
    Builds a minimal valid Standard MIDI File (Format 0) byte stream.
    events: list of (delta_ticks, status, data1, data2)
    """
    # Build MTrk track chunk
    track_body = bytearray()
    for delta, status, d1, d2 in events:
        track_body.extend(_encode_vlq(delta))
        track_body.append(status)
        track_body.append(d1)
        if d2 is not None:
            track_body.append(d2)

    # End of Track meta event: delta=0, FF 2F 00
    track_body.extend(_encode_vlq(0))
    track_body.extend(b"\xFF\x2F\x00")

    # MThd header chunk: Format 0, 1 track, division
    header = b"MThd" + struct.pack(">IHHH", 6, 0, 1, division)
    track = b"MTrk" + struct.pack(">I", len(track_body)) + bytes(track_body)
    return header + track


class TestMidiImporter(unittest.TestCase):

    def test_read_vlq(self):
        self.assertEqual(_read_vlq(b"\x00", 0), (0, 1))
        self.assertEqual(_read_vlq(b"\x40", 0), (64, 1))
        self.assertEqual(_read_vlq(b"\x81\x00", 0), (128, 2))

    def test_parser_and_melody_extraction(self):
        # Create a simple C4 -> E4 -> G4 sequence
        # C4 (60): on at t=0, off at t=480 (dur 1 beat)
        # E4 (64): on at t=480, off at t=960 (dur 1 beat)
        # G4 (67): on at t=960, off at t=1440 (dur 1 beat)
        events = [
            (0, 0x90, 60, 100),    # Note On C4
            (480, 0x80, 60, 0),    # Note Off C4
            (0, 0x90, 64, 100),    # Note On E4
            (480, 0x80, 64, 0),    # Note Off E4
            (0, 0x90, 67, 100),    # Note On G4
            (480, 0x80, 67, 0),    # Note Off G4
        ]
        midi_bytes = build_synthetic_midi(events, division=480)
        parser = MidiParser(midi_bytes)
        notes, bpm = parser.extract_monophonic_melody()

        self.assertEqual(len(notes), 3)
        self.assertEqual(notes[0][0], 60)  # C4
        self.assertEqual(notes[1][0], 64)  # E4
        self.assertEqual(notes[2][0], 67)  # G4

    def test_import_midi_as_song(self):
        events = [
            (0, 0x90, 60, 100),    # C4
            (480, 0x80, 60, 0),
            (0, 0x90, 62, 100),    # D4
            (480, 0x80, 62, 0),
            (0, 0x90, 64, 100),    # E4
            (480, 0x80, 64, 0),
        ]
        midi_bytes = build_synthetic_midi(events, division=480)

        with tempfile.NamedTemporaryFile(suffix=".mid", delete=False) as tmp:
            tmp.write(midi_bytes)
            tmp_path = tmp.name

        try:
            song = import_midi_as_song(tmp_path, title="Teste Melodia", composer="Compositor Teste")
            self.assertIsInstance(song, Song)
            self.assertIn("Teste Melodia", song.title)
            self.assertEqual(len(song.notes), 3)
            self.assertEqual(song.notes[0].note.pitch_with_octave, "C4")
            self.assertEqual(song.notes[1].note.pitch_with_octave, "D4")
            self.assertEqual(song.notes[2].note.pitch_with_octave, "E4")
            # Verify ergonomics were assigned
            self.assertIsNotNone(song.notes[0].piano_finger)
            self.assertIsNotNone(song.notes[0].guitar_string)
            self.assertIsNotNone(song.notes[0].guitar_fret)
        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)

    def test_user_song_json_persistence(self):
        song = Song(
            id="user_teste123",
            title="Minha Obra",
            composer="Eu",
            difficulty="Iniciante",
            bpm=110,
            notes=[
                SongNote(note=Note("C4"), duration_beats=1.0, piano_finger=1, guitar_string=4, guitar_fret=1),
                SongNote(note=Note("G4"), duration_beats=2.0, piano_finger=5, guitar_string=5, guitar_fret=3),
            ],
        )

        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as tmp:
            tmp_json = tmp.name

        try:
            save_user_song(song, filepath=tmp_json)
            loaded = load_user_songs(filepath=tmp_json)
            self.assertEqual(len(loaded), 1)
            self.assertEqual(loaded[0].id, "user_teste123")
            self.assertEqual(loaded[0].title, "Minha Obra")
            self.assertEqual(len(loaded[0].notes), 2)
            self.assertEqual(loaded[0].notes[0].note.pitch_with_octave, "C4")
        finally:
            if os.path.exists(tmp_json):
                os.remove(tmp_json)


if __name__ == "__main__":
    unittest.main()
