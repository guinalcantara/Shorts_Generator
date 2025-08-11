import subprocess
import whisper
from pathlib import Path
from typing import List, Dict, Any, Optional
from config.settings import DATA_DIR, FFMPEG_PATH, WHISPER_MODEL


class AudioProcessor:
    """Classe responsável por extrair áudio e gerar transcrições."""
    
    def __init__(self):
        self.data_dir = DATA_DIR
        self.whisper_model = whisper.load_model(WHISPER_MODEL)
        
    def extract_audio(self, video_path: Path, audio_path: Optional[Path] = None) -> Path:
        """
        Extrai o áudio de um arquivo de vídeo.
        
        Args:
            video_path: Caminho para o arquivo de vídeo
            audio_path: Caminho de saída para o áudio (opcional)
            
        Returns:
            Path: Caminho para o arquivo de áudio extraído
        """
        if not audio_path:
            audio_path = self.data_dir / "extracted_audio.wav"
            
        try:
            cmd = [
                FFMPEG_PATH, "-i", str(video_path),
                "-vn",  # Sem vídeo
                "-acodec", "pcm_s16le",  # Codec de áudio WAV
                "-ar", "16000",  # Sample rate 16kHz (recomendado para Whisper)
                "-ac", "1",  # Mono
                "-y", str(audio_path)
            ]
            
            subprocess.run(cmd, check=True, capture_output=True)
            print(f"Áudio extraído: {audio_path}")
            return audio_path
            
        except subprocess.CalledProcessError as e:
            raise Exception(f"Erro ao extrair áudio: {e.stderr.decode()}")
    
    def transcribe_audio(self, audio_path: Path) -> Dict[str, Any]:
        """
        Transcreve o áudio usando Whisper.
        
        Args:
            audio_path: Caminho para o arquivo de áudio
            
        Returns:
            Dict: Resultado da transcrição com timestamps
        """
        try:
            print("Iniciando transcrição do áudio...")
            result = self.whisper_model.transcribe(
                str(audio_path),
                word_timestamps=True,
                verbose=False
            )
            
            print(f"Transcrição concluída. Texto: {len(result['text'])} caracteres")
            return result
            
        except Exception as e:
            raise Exception(f"Erro na transcrição: {str(e)}")
    
    def format_transcription(self, transcription_result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Formata o resultado da transcrição em segmentos com timestamps.
        
        Args:
            transcription_result: Resultado bruto do Whisper
            
        Returns:
            List: Lista de segmentos formatados
        """
        segments = []
        
        for segment in transcription_result.get('segments', []):
            formatted_segment = {
                'start': segment['start'],
                'end': segment['end'],
                'text': segment['text'].strip(),
                'duration': segment['end'] - segment['start']
            }
            segments.append(formatted_segment)
        
        return segments
    
    def save_transcription(self, segments: List[Dict[str, Any]], output_path: Optional[Path] = None) -> Path:
        """
        Salva a transcrição em um arquivo de texto.
        
        Args:
            segments: Lista de segmentos da transcrição
            output_path: Caminho de saída (opcional)
            
        Returns:
            Path: Caminho do arquivo salvo
        """
        if not output_path:
            output_path = self.data_dir / "transcription.txt"
            
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write("TRANSCRIÇÃO DO VÍDEO\n")
                f.write("=" * 50 + "\n\n")
                
                for segment in segments:
                    start_time = self._format_timestamp(segment['start'])
                    end_time = self._format_timestamp(segment['end'])
                    
                    f.write(f"[{start_time} - {end_time}] {segment['text']}\n")
                
                f.write("\n" + "=" * 50 + "\n")
                f.write("TEXTO COMPLETO\n")
                f.write("=" * 50 + "\n\n")
                
                full_text = " ".join([seg['text'] for seg in segments])
                f.write(full_text)
            
            print(f"Transcrição salva: {output_path}")
            return output_path
            
        except Exception as e:
            raise Exception(f"Erro ao salvar transcrição: {str(e)}")
    
    def _format_timestamp(self, seconds: float) -> str:
        """Formata timestamp em formato HH:MM:SS."""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"
    
    def process_audio(self, video_path: Path) -> tuple[List[Dict[str, Any]], Path]:
        """
        Método principal para processar áudio: extração + transcrição.
        
        Args:
            video_path: Caminho para o arquivo de vídeo
            
        Returns:
            tuple: (segmentos_da_transcrição, caminho_do_arquivo_de_transcrição)
        """
        # Extrair áudio
        audio_path = self.extract_audio(video_path)
        
        # Transcrever áudio
        transcription_result = self.transcribe_audio(audio_path)
        
        # Formatar segmentos
        segments = self.format_transcription(transcription_result)
        
        # Salvar transcrição
        transcription_file = self.save_transcription(segments)
        
        return segments, transcription_file

