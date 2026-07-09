import logging
import threading
import time

from ..core.config import CFG

log = logging.getLogger(__name__)

try:
    import obd
    _OBD_DISPONIVEL = True
except ImportError:
    _OBD_DISPONIVEL = False


class VelocidadeOBD(threading.Thread):
    __slots__ = ("_lock", "_velocidade", "_fonte", "_conn", "_running")

    def __init__(self, running_flag: threading.Event):
        super().__init__(daemon=True, name="VelocidadeOBD")
        self._running    = running_flag
        self._lock       = threading.Lock()
        self._velocidade = 0.0
        self._fonte      = "sem_sinal"
        self._conn       = None

    @property
    def velocidade_kmh(self) -> float:
        with self._lock:
            return self._velocidade

    @property
    def fonte(self) -> str:
        with self._lock:
            return self._fonte

    def run(self):
        if not _OBD_DISPONIVEL:
            log.warning("OBD: biblioteca não disponível. Velocidade permanece 0.")
            return
        while self._running.is_set():
            self._conectar()
            if self._conn and self._conn.is_connected():
                self._ler()

    def _conectar(self):
        try:
            c = obd.OBD(
                portstr   = CFG.obd_porta,
                baudrate  = CFG.obd_baudrate,
                timeout   = CFG.obd_timeout,
                fast      = False,
            )
            if c.is_connected():
                self._conn = c
                with self._lock:
                    self._fonte = "obd"
                log.info("OBD: conectado — protocolo %s", c.protocol_name())
            else:
                time.sleep(5)
        except Exception as exc:
            log.warning("OBD: falha na conexão: %s. Nova tentativa em 5 s.", exc)
            time.sleep(5)

    def _ler(self):
        cmd = obd.commands.SPEED
        iv  = 1.0 / CFG.obd_hz
        while self._running.is_set() and self._conn and self._conn.is_connected():
            try:
                r = self._conn.query(cmd)
                if not r.is_null():
                    with self._lock:
                        self._velocidade = float(r.value.magnitude)
            except Exception as exc:
                log.warning("OBD: perda de sinal: %s", exc)
                with self._lock:
                    self._velocidade = 0.0
                    self._fonte      = "sem_sinal"
                break
            time.sleep(iv)

    def parar(self):
        if self._conn:
            try:
                self._conn.close()
            except Exception:
                pass
