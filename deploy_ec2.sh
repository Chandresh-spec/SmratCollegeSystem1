#!/bin/bash
# ==============================================================================
# Smart College System - Automated AWS EC2 Deployment Script (Ubuntu)
# ==============================================================================
set -e

echo ">>> Updating system packages..."
sudo apt-get update -y && sudo apt-get upgrade -y

echo ">>> Installing Docker & Docker Compose..."
sudo apt-get install -y ca-certificates curl gnupg lsb-release

if ! command -v docker &> /dev/null; then
    sudo mkdir -p /etc/apt/keyrings
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
    echo \
      "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
      $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
    sudo apt-get update -y
    sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin
    sudo usermod -aG docker $USER
fi

echo ">>> Setting up environment..."
if [ ! -f .env ]; then
    cp .env.example .env
    echo "[!] Created .env file from .env.example. Please update your credentials."
fi

echo ">>> Building and starting containers..."
sudo docker compose down || true
sudo docker compose up --build -d

echo "=============================================================================="
echo ">>> SUCCESS! The application is running on port 8000."
echo ">>> You can access it via: http://<YOUR_EC2_PUBLIC_IP>:8000"
echo "=============================================================================="
