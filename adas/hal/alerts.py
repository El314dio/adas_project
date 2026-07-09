import threading
import time
from typing import Dict, Any

import RPi.GPIO as GPIO

from ..core.config import CFG


class BuzzerThread(threading.Thread):
    __slots__ = ("_lock", "_modo", "_pino_hw", "_running")

    def __init__(self, running_flag: threading.Event):
        super().__init__(daemon=True, name="BuzzerThread")
        self._running = running_flag
        self._lock    = threading.Lock()
        self._modo    = CFG.BUZZER_SILENCIO
        self._pino_hw = False

    def set_modo(self, modo: int):
        with self._lock:
            self._modo = modo

    def _modo_atual(self) -> int:
        with self._lock:
            return self._modo

    def _ligar(self):
        if not self._pino_hw:
            GPIO.output(CFG.pino_buzzer, GPIO.HIGH)
            self._pino_hw = True

    def _desligar(self):
        if self._pino_hw:
            GPIO.output(CFG.pino_buzzer, GPIO.LOW)
            self._pino_hw = False

    def _sleep_cancelavel(self, dur: float) -> bool:
        modo_inicial = self._modo_atual()
        t0 = time.monotonic()
        while time.monotonic() - t0 < dur:
            if not self._running.is_set():
                return False
            if self._modo_atual() != modo_inicial:
                return False
            time.sleep(0.02)
        return True

    def run(self):
        while self._running.is_set():
            m = self._modo_atual()
            if m == CFG.BUZZER_SILENCIO:
                self._desligar()
                time.sleep(0.05)
            elif m == CFG.BUZZER_CONTINUO:
                self._ligar()
                time.sleep(0.05)
            elif m == CFG.BUZZER_INTERMITENTE:
                self._ligar()
                if not self._sleep_cancelavel(CFG.buzzer_pulso_on):
                    continue
                self._desligar()
                self._sleep_cancelavel(CFG.buzzer_pulso_off)
        self._desligar()

    def parar(self):
        self._desligar()


class GerenciadorAlertas:
    __slots__ = ("_buzzer", "_pinos_led", "_led_atual",
                 "_estado_atual", "_estado_candidato", "_contador")

    def __init__(self, buzzer: BuzzerThread):
        self._buzzer          = buzzer
        self._pinos_led       = [CFG.led_vermelho, CFG.led_amarelo, CFG.led_verde]
        self._led_atual       = None
        self._estado_atual    = "silencio"
        self._estado_candidato = "silencio"
        self._contador        = 0

        GPIO.setmode(GPIO.BCM)
        for p in self._pinos_led + [CFG.pino_buzzer]:
            GPIO.setup(p, GPIO.OUT, initial=GPIO.LOW)

    def atualizar(self, resultado: dict, vel_kmh: float):
        novo_estado = self._calcular_estado(resultado, vel_kmh)

        if novo_estado == self._estado_candidato:
            self._contador += 1
        else:
            self._estado_candidato = novo_estado
            self._contador = 1

        if self._contador >= CFG.frames_confirmacao:
            if novo_estado != self._estado_atual:
                self._estado_atual = novo_estado
                self._aplicar_estado(novo_estado)

    def _calcular_estado(self, resultado: dict, vel_kmh: float) -> str:
        if not resultado["tem_deteccao"]:
            return "silencio"
        if vel_kmh < CFG.vel_min_movimento or not resultado["dentro_trapezio"]:
            return "verde"
        if vel_kmh >= CFG.vel_perigo_kmh:
            return "vermelho"
        if vel_kmh >= CFG.vel_alerta_kmh:
            return "amarelo"
        return "verde"

    def _aplicar_estado(self, estado: str):
        mapa = {
            "silencio":  (None,              CFG.BUZZER_SILENCIO),
            "verde":     (CFG.led_verde,     CFG.BUZZER_SILENCIO),
            "amarelo":   (CFG.led_amarelo,   CFG.BUZZER_INTERMITENTE),
            "vermelho":  (CFG.led_vermelho,  CFG.BUZZER_CONTINUO),
        }
        led, buzzer = mapa[estado]
        self._set_led(led)
        self._buzzer.set_modo(buzzer)

    def _set_led(self, pino_alvo):
        if self._led_atual == pino_alvo:
            return
        for p in self._pinos_led:
            GPIO.output(p, GPIO.HIGH if p == pino_alvo else GPIO.LOW)
        self._led_atual = pino_alvo

    def liberar(self):
        self._set_led(None)
        GPIO.output(CFG.pino_buzzer, GPIO.LOW)
        GPIO.cleanup()
 
