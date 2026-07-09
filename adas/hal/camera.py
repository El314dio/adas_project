import queue
import threading

from picamera2 import Picamera2

from ..core.config import CFG


class CapturaThread(threading.Thread):
    __slots__ = ("_fila", "_cam", "_running")

    def __init__(self, running_flag: threading.Event):
        super().__init__(daemon=True, name="CapturaThread")
        self._running = running_flag
        self._fila    = queue.Queue(maxsize=1)
        cam = Picamera2()
        cam.configure(cam.create_video_configuration(
            main={"size": (CFG.cam_width, CFG.cam_height), "format": "RGB888"}
        ))
        cam.start()
        self._cam = cam

    def run(self):
        while self._running.is_set():
            frame = self._cam.capture_array()
            try:
                self._fila.get_nowait()
            except queue.Empty:
                pass
            self._fila.put(frame)

    def get_frame(self, timeout: float = 0.5):
        try:
            return self._fila.get(timeout=timeout)
        except queue.Empty:
            return None

    def parar(self):
        self._cam.stop()
