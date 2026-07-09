from typing import Dict, Any

import numpy as np

from .config import CFG


_TRAP_DY    = CFG.trap_y_base - CFG.trap_y_topo
_TRAP_DX_ESQ = CFG.trap_x_base_esq - CFG.trap_x_topo_esq
_TRAP_DX_DIR = CFG.trap_x_base_dir - CFG.trap_x_topo_dir
_FL_H        = CFG.altura_real_pedestre * CFG.focal_length


def _dentro_do_trapezio(px: float, py: float) -> bool:
    if not (CFG.trap_y_topo <= py <= CFG.trap_y_base):
        return False
    t = (py - CFG.trap_y_topo) / _TRAP_DY
    return (CFG.trap_x_topo_esq + t * _TRAP_DX_ESQ) <= px <= (CFG.trap_x_topo_dir + t * _TRAP_DX_DIR)
   


def _bbox_valida(ymin: float, xmin: float, ymax: float, xmax: float) -> bool:
    w = xmax - xmin
    h = ymax - ymin
    if w * h < CFG.area_min:
        return False
    if w <= 0 or (h / w) < CFG.aspecto_min:
        return False
    return True


def classificar_deteccoes(boxes: np.ndarray, classes: np.ndarray, scores: np.ndarray) -> Dict[str, Any]:
    resultado: Dict[str, Any] = {
        "tem_deteccao":    False,
        "dentro_trapezio": False,
        "dist_min_trap":   float("inf"),
        "n_total":         0,
        "n_dentro":        0,
    }

    pre  = (scores > CFG.conf_threshold) & np.isin(classes, CFG.classes_alvo)
    idxs = np.where(pre)[0]
    if not len(idxs):
        return resultado

    for i in idxs:
        ymin, xmin, ymax, xmax = boxes[i]
        if not _bbox_valida(ymin, xmin, ymax, xmax):
            continue

        resultado["tem_deteccao"] = True
        resultado["n_total"]     += 1

        px = (xmin + xmax) * 0.5
        py = ymax

        if not _dentro_do_trapezio(px, py):
            continue

        resultado["dentro_trapezio"] = True
        resultado["n_dentro"]        += 1

        h_px = (ymax - ymin) * CFG.cam_height
        if h_px > 0:
            dist = _FL_H / h_px
            if dist < resultado["dist_min_trap"]:
                resultado["dist_min_trap"] = dist

    return resultado
    
    
