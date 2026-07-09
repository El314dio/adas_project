import logging
import signal
import threading

from adas.core.config import CFG
from adas.core.pipeline import Pipeline
from adas.utils.logging_setup import configurar_logging

log = logging.getLogger(__name__)

_running = threading.Event()
_running.set()


def _ao_encerrar(sig, frame):
    log.info("Sinal %s recebido — encerrando...", sig)
    _running.clear()


signal.signal(signal.SIGINT,  _ao_encerrar)
signal.signal(signal.SIGTERM, _ao_encerrar)


def main():
    configurar_logging(
        nivel        = CFG.log_nivel,
        arquivo      = CFG.log_arquivo,
        max_bytes    = CFG.log_max_bytes,
        backup_count = CFG.log_backups,
    )

    log.info("ADAS v1.0.0 iniciando...")
    pipeline = Pipeline(_running)

    try:
        pipeline.iniciar()
        pipeline.executar()
    except Exception as exc:
        log.critical("Erro fatal: %s", exc, exc_info=True)
    finally:
        pipeline.encerrar()
        log.info("Sistema encerrado.")


if __name__ == "__main__":
    main()
