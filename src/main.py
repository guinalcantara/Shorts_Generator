#!/usr/bin/env python3
"""
Shorts Generator - Gerador de Shorts de Lives
Versão simplificada para identificar momentos engraçados usando LLM
"""

import argparse
import sys
from pathlib import Path
from typing import Optional

# Adicionar o diretório pai ao path para imports
sys.path.append(str(Path(__file__).parent.parent))

import os 
from dotenv import load_dotenv

# Carregar variáveis do arquivo .env
load_dotenv()

from src.video_ingestion import VideoIngestion
from src.audio_processor import AudioProcessor
from src.moment_identifier import MomentIdentifier
from src.video_editor import VideoEditor
from config.settings import OUTPUT_DIR, DATA_DIR


class ShortsGenerator:
    """Classe principal que orquestra todo o processo de geração de shorts."""
    
    def __init__(self):
        self.video_ingestion = VideoIngestion()
        self.audio_processor = AudioProcessor()
        self.moment_identifier = MomentIdentifier()
        self.video_editor = VideoEditor()
    
    def generate_shorts(self, source: str, create_individual: bool = True, 
                       create_compilation: bool = True) -> list[Path]:
        """
        Método principal para gerar shorts a partir de uma fonte de vídeo.
        
        Args:
            source: URL ou caminho para arquivo de vídeo
            create_individual: Se deve criar shorts individuais
            create_compilation: Se deve criar short de compilação
            
        Returns:
            List[Path]: Lista de caminhos para os shorts criados
        """
        try:
            print("🎬 Iniciando geração de shorts...")
            print(f"📹 Fonte: {source}")
            
            # 1. Ingestão de vídeo
            print("\n📥 Etapa 1: Processando vídeo...")
            video_path, video_info = self.video_ingestion.ingest_video(source)
            
            # Verificar duração do vídeo
            if video_info['duration'] > 7200:  # 2 horas
                print("⚠️  Aviso: Vídeo muito longo. Considere usar um segmento menor.")
            
            # 2. Processamento de áudio e transcrição
            print("\n🎵 Etapa 2: Extraindo áudio e gerando transcrição...")
            segments, transcription_file = self.audio_processor.process_audio(video_path)
            
            if not segments:
                raise Exception("Não foi possível gerar transcrição do áudio")
            
            # 3. Identificação de momentos engraçados
            print("\n🤖 Etapa 3: Identificando momentos engraçados com IA...")
            funny_moments = self.moment_identifier.identify_moments(segments)
            
            if not funny_moments:
                print("❌ Nenhum momento engraçado foi identificado.")
                return []
            
            # Mostrar momentos encontrados
            print(f"\n✨ Encontrados {len(funny_moments)} momentos interessantes:")
            for i, moment in enumerate(funny_moments[:5], 1):
                duration = moment['duration']
                priority = moment['priority']
                print(f"  {i}. {moment['title']} ({duration:.1f}s) - Prioridade: {priority}/10")
            
            # 4. Criação dos shorts
            print("\n✂️  Etapa 4: Criando shorts...")
            created_shorts = self.video_editor.create_shorts(
                video_path, funny_moments, create_individual, create_compilation
            )
            
            # Resultados finais
            print(f"\n🎉 Processo concluído!")
            print(f"📁 Shorts criados em: {OUTPUT_DIR}")
            print(f"📊 Total de shorts: {len(created_shorts)}")
            
            for short_path in created_shorts:
                print(f"   - {short_path.name}")
            
            return created_shorts
            
        except Exception as e:
            print(f"\n❌ Erro durante o processamento: {str(e)}")
            raise
    
    def cleanup_temp_files(self):
        """Remove arquivos temporários."""
        try:
            temp_files = [
                DATA_DIR / "downloaded_video.*",
                DATA_DIR / "input_video.*",
                DATA_DIR / "extracted_audio.wav",
            ]
            
            for pattern in temp_files:
                for file_path in DATA_DIR.glob(pattern.name):
                    if file_path.exists():
                        file_path.unlink()
                        print(f"🗑️  Removido: {file_path.name}")
                        
        except Exception as e:
            print(f"⚠️  Erro ao limpar arquivos temporários: {e}")


def main():
    """Função principal da aplicação."""
    parser = argparse.ArgumentParser(
        description="Gerador de Shorts de Lives - Identifica momentos engraçados usando IA"
    )
    
    parser.add_argument(
        "source",
        help="URL do vídeo/live ou caminho para arquivo local"
    )
    
    parser.add_argument(
        "--no-individual",
        action="store_true",
        help="Não criar shorts individuais"
    )
    
    parser.add_argument(
        "--no-compilation",
        action="store_true",
        help="Não criar short de compilação"
    )
    
    parser.add_argument(
        "--keep-temp",
        action="store_true",
        help="Manter arquivos temporários"
    )
    
    parser.add_argument(
        "--output-dir",
        type=str,
        help="Diretório de saída personalizado"
    )
    
    args = parser.parse_args()
    
    # Configurar diretório de saída personalizado
    if args.output_dir:
        global OUTPUT_DIR
        OUTPUT_DIR = Path(args.output_dir)
        OUTPUT_DIR.mkdir(exist_ok=True)
    
    # Verificar se as chaves de API estão configuradas
    from config.settings import OPENAI_API_KEY
    if not OPENAI_API_KEY:
        print("❌ Erro: OPENAI_API_KEY não configurada.")
        print("Configure a variável de ambiente OPENAI_API_KEY antes de executar.")
        sys.exit(1)
    
    # Criar instância do gerador
    generator = ShortsGenerator()
    
    try:
        # Gerar shorts
        created_shorts = generator.generate_shorts(
            source=args.source,
            create_individual=not args.no_individual,
            create_compilation=not args.no_compilation
        )
        
        if created_shorts:
            print(f"\n✅ Sucesso! {len(created_shorts)} shorts criados.")
        else:
            print("\n⚠️  Nenhum short foi criado.")
            
    except KeyboardInterrupt:
        print("\n⏹️  Processo interrompido pelo usuário.")
        sys.exit(1)
        
    except Exception as e:
        print(f"\n💥 Erro fatal: {str(e)}")
        sys.exit(1)
        
    finally:
        # Limpar arquivos temporários
        if not args.keep_temp:
            generator.cleanup_temp_files()


if __name__ == "__main__":
    main()

