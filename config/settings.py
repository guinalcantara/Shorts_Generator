import os
from pathlib import Path

# Configurações do projeto
PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data"
OUTPUT_DIR = PROJECT_ROOT / "output"

# FFmpeg configuration
FFMPEG_PATH = os.getenv("FFMPEG_PATH", "ffmpeg")  # Default to system PATH

# OpenAI API configuration (para GPT-5 nano ou similar)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_API_BASE = os.getenv("OPENAI_API_BASE", "https://api.openai.com/v1")

# Configurações de processamento
MAX_VIDEO_DURATION = 3600  # 1 hora em segundos
CHUNK_DURATION = 300  # 5 minutos por chunk para processamento
SHORT_DURATION = 60  # Duração máxima do short em segundos
MIN_MOMENT_DURATION = 10  # Duração mínima de um momento engraçado

# Configurações de transcrição
WHISPER_MODEL = "base"  # Modelo do Whisper para transcrição

# Configurações do LLM
LLM_MODEL = "gpt-4o-mini"  # Modelo para identificar momentos engraçados
LLM_TEMPERATURE = 0.7
LLM_MAX_TOKENS = 1000

# Criar diretórios se não existirem
DATA_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(exist_ok=True)

