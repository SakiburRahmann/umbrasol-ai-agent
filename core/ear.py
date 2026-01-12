import os
import sys
import json
import queue

try:
    import vosk
    import sounddevice as sd
    AUDIO_AVAILABLE = True
except ImportError as e:
    print(f"[EAR] Warning: Audio dependencies missing ({e}). Voice disabled.")
    AUDIO_AVAILABLE = False
except OSError as e:
    print(f"[EAR] Warning: PortAudio missing ({e}). Voice disabled.")
    print("Run: sudo apt-get install libportaudio2")
    AUDIO_AVAILABLE = False

class Ear:
    """The Auditory Perception Module (Layer 3)."""
    def __init__(self, model_path="models/model"):
        if not AUDIO_AVAILABLE:
            self.model = None
            return

        self.model_path = model_path
        if not os.path.exists(model_path):
            print(f"[EAR] Error: Model not found at {model_path}")
            print("Please run: cd models && wget ...")
            self.model = None
            return

        print(f"[EAR] Loading VOSK Model from {model_path}...")
        try:
            vosk.SetLogLevel(-1) # Silence VOSK
            self.model = vosk.Model(model_path)
            self.q = queue.Queue()
            print("[EAR] Auditory Cortex Online. (VOSK)")
        except Exception as e:
            print(f"[EAR] Fail: {str(e)}")
            self.model = None

    def _callback(self, indata, frames, time, status):
        """This is called (from a separate thread) for each audio block."""
        if status:
            print(status, file=sys.stderr)
        self.q.put(bytes(indata))

    def listen(self, timeout=None):
        """Generator that yields text command strings."""
        if not self.model: return

        # 16kHz sample rate is standard for VOSK models
        samplerate = 16000
        
        try:
            with sd.RawInputStream(samplerate=samplerate, blocksize=8000, dtype='int16',
                                   channels=1, callback=self._callback):
                rec = vosk.KaldiRecognizer(self.model, samplerate)
                print("[EAR] Listening... (Say something)")
                
                while True:
                    data = self.q.get()
                    if rec.AcceptWaveform(data):
                        result = json.loads(rec.Result())
                        text = result.get('text', '')
                        if text:
                            yield text
                    else:
                        # Partial results - good for "wake word" detection if needed
                        # partial = json.loads(rec.PartialResult())
                        pass
                        
        except Exception as e:
            print(f"[EAR] Microphone Error: {str(e)}")

    def listen_once(self):
        """Listens for a single command and returns it."""
        for command in self.listen():
            return command  # Return first valid command

if __name__ == "__main__":
    ear = Ear()
    for cmd in ear.listen():
        print(f"Heard: {cmd}")
