# 📦 Guia de Instalação Detalhado

Este guia fornece instruções passo a passo para instalar e configurar o Shorts Generator em diferentes sistemas operacionais.

## 🖥️ Requisitos do Sistema

### Requisitos Mínimos
- **Sistema Operacional**: Windows 10+, macOS 10.15+, ou Linux (Ubuntu 18.04+)
- **Python**: 3.11 ou superior
- **RAM**: 4GB mínimo, 8GB recomendado
- **Espaço em Disco**: 5GB livres (10GB+ recomendado)
- **Internet**: Conexão estável para download de modelos e vídeos

### Dependências Externas
- **FFmpeg**: Para processamento de áudio/vídeo
- **Git**: Para clonar o repositório
- **Docker** (opcional): Para instalação containerizada

## 🐳 Instalação com Docker (Recomendado)

### Pré-requisitos
1. Instale o Docker Desktop:
   - **Windows**: [Docker Desktop for Windows](https://docs.docker.com/desktop/windows/install/)
   - **macOS**: [Docker Desktop for Mac](https://docs.docker.com/desktop/mac/install/)
   - **Linux**: [Docker Engine](https://docs.docker.com/engine/install/)

2. Instale o Docker Compose (geralmente incluído no Docker Desktop)

### Passos de Instalação

```bash
# 1. Clone o repositório
git clone <repository-url>
cd shorts_generator

# 2. Configure as variáveis de ambiente
cp .env.example .env

# 3. Edite o arquivo .env com suas configurações
# No Windows: use notepad .env
# No Linux/Mac: use nano .env ou vim .env

# 4. Construa e execute o container
docker-compose up -d

# 5. Verifique se está funcionando
docker-compose exec shorts-generator python src/main.py --help
```

### Configuração do .env para Docker

```env
# Obrigatório
OPENAI_API_KEY=sua_chave_openai_aqui

# Opcional (já configurado no Docker)
OPENAI_API_BASE=https://api.openai.com/v1
FFMPEG_PATH=/usr/bin/ffmpeg
```

## 💻 Instalação Local

### Windows

#### 1. Instalar Python
```powershell
# Baixe Python 3.11+ de https://python.org
# Durante a instalação, marque "Add Python to PATH"

# Verifique a instalação
python --version
pip --version
```

#### 2. Instalar Git
```powershell
# Baixe Git de https://git-scm.com/download/win
# Use as configurações padrão durante a instalação
```

#### 3. Configurar FFmpeg
```powershell
# Opção A: Usar FFmpeg pré-compilado (como mencionado pelo usuário)
# Se você já tem FFmpeg em D:\Projetos\Git\Python_Util\ffmpeg\bin
# Configure no .env:
# FFMPEG_PATH=D:\Projetos\Git\Python_Util\ffmpeg\bin\ffmpeg.exe

# Opção B: Baixar FFmpeg
# 1. Baixe de https://ffmpeg.org/download.html#build-windows
# 2. Extraia para C:\ffmpeg
# 3. Adicione C:\ffmpeg\bin ao PATH do sistema
```

#### 4. Instalar o Projeto
```powershell
# Clone o repositório
git clone <repository-url>
cd shorts_generator

# Crie ambiente virtual
python -m venv venv
venv\Scripts\activate

# Instale dependências
pip install -r requirements.txt

# Configure variáveis de ambiente
copy .env.example .env
# Edite .env com notepad ou seu editor preferido
```

### macOS

#### 1. Instalar Homebrew (se não tiver)
```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

#### 2. Instalar dependências
```bash
# Instalar Python, Git e FFmpeg
brew install python@3.11 git ffmpeg

# Verificar instalações
python3 --version
git --version
ffmpeg -version
```

#### 3. Instalar o projeto
```bash
# Clone o repositório
git clone <repository-url>
cd shorts_generator

# Crie ambiente virtual
python3 -m venv venv
source venv/bin/activate

# Instale dependências
pip install -r requirements.txt

# Configure variáveis de ambiente
cp .env.example .env
# Edite .env com nano, vim ou seu editor preferido
```

### Linux (Ubuntu/Debian)

#### 1. Atualizar sistema e instalar dependências
```bash
# Atualizar repositórios
sudo apt update

# Instalar Python, Git e FFmpeg
sudo apt install python3.11 python3.11-venv python3-pip git ffmpeg

# Verificar instalações
python3.11 --version
git --version
ffmpeg -version
```

#### 2. Instalar o projeto
```bash
# Clone o repositório
git clone <repository-url>
cd shorts_generator

# Crie ambiente virtual
python3.11 -m venv venv
source venv/bin/activate

# Instale dependências
pip install -r requirements.txt

# Configure variáveis de ambiente
cp .env.example .env
nano .env  # ou vim .env
```

## 🔑 Configuração da API OpenAI

### Obter Chave da API
1. Acesse [OpenAI Platform](https://platform.openai.com/)
2. Faça login ou crie uma conta
3. Vá para [API Keys](https://platform.openai.com/api-keys)
4. Clique em "Create new secret key"
5. Copie a chave gerada

### Configurar no Projeto

#### Opção 1: Arquivo .env (Recomendado)
```env
OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

#### Opção 2: Variável de Ambiente
```bash
# Windows (PowerShell)
$env:OPENAI_API_KEY="sk-proj-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"

# Windows (CMD)
set OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# Linux/Mac
export OPENAI_API_KEY="sk-proj-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
```

## ✅ Verificação da Instalação

### Teste Básico
```bash
# Ativar ambiente virtual (se instalação local)
# Windows: venv\Scripts\activate
# Linux/Mac: source venv/bin/activate

# Testar ajuda
python src/main.py --help

# Testar configurações
python -c "
import os
from config.settings import OPENAI_API_KEY, FFMPEG_PATH
print(f'OpenAI API Key: {\"✅ Configurada\" if OPENAI_API_KEY else \"❌ Não configurada\"}')
print(f'FFmpeg Path: {FFMPEG_PATH}')
"
```

### Teste com Vídeo de Exemplo
```bash
# Baixe um vídeo curto de teste
# Ou use um arquivo local pequeno

python src/main.py "caminho/para/video_teste.mp4" --keep-temp
```

## 🔧 Solução de Problemas

### Erro: "python não é reconhecido"
**Windows:**
```powershell
# Reinstale Python marcando "Add to PATH"
# Ou adicione manualmente ao PATH:
# C:\Users\SeuUsuario\AppData\Local\Programs\Python\Python311\
```

### Erro: "ffmpeg não encontrado"
```bash
# Verifique se FFmpeg está no PATH
ffmpeg -version

# Se não estiver, configure FFMPEG_PATH no .env
```

### Erro: "ModuleNotFoundError"
```bash
# Certifique-se de que o ambiente virtual está ativo
# Reinstale dependências
pip install --upgrade pip
pip install -r requirements.txt
```

### Erro: "OpenAI API Key não configurada"
```bash
# Verifique se a chave está no .env
cat .env | grep OPENAI_API_KEY

# Ou configure como variável de ambiente
export OPENAI_API_KEY="sua_chave_aqui"
```

## 🚀 Próximos Passos

Após a instalação bem-sucedida:

1. **Leia o README.md** para entender como usar o projeto
2. **Execute o exemplo** com `python run_example.py`
3. **Teste com seus vídeos** usando `python src/main.py "seu_video.mp4"`
4. **Explore as configurações** em `config/settings.py`

## 📞 Suporte

Se encontrar problemas durante a instalação:

1. Verifique os logs de erro
2. Consulte a seção de troubleshooting no README.md
3. Certifique-se de que todas as dependências estão instaladas
4. Abra uma issue no repositório com detalhes do erro

---

**🎉 Instalação concluída! Agora você pode começar a gerar shorts incríveis! 🎬**

