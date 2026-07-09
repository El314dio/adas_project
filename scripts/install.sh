#!/usr/bin/env bash
set -euo pipefail

INSTALL_DIR="/opt/adas"
SERVICE_USER="adas"
LOG_DIR="/var/log/adas"

echo "=== ADAS — Instalação do sistema ==="

# 1. Dependências do sistema
echo "[1/6] Instalando dependências do sistema..."
apt-get update -qq
apt-get install -y --no-install-recommends \
    python3-pip python3-yaml \
    python3-picamera2 \
    libatlas-base-dev \
    bluez bluetooth rfkill

# 2. Dependências Python
echo "[2/6] Instalando dependências Python..."
pip3 install --break-system-packages \
    tflite-runtime \
    opencv-python-headless \
    numpy \
    RPi.GPIO \
    obd \
    pyyaml

# 3. Diretórios e permissões
echo "[3/6] Criando diretórios..."
install -d -m 755 "$INSTALL_DIR"
install -d -m 755 "$INSTALL_DIR/models/mobilenet_ssd"
install -d -m 755 "$LOG_DIR"

# 4. Usuário de serviço
echo "[4/6] Criando usuário de serviço '$SERVICE_USER'..."
id "$SERVICE_USER" &>/dev/null || useradd --system --no-create-home \
    --groups dialout,gpio,video,bluetooth "$SERVICE_USER"
chown "$SERVICE_USER":"$SERVICE_USER" "$LOG_DIR"

# 5. Copiar arquivos do projeto
echo "[5/6] Copiando arquivos para $INSTALL_DIR..."
cp -r adas config main.py "$INSTALL_DIR/"
chown -R "$SERVICE_USER":"$SERVICE_USER" "$INSTALL_DIR"

# 6. Instalar e ativar serviço systemd
echo "[6/6] Instalando serviço systemd..."
cp scripts/adas.service /etc/systemd/system/adas.service
systemctl daemon-reload
systemctl enable adas.service

echo ""
echo "=== Instalação concluída ==="
echo "Coloque o modelo TFLite em: $INSTALL_DIR/models/mobilenet_ssd/detect.tflite"
echo "Inicie com: sudo systemctl start adas"
echo "Logs:       sudo journalctl -u adas -f"
