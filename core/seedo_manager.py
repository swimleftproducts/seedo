import time
import threading
from helpers.config_loading import load_all_seedos

class SeeDoManager:
    def __init__(self):
        self.seedos = load_all_seedos()
        print(f"SeeDoManager initialized with {len(self.seedos)} SeeDos.")
        self._last_run = {seedo: 0.0 for seedo in self.seedos}

    def add(self, seedo):
        self.seedos.append(seedo)
        self._last_run[seedo] = 0.0

    def should_be_run(self, seedo, now):
        return (now - self._last_run[seedo]) >= seedo.interval_sec

    def run(self, frame, now):
        """Called from AppController.tick()"""
        if frame is None:
            return

        for seedo in self.seedos:
            if seedo.enabled and self.should_be_run(seedo, now):
                self._last_run[seedo] = now
                self._launch_eval_thread(seedo, frame, now)

    def _launch_eval_thread(self, seedo, frame, now):
        threading.Thread(
            target=self._process_seedo,
            args=(seedo, frame, now),
            daemon=True
        ).start()

    def _process_seedo(self, seedo, frame, now):
        result = seedo.evaluate(frame, now)
        if result:
            seedo.action.execute({"timestamp": now, "frame": frame})
