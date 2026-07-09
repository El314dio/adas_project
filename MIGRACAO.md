# Guia de Migração — projeto_tcc → adas_project

---

## 1. Transfira o projeto para a Raspberry Pi

No seu computador, dentro da pasta onde está o `adas_project/`:

```bash
scp -r adas_project/ pi@<IP_DA_RASPBERRY>:/home/pi/
```

Se não souber o IP da Raspberry:
```bash
# Na própria Raspberry
hostname -I
```

---

## 2. Instale a dependência nova (PyYAML)

O projeto agora lê um arquivo `settings.yaml`, então precisa do PyYAML
no mesmo ambiente virtual que você já usa:

```bash
/home/pi/tflite_env/bin/pip install pyyaml
```

Todas as outras bibliotecas (tflite-runtime, opencv, numpy, RPi.GPIO,
picamera2, obd) você já tem instaladas no `tflite_env`.

---

## 3. Copie o modelo TFLite para o novo lugar

```bash
cp /home/pi/projeto_tcc/models/mobilenet_ssd/detect.tflite \
   /home/pi/adas_project/models/mobilenet_ssd/detect.tflite
```

> Se o seu modelo estiver em outro caminho, ajuste o campo
> `model.path` em `config/settings.yaml`.

---

## 4. Crie o diretório de logs

```bash
sudo mkdir -p /var/log/adas
sudo chown pi:pi /var/log/adas
```

---

## 5. Pare e desative o serviço antigo

```bash
sudo systemctl stop deteccao_pedestre
sudo systemctl disable deteccao_pedestre
```

O arquivo antigo continua em `/etc/systemd/system/` sem causar problema,
mas se quiser remover de vez:
```bash
sudo rm /etc/systemd/system/deteccao_pedestre.service
```

---

## 6. Instale o novo serviço

```bash
sudo cp /home/pi/adas_project/scripts/adas.service \
        /etc/systemd/system/adas.service

sudo systemctl daemon-reload
sudo systemctl enable adas.service
sudo systemctl start adas.service
```

---

## 7. Verifique se está rodando

```bash
# Status geral
sudo systemctl status adas

# Logs em tempo real (Ctrl+C para sair)
sudo journalctl -u adas -f

# Logs do arquivo rotativo
tail -f /var/log/adas/adas.log
```

Saída esperada nos logs:
```
[INFO] 2025-01-01 08:00:01  __main__ — ADAS v1.0.0 iniciando...
[INFO] 2025-01-01 08:00:03  __main__ — Pipeline iniciado.
[INFO] 2025-01-01 08:00:08  adas.core.pipeline — FPS=8.2 | Vel=0 km/h [obd] | det=0 trap=0 dist=0.0m
```

---

## 8. Teste sem hardware (opcional, no PC)

Para rodar os testes unitários da lógica de detecção sem precisar
de câmera ou GPIO:

```bash
cd adas_project
python3 -m pytest tests/ -v
```

---

## Diferenças entre o serviço antigo e o novo

| | deteccao_pedestre.service | adas.service |
|---|---|---|
| Script executado | `detect_mobilenet_tflite.py` | `main.py` |
| Pasta do projeto | `/home/pi/projeto_tcc` | `/home/pi/adas_project` |
| Reinício automático | Não | Sim (5 s após falha) |
| Limite de reinícios | — | 5 tentativas em 60 s |
| Bluetooth (OBD) | Não aguarda | Aguarda serviço BT |
| Variável de config | — | `ADAS_CONFIG` aponta para o YAML |
| Log em arquivo | Só journal | Journal + arquivo rotativo |

---

## Estrutura final na Raspberry

```
/home/pi/
├── tflite_env/              ← ambiente virtual existente (não muda)
├── projeto_tcc/             ← projeto antigo (pode manter ou apagar)
└── adas_project/            ← projeto novo
    ├── main.py
    ├── requirements.txt
    ├── config/
    │   └── settings.yaml    ← edite aqui para ajustar parâmetros
    ├── adas/
    │   ├── core/
    │   ├── hal/
    │   └── utils/
    ├── models/
    │   └── mobilenet_ssd/
    │       └── detect.tflite  ← copie o seu modelo aqui
    ├── logs/                  ← pasta reserva (log principal em /var/log/adas)
    └── scripts/
        └── adas.service

/etc/systemd/system/
└── adas.service             ← copiado pelo passo 6

/var/log/adas/
└── adas.log                 ← log rotativo (máx 10 MB × 5 arquivos)
```

---

## Comandos úteis do dia a dia

```bash
sudo systemctl start adas       # iniciar
sudo systemctl stop adas        # parar
sudo systemctl restart adas     # reiniciar (após editar o YAML)
sudo systemctl status adas      # ver estado atual
sudo journalctl -u adas -f      # logs ao vivo
sudo journalctl -u adas --since "1 hour ago"   # última hora
```

---

## Ajustar parâmetros sem mexer no código

Edite o arquivo de configuração e reinicie:

```bash
nano /home/pi/adas_project/config/settings.yaml
sudo systemctl restart adas
```
