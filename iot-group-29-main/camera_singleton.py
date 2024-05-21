import threading
from imutils.video.pivideostream import PiVideoStream
import time

class CameraSingleton:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super(CameraSingleton, cls).__new__(cls)
                    cls._instance.camera = None
        return cls._instance

    def start_camera(self):
        if self.camera is None:
            self.camera = PiVideoStream().start()
            time.sleep(2.0)  # Camera warm-up time

    def stop_camera(self):
        if self.camera is not None:
            self.camera.stop()
            self.camera = None

    def get_frame(self):
        if self.camera is not None:
            return self.camera.read()
        return None
