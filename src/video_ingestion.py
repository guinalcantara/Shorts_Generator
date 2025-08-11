import os
import subprocess
from pathlib import Path
from typing import Optional, Union
import yt_dlp
from config.settings import DATA_DIR, FFMPEG_PATH


class VideoIngestion:
    """Classe responsável por baixar e processar vídeos de entrada."""
    
    def __init__(self):
        self.data_dir = DATA_DIR
        
    def download_video(self, url: str, output_filename: Optional[str] = None) -> Path:
        """
        Baixa um vídeo de uma URL usando yt-dlp.
        
        Args:
            url: URL do vídeo ou live stream
            output_filename: Nome do arquivo de saída (opcional)
            
        Returns:
            Path: Caminho para o arquivo de vídeo baixado
        """
        if not output_filename:
            output_filename = "downloaded_video.%(ext)s"
            
        output_path = self.data_dir / output_filename
        
        ydl_opts = {
            'outtmpl': str(output_path),
            'format': 'best[height<=720]',  # Limita a qualidade para economizar espaço
            'writesubtitles': False,
            'writeautomaticsub': False,
        }
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
                
            # Encontrar o arquivo baixado (yt-dlp pode mudar a extensão)
            downloaded_files = list(self.data_dir.glob("downloaded_video.*"))
            if downloaded_files:
                return downloaded_files[0]
            else:
                raise FileNotFoundError("Arquivo de vídeo não encontrado após download")
                
        except Exception as e:
            raise Exception(f"Erro ao baixar vídeo: {str(e)}")
    
    def process_local_video(self, video_path: Union[str, Path]) -> Path:
        """
        Processa um arquivo de vídeo local, copiando-o para o diretório de dados.
        
        Args:
            video_path: Caminho para o arquivo de vídeo local
            
        Returns:
            Path: Caminho para o arquivo processado
        """
        video_path = Path(video_path)
        
        if not video_path.exists():
            raise FileNotFoundError(f"Arquivo de vídeo não encontrado: {video_path}")
            
        # Copiar para o diretório de dados
        output_path = self.data_dir / f"input_video{video_path.suffix}"
        
        try:
            # Usar ffmpeg para recodificar e garantir compatibilidade
            cmd = [
                FFMPEG_PATH, "-i", str(video_path),
                "-c:v", "libx264", "-c:a", "aac",
                "-y", str(output_path)
            ]
            
            subprocess.run(cmd, check=True, capture_output=True)
            return output_path
            
        except subprocess.CalledProcessError as e:
            raise Exception(f"Erro ao processar vídeo local: {e.stderr.decode()}")
    
    def get_video_info(self, video_path: Path) -> dict:
        """
        Obtém informações sobre o vídeo usando ffprobe.
        
        Args:
            video_path: Caminho para o arquivo de vídeo
            
        Returns:
            dict: Informações do vídeo (duração, resolução, etc.)
        """
        try:
            cmd = [
                "ffprobe", "-v", "quiet", "-print_format", "json",
                "-show_format", "-show_streams", str(video_path)
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            import json
            info = json.loads(result.stdout)
            
            # Extrair informações relevantes
            video_stream = next(
                (s for s in info['streams'] if s['codec_type'] == 'video'), None
            )
            
            if video_stream:
                duration = float(info['format']['duration'])
                width = video_stream['width']
                height = video_stream['height']
                
                return {
                    'duration': duration,
                    'width': width,
                    'height': height,
                    'format': info['format']['format_name']
                }
            else:
                raise Exception("Stream de vídeo não encontrado")
                
        except subprocess.CalledProcessError as e:
            raise Exception(f"Erro ao obter informações do vídeo: {e.stderr}")
        except json.JSONDecodeError:
            raise Exception("Erro ao decodificar informações do vídeo")
    
    def ingest_video(self, source: str) -> tuple[Path, dict]:
        """
        Método principal para ingestão de vídeo.
        
        Args:
            source: URL ou caminho para arquivo local
            
        Returns:
            tuple: (caminho_do_video, informações_do_video)
        """
        # Verificar se é URL ou arquivo local
        if source.startswith(('http://', 'https://', 'www.')):
            print(f"Baixando vídeo de: {source}")
            video_path = self.download_video(source)
        else:
            print(f"Processando vídeo local: {source}")
            video_path = self.process_local_video(source)
        
        # Obter informações do vídeo
        video_info = self.get_video_info(video_path)
        
        print(f"Vídeo processado: {video_path}")
        print(f"Duração: {video_info['duration']:.2f} segundos")
        print(f"Resolução: {video_info['width']}x{video_info['height']}")
        
        return video_path, video_info

