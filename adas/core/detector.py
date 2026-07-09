import numpy as np
import cv2
from tflite_runtime.interpreter import Interpreter

from .config import CFG


class Detector:
    __slots__ = ("_interp", "_idx_in", "_dtype", "_h", "_w",
                 "_idx_boxes", "_idx_classes", "_idx_scores")

    def __init__(self):
        self._interp = Interpreter(model_path=CFG.model_path, num_threads=2)
        self._interp.allocate_tensors()
        inp = self._interp.get_input_details()[0]
        out = self._interp.get_output_details()
        self._idx_in      = inp["index"]
        self._dtype       = inp["dtype"]
        self._h           = inp["shape"][1]
        self._w           = inp["shape"][2]
        self._idx_boxes   = out[0]["index"]
        self._idx_classes = out[1]["index"]
        self._idx_scores  = out[2]["index"]

    def inferir(self, frame_rgb: np.ndarray):
        self._interp.set_tensor(self._idx_in, self._pre(frame_rgb))
        self._interp.invoke()
        return (
            self._interp.get_tensor(self._idx_boxes)[0],
            self._interp.get_tensor(self._idx_classes)[0].astype(int),
            self._interp.get_tensor(self._idx_scores)[0],
        )

    def _pre(self, frame: np.ndarray) -> np.ndarray:
        img = cv2.resize(frame, (self._w, self._h), interpolation=cv2.INTER_LINEAR)
        if self._dtype == np.uint8:
            return np.expand_dims(img, axis=0)
        img = img.astype(np.float32)
        img -= 127.5
        img /= 127.5
        return np.expand_dims(img, axis=0)
