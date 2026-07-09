import cv2
import numpy as np
import sys, os, time

sys.path.insert(0, "/home/pi/adas_project")
os.environ["ADAS_CONFIG"] = "/home/pi/adas_project/config/settings.yaml"

from adas.core.config import CFG
from picamera2 import Picamera2

W, H = CFG.cam_width, CFG.cam_height

cam = Picamera2()
cam.configure(cam.create_video_configuration(
    main={"size": (W, H), "format": "RGB888"}
))
cam.start()
time.sleep(2)
frame = cam.capture_array()
cam.stop()

img = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

trap_pts = np.array([
    [int(CFG.trap_x_topo_esq * W), int(CFG.trap_y_topo * H)],
    [int(CFG.trap_x_topo_dir * W), int(CFG.trap_y_topo * H)],
    [int(CFG.trap_x_base_dir * W), int(CFG.trap_y_base * H)],
    [int(CFG.trap_x_base_esq * W), int(CFG.trap_y_base * H)],
], dtype=np.int32)

overlay = img.copy()
cv2.fillPoly(overlay, [trap_pts], (0, 255, 0))
cv2.addWeighted(overlay, 0.25, img, 0.75, 0, img)
cv2.polylines(img, [trap_pts], isClosed=True, color=(0, 200, 0), thickness=2)

vertices = {
    "Topo Esq":  trap_pts[0],
    "Topo Dir":  trap_pts[1],
    "Base Dir":  trap_pts[2],
    "Base Esq":  trap_pts[3],
}
for nome, (x, y) in vertices.items():
    cv2.circle(img, (x, y), 5, (0, 200, 0), -1)
    cv2.putText(img, nome, (x + 6, y - 6),
                cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 200, 0), 1)

cx = int(sum(p[0] for p in trap_pts) / 4)
cy = int(sum(p[1] for p in trap_pts) / 4)
cv2.putText(img, "ZONA DE RISCO", (cx - 70, cy),
            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 200, 0), 2)

saida = "/home/pi/adas_project/trapezio_preview.png"
cv2.imwrite(saida, img)
print(f"Imagem salva em: {saida}")
print(f"Vertices (pixels):")
for nome, (x, y) in vertices.items():
    print(f"  {nome}: ({x}, {y})")
