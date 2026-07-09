import logging
import logging.handlers
import os


def configurar_logging(nivel: str, arquivo: str, max_bytes: int, backup_count: int):
    os.makedirs(os.path.dirname(arquivo), exist_ok=True)

    fmt = logging.Formatter(
        fmt="[%(levelname)s] %(asctime)s  %(name)s — %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    root = logging.getLogger()
    root.setLevel(getattr(logging, nivel.upper(), logging.INFO))

    ch = logging.StreamHandler()
    ch.setFormatter(fmt)
    root.addHandler(ch)

    fh = logging.handlers.RotatingFileHandler(
        filename    = arquivo,
        maxBytes    = max_bytes,
        backupCount = backup_count,
        encoding    = "utf-8",
    )
    fh.setFormatter(fmt)
    root.addHandler(fh)
