import logging
import time
from collections import deque

from .config import CFG
from .detector import Detector
from .classifier import classificar_deteccoes
from ..hal.camera import CapturaThread
from ..hal.obd import VelocidadeOBD
from ..hal.alerts import GerenciadorAlertas, BuzzerThread

log = logging.getLogger(__name__)


class Pipeline:
    def __init__(self, running_flag):
        self._running = running_flag
        self._buzzer = BuzzerThread(running_flag)
        self._alertas = GerenciadorAlertas(self._buzzer)
        self._captura = CapturaThread(running_flag)
        self._detector = Detector()
        self._obd = VelocidadeOBD(running_flag)

    def iniciar(self):
        self._captura.start()
        self._buzzer.start()
        self._obd.start()
        log.info("Pipeline iniciado.")

    def encerrar(self):
        self._captura.parar()
        self._obd.parar()
        self._buzzer.parar()
        self._captura.join(timeout=3)
        self._alertas.liberar()
        log.info("Pipeline encerrado.")

    def executar(self):
        fps_buf = deque(maxlen=CFG.fps_smoothing)
        t_anterior = time.perf_counter()
        frame_count = 0
        t_ultimo_log = time.time()

        # Inicializa métricas
        latencia_inferencia_ms = 0.0
        latencia_total_ms = 0.0

        while self._running.is_set():
            vel_kmh = self._obd.velocidade_kmh
            fonte_vel = self._obd.fonte

            # Início do processamento do frame
            t_frame_inicio = time.perf_counter()

            frame = self._captura.get_frame(timeout=0.5)
            if frame is None:
                continue

            frame_count += 1
            if frame_count % CFG.frame_skip != 0:
                continue

            # Inferência
            t_inf_inicio = time.perf_counter()
            boxes, classes, scores = self._detector.inferir(frame)
            t_inf_fim = time.perf_counter()

            resultado = classificar_deteccoes(boxes, classes, scores)
            self._alertas.atualizar(resultado, vel_kmh)

            # Fim do processamento
            t_frame_fim = time.perf_counter()

            # Latências
            latencia_inferencia_ms = (t_inf_fim - t_inf_inicio) * 1000
            latencia_total_ms = (t_frame_fim - t_frame_inicio) * 1000

            # FPS
            dt = max(t_frame_fim - t_anterior, 1e-9)
            fps_buf.append(1.0 / dt)
            t_anterior = t_frame_fim

            # Log periódico
            if time.time() - t_ultimo_log >= CFG.log_intervalo:
                fps = sum(fps_buf) / len(fps_buf) if fps_buf else 0.0

                log.info(
                    "FPS=%.1f | Inf=%.1fms | Total=%.1fms | Vel=%.0f km/h [%s] | det=%d trap=%d dist=%.1fm",
                    fps,
                    latencia_inferencia_ms,
                    latencia_total_ms,
                    vel_kmh,
                    fonte_vel,
                    resultado["n_total"],
                    resultado["n_dentro"],
                    resultado["dist_min_trap"]
                    if resultado["dist_min_trap"] != float("inf")
                    else 0.0,
                )

                t_ultimo_log = time.time()
