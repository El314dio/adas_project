import os
from dataclasses import dataclass, field
from typing import Tuple, Dict

import yaml

_CONFIG_PATH = os.environ.get(
    "ADAS_CONFIG",
    os.path.join(os.path.dirname(__file__), "../../config/settings.yaml"),
)


@dataclass(frozen=True)
class Config:
    model_path:     str
    conf_threshold: float
    classes_alvo:   Tuple[int, ...]

    cam_width:    int
    cam_height:   int
    frame_skip:   int
    fps_smoothing: int

    area_min:    float
    aspecto_min: float

    trap_x_topo_esq: float
    trap_x_topo_dir: float
    trap_x_base_esq: float
    trap_x_base_dir: float
    trap_y_topo:     float
    trap_y_base:     float

    altura_real_pedestre: float
    focal_length:         float

    vel_min_movimento: float
    vel_alerta_kmh:    float
    vel_perigo_kmh:    float

    obd_porta:    str
    obd_baudrate: object
    obd_timeout:  float
    obd_hz:       float

    led_vermelho: int
    led_amarelo:  int
    led_verde:    int
    pino_buzzer:  int

    BUZZER_SILENCIO:     int = 0
    BUZZER_INTERMITENTE: int = 1
    BUZZER_CONTINUO:     int = 2

    buzzer_pulso_on:  float = 0.20
    buzzer_pulso_off: float = 0.30

    nomes_classe: Dict[int, str] = field(
        default_factory=lambda: {0: "Pedestre", 1: "Ciclista", 3: "Moto"}
    )

    log_intervalo: float = 5.0
    log_nivel:     str   = "INFO"
    log_arquivo:   str   = "/var/log/adas/adas.log"
    log_max_bytes: int   = 10_485_760
    log_backups:   int   = 5
    
    frames_confirmacao: int = 5


def _load() -> Config:
    path = os.path.abspath(_CONFIG_PATH)
    with open(path, "r") as fh:
        y = yaml.safe_load(fh)

    return Config(
        model_path     = y["model"]["path"],
        conf_threshold = y["model"]["conf_threshold"],
        classes_alvo   = tuple(y["model"]["classes_alvo"]),

        cam_width     = y["camera"]["width"],
        cam_height    = y["camera"]["height"],
        frame_skip    = y["camera"]["frame_skip"],
        fps_smoothing = y["camera"]["fps_smoothing"],


        area_min    = y["filtro_bbox"]["area_min"],
        aspecto_min = y["filtro_bbox"]["aspecto_min"],

        trap_x_topo_esq = y["trapezio"]["x_topo_esq"],
        trap_x_topo_dir = y["trapezio"]["x_topo_dir"],
        trap_x_base_esq = y["trapezio"]["x_base_esq"],
        trap_x_base_dir = y["trapezio"]["x_base_dir"],
        trap_y_topo     = y["trapezio"]["y_topo"],
        trap_y_base     = y["trapezio"]["y_base"],

        altura_real_pedestre = y["distancia"]["altura_real_pedestre"],
        focal_length         = y["distancia"]["focal_length"],

        vel_min_movimento = y["velocidade"]["vel_min_movimento"],
        vel_alerta_kmh    = y["velocidade"]["vel_alerta_kmh"],
        vel_perigo_kmh    = y["velocidade"]["vel_perigo_kmh"],

        obd_porta    = y["obd"]["porta"],
        obd_baudrate = y["obd"]["baudrate"],
        obd_timeout  = y["obd"]["timeout"],
        obd_hz       = y["obd"]["hz"],

        led_vermelho = y["gpio"]["led_vermelho"],
        led_amarelo  = y["gpio"]["led_amarelo"],
        led_verde    = y["gpio"]["led_verde"],
        pino_buzzer  = y["gpio"]["pino_buzzer"],

        buzzer_pulso_on  = y["buzzer"]["pulso_on"],
        buzzer_pulso_off = y["buzzer"]["pulso_off"],

        log_intervalo = y["logging"]["intervalo"],
        log_nivel     = y["logging"]["nivel"],
        log_arquivo   = y["logging"]["arquivo"],
        log_max_bytes = y["logging"]["max_bytes"],
        log_backups   = y["logging"]["backup_count"],
        
        frames_confirmacao = y.get("filtro", {}).get("frames_confirmacao", 5),
    )


CFG: Config = _load()
