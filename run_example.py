#!/usr/bin/env python3
"""
Exemplo de uso do Shorts Generator
"""

import os
import sys
from pathlib import Path

# Adicionar o diretório atual ao path
sys.path.append(str(Path(__file__).parent))

from src.main import ShortsGenerator


def main():
    """Exemplo de uso básico."""
    
    # Configurar chave da API (substitua pela sua chave)
    if not os.getenv('OPENAI_API_KEY'):
        print("⚠️  Configure a variável OPENAI_API_KEY antes de executar")
        print("Exemplo: export OPENAI_API_KEY='sua_chave_aqui'")
        return
    
    # Configurar FFmpeg para Windows (se necessário)
    if not os.getenv('FFMPEG_PATH') and sys.platform == 'win32':
        # Exemplo do caminho fornecido pelo usuário
        ffmpeg_path = r"D:\Projetos\Git\Python_Util\ffmpeg\bin\ffmpeg.exe"
        if Path(ffmpeg_path).exists():
            os.environ['FFMPEG_PATH'] = ffmpeg_path
            print(f"✅ FFmpeg configurado: {ffmpeg_path}")
        else:
            print("⚠️  FFmpeg não encontrado no caminho especificado")
    
    # Criar instância do gerador
    generator = ShortsGenerator()
    
    # Exemplos de uso:
    
    # 1. Processar vídeo local
    # video_path = "caminho/para/seu/video.mp4"
    # shorts = generator.generate_shorts(video_path)
    
    # 2. Processar vídeo do YouTube
    # youtube_url = "https://www.youtube.com/watch?v=VIDEO_ID"
    # shorts = generator.generate_shorts(youtube_url)
    
    # 3. Exemplo com arquivo de teste (substitua pelo seu arquivo)
    test_video = "test_video.mp4"
    
    if Path(test_video).exists():
        print(f"🎬 Processando vídeo: {test_video}")
        try:
            shorts = generator.generate_shorts(
                source=test_video,
                create_individual=True,
                create_compilation=True
            )
            
            if shorts:
                print(f"✅ {len(shorts)} shorts criados com sucesso!")
                for short in shorts:
                    print(f"   📹 {short}")
            else:
                print("❌ Nenhum short foi criado")
                
        except Exception as e:
            print(f"💥 Erro: {e}")
    else:
        print(f"❌ Arquivo de teste não encontrado: {test_video}")
        print("\n📝 Para usar este exemplo:")
        print("1. Coloque um arquivo de vídeo chamado 'test_video.mp4' neste diretório")
        print("2. Ou modifique a variável 'test_video' com o caminho do seu vídeo")
        print("3. Configure a variável OPENAI_API_KEY")
        print("4. Execute: python run_example.py")


if __name__ == "__main__":
    main()

