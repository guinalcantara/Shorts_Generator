# Use Python 3.11 como base
FROM python:3.11-slim

# Definir variáveis de ambiente
ENV PYTHONUNBUFFERED=1
ENV DEBIAN_FRONTEND=noninteractive

# Instalar dependências do sistema
RUN apt-get update && apt-get install -y \
    ffmpeg \
    git \
    wget \
    curl \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Criar diretório de trabalho
WORKDIR /app

# Copiar arquivos de dependências
COPY requirements.txt .

# Instalar dependências Python
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código fonte
COPY . .

# Criar diretórios necessários
RUN mkdir -p data output

# Definir variável de ambiente para FFmpeg
ENV FFMPEG_PATH=/usr/bin/ffmpeg

# Expor porta (se necessário para futuras extensões)
EXPOSE 8000

# Comando padrão
CMD ["python", "src/main.py", "--help"]

