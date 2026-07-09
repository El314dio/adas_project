import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import numpy as np
import unittest

os.environ["ADAS_CONFIG"] = os.path.join(
    os.path.dirname(__file__), "../config/settings.yaml"
)

from adas.core.classifier import classificar_deteccoes


def _make(score=0.9, cls=0, ymin=0.35, xmin=0.35, ymax=0.75, xmax=0.65):
    boxes   = np.array([[ymin, xmin, ymax, xmax]], dtype=np.float32)
    classes = np.array([cls], dtype=int)
    scores  = np.array([score], dtype=np.float32)
    return boxes, classes, scores


class TestSemDeteccao(unittest.TestCase):
    def test_score_baixo(self):
        r = classificar_deteccoes(*_make(score=0.10))
        self.assertFalse(r["tem_deteccao"])

    def test_classe_fora(self):
        r = classificar_deteccoes(*_make(cls=99))
        self.assertFalse(r["tem_deteccao"])

    def test_area_pequena(self):
        r = classificar_deteccoes(*_make(ymin=0.49, ymax=0.51, xmin=0.49, xmax=0.51))
        self.assertFalse(r["tem_deteccao"])


class TestComDeteccao(unittest.TestCase):
    def test_pedestre_valido(self):
        r = classificar_deteccoes(*_make())
        self.assertTrue(r["tem_deteccao"])
        self.assertGreater(r["n_total"], 0)

    def test_dentro_trapezio(self):
        r = classificar_deteccoes(*_make(ymin=0.25, xmin=0.44, ymax=0.65, xmax=0.56))
        self.assertTrue(r["dentro_trapezio"])
        self.assertLess(r["dist_min_trap"], float("inf"))

    def test_distancia_calculada(self):
        r = classificar_deteccoes(*_make(ymin=0.25, xmin=0.44, ymax=0.65, xmax=0.56))
        self.assertIsInstance(r["dist_min_trap"], float)
        self.assertGreater(r["dist_min_trap"], 0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
