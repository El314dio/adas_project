# ADAS — Sistema de Detecção e Alerta de Segurança

Sistema embarcado de detecção de pedestres, ciclistas e motos para Raspberry Pi,
com alerta visual (LEDs) e sonoro (buzzer) baseado na velocidade OBD-II do veículo.

---

## Estrutura do projeto

```
adas_project/
├── main.py                  # Ponto de entrada
├── requirements.txt
├── config/
│   └── settings.yaml        # Todos os parâmetros configuráveis
├── adas/
│   ├── core/
│   │   ├── config.py        # Carrega settings.yaml → dataclass imutável
│   │   ├── detector.py      # Inferência TFLite
│   │   ├── classifier.py    # Filtro de bbox, trapézio, distância
│   │   └── pipeline.py      # Loop principal de processamento
│   ├── hal/                 # Hardware Abstraction Layer
│   │   ├── camera.py        # Thread de captura da PiCamera2
│   │   ├── obd.py           # Thread de leitura de velocidade OBD-II
│   │   └── alerts.py        # Thread do buzzer + gerenciador de LEDs
│   └── utils/
│       └── logging_setup.py # Log rotativo em arquivo + console
├── models/
│   └── mobilenet_ssd/
│       └── detect.tflite    # ← coloque o modelo aqui
├── scripts/
│   ├── install.sh           # Instalação completa no sistema
│   └── adas.service         # Unit systemd (autostart + watchdog)
└── tests/
    └── test_classifier.py   # Testes unitários (sem hardware)
```

---

## Instalação rápida (Raspberry Pi)

```bash
git clone <repo> adas_project
cd adas_project

# Coloque o modelo TFLite no lugar certo
cp seu_modelo.tflite models/mobilenet_ssd/detect.tflite

# Execute o instalador como root
sudo bash scripts/install.sh
```

O script:
- Instala todas as dependências Python e de sistema
- Cria o usuário de serviço `adas` com as permissões corretas (gpio, dialout, bluetooth)
- Copia o projeto para `/opt/adas`
- Registra e habilita o serviço systemd com watchdog automático

---

## Comandos do serviço

```bash
sudo systemctl start adas      # Iniciar
sudo systemctl stop adas       # Parar
sudo systemctl status adas     # Ver status
sudo journalctl -u adas -f     # Acompanhar logs em tempo real
```

---

## Configuração

Edite `/opt/adas/config/settings.yaml` e reinicie o serviço:

```bash
sudo nano /opt/adas/config/settings.yaml
sudo systemctl restart adas
```

Parâmetros mais comuns:

| Parâmetro | Descrição |
|---|---|
| `model.conf_threshold` | Confiança mínima de detecção (0–1) |
| `velocidade.vel_alerta_kmh` | Velocidade para alerta amarelo |
| `velocidade.vel_perigo_kmh` | Velocidade para alerta vermelho |
| `obd.porta` | Porta Bluetooth do adaptador OBD |
| `camera.frame_skip` | Processar 1 a cada N frames |

---

## Executar testes (sem hardware)

```bash
cd adas_project
python3 -m pytest tests/ -v
```

---

## Lógica de alertas

| Situação | LED | Buzzer |
|---|---|---|
| Nenhuma detecção | Apagado | Silêncio |
| Detecção fora do trapézio / vel < 2 km/h | Verde | Silêncio |
| Detecção no trapézio, vel ≥ 5 km/h | Amarelo | Intermitente |
| Detecção no trapézio, vel ≥ 10 km/h | Vermelho | Contínuo |

---

## Pinagem GPIO (BCM)

| Pino | Função |
|---|---|
| 17 | LED Vermelho |
| 27 | LED Amarelo |
| 22 | LED Verde |
| 4  | Buzzer |
