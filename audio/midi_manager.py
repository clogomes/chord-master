"""USB MIDI hardware keyboard manager supporting plug-and-play input devices."""
import threading
import time
from typing import Callable, Dict, List, Optional, Any
from core.notes import Note, midi_to_note

try:
    import pygame
    import pygame.midi
    HAS_PYGAME_MIDI = True
except Exception:
    HAS_PYGAME_MIDI = False


class MidiManager:
    """
    Manages physical USB MIDI keyboard input detection and note events dispatching.
    """

    _instance: Optional["MidiManager"] = None

    def __init__(self):
        self._is_initialized = False
        self._is_listening = False
        self._input_device: Optional[Any] = None
        self._thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()
        self._lock = threading.Lock()

        self._on_note_on: Optional[Callable[[int, int], None]] = None
        self._on_note_off: Optional[Callable[[int], None]] = None

        self._init_midi()

    @classmethod
    def get_instance(cls) -> "MidiManager":
        if cls._instance is None:
            cls._instance = MidiManager()
        return cls._instance

    def _init_midi(self):
        if HAS_PYGAME_MIDI and not pygame.midi.get_init():
            try:
                pygame.midi.init()
                self._is_initialized = True
            except Exception as e:
                print(f"[MidiManager] Erro ao inicializar pygame.midi: {e}")
                self._is_initialized = False
        elif HAS_PYGAME_MIDI and pygame.midi.get_init():
            self._is_initialized = True

    def get_available_devices(self) -> List[Dict]:
        """Returns list of connected input MIDI devices."""
        if not self._is_initialized:
            return []

        devices = []
        try:
            count = pygame.midi.get_count()
            for i in range(count):
                info = pygame.midi.get_device_info(i)
                if info is not None:
                    interface, name, is_input, is_output, is_opened = info
                    name_str = name.decode("utf-8", errors="ignore") if isinstance(name, bytes) else str(name)
                    if is_input:
                        devices.append({
                            "device_id": i,
                            "name": name_str,
                            "is_input": True,
                            "is_opened": bool(is_opened),
                        })
        except Exception:
            pass
        return devices

    def start_listening(
        self,
        on_note_on: Callable[[int, int], None],
        on_note_off: Optional[Callable[[int], None]] = None,
        device_id: Optional[int] = None,
    ) -> bool:
        """
        Starts listening to incoming MIDI note events from USB keyboard.
        """
        if not self._is_initialized:
            return False

        with self._lock:
            if self._is_listening:
                self._on_note_on = on_note_on
                self._on_note_off = on_note_off
                return True

            self._on_note_on = on_note_on
            self._on_note_off = on_note_off

            # Find default input device if none specified
            if device_id is None:
                default_id = pygame.midi.get_default_input_id()
                if default_id < 0:
                    # Search first available input device
                    inputs = self.get_available_devices()
                    if inputs:
                        device_id = inputs[0]["device_id"]
                    else:
                        device_id = -1
                else:
                    device_id = default_id

            if device_id is None or device_id < 0:
                return False

            try:
                self._input_device = pygame.midi.Input(device_id)
                self._is_listening = True
                self._stop_event.clear()
                self._thread = threading.Thread(target=self._poll_midi_loop, daemon=True)
                self._thread.start()
                return True
            except Exception as e:
                print(f"[MidiManager] Erro ao abrir dispositivo MIDI {device_id}: {e}")
                self._is_listening = False
                self._input_device = None
                return False

    def stop_listening(self):
        """Stops MIDI polling and closes input device."""
        with self._lock:
            self._is_listening = False
            self._stop_event.set()
            if self._input_device is not None:
                try:
                    self._input_device.close()
                except Exception:
                    pass
                self._input_device = None
            self._on_note_on = None
            self._on_note_off = None

        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=0.2)
        self._thread = None

    def _poll_midi_loop(self):
        while not self._stop_event.is_set():
            if self._input_device is None:
                break

            try:
                if self._input_device.poll():
                    events = self._input_device.read(16)
                    for event in events:
                        data, timestamp = event
                        status = data[0] & 0xF0
                        note_midi = data[1]
                        velocity = data[2]

                        # Note On (0x90)
                        if status == 0x90:
                            if velocity > 0 and self._on_note_on is not None:
                                self._on_note_on(note_midi, velocity)
                            elif velocity == 0 and self._on_note_off is not None:
                                self._on_note_off(note_midi)
                        # Note Off (0x80)
                        elif status == 0x80 and self._on_note_off is not None:
                            self._on_note_off(note_midi)

            except Exception:
                pass

            time.sleep(0.005)  # 5ms polling loop for ultra-low latency


def get_midi_manager() -> MidiManager:
    return MidiManager.get_instance()
