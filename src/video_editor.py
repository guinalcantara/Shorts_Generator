import subprocess
from pathlib import Path
from typing import List, Dict, Any, Optional
from moviepy.editor import VideoFileClip, concatenate_videoclips, CompositeVideoClip, TextClip
from config.settings import DATA_DIR, OUTPUT_DIR, FFMPEG_PATH, SHORT_DURATION


class VideoEditor:
    """Classe responsável por editar e criar os shorts de vídeo."""
    
    def __init__(self):
        self.data_dir = DATA_DIR
        self.output_dir = OUTPUT_DIR
        
    def extract_video_segment(self, video_path: Path, start_time: float, end_time: float) -> VideoFileClip:
        """
        Extrai um segmento específico do vídeo.
        
        Args:
            video_path: Caminho para o arquivo de vídeo
            start_time: Tempo de início em segundos
            end_time: Tempo de fim em segundos
            
        Returns:
            VideoFileClip: Clipe do segmento extraído
        """
        try:
            clip = VideoFileClip(str(video_path))
            segment = clip.subclip(start_time, end_time)
            return segment
            
        except Exception as e:
            raise Exception(f"Erro ao extrair segmento: {str(e)}")
    
    def add_text_overlay(self, clip: VideoFileClip, text: str, position: str = 'bottom') -> CompositeVideoClip:
        """
        Adiciona texto sobreposto ao vídeo.
        
        Args:
            clip: Clipe de vídeo
            text: Texto a ser adicionado
            position: Posição do texto ('top', 'bottom', 'center')
            
        Returns:
            CompositeVideoClip: Clipe com texto sobreposto
        """
        try:
            # Configurações do texto
            txt_clip = TextClip(
                text,
                fontsize=50,
                color='white',
                font='Arial-Bold',
                stroke_color='black',
                stroke_width=2
            ).set_duration(clip.duration)
            
            # Posicionamento
            if position == 'top':
                txt_clip = txt_clip.set_position(('center', 50))
            elif position == 'bottom':
                txt_clip = txt_clip.set_position(('center', clip.h - 100))
            else:  # center
                txt_clip = txt_clip.set_position('center')
            
            # Compor vídeo com texto
            final_clip = CompositeVideoClip([clip, txt_clip])
            return final_clip
            
        except Exception as e:
            print(f"Aviso: Erro ao adicionar texto: {str(e)}")
            return clip  # Retorna o clipe original se falhar
    
    def resize_for_shorts(self, clip: VideoFileClip, target_resolution: tuple = (1080, 1920)) -> VideoFileClip:
        """
        Redimensiona o vídeo para formato de shorts (vertical).
        
        Args:
            clip: Clipe de vídeo
            target_resolution: Resolução alvo (largura, altura)
            
        Returns:
            VideoFileClip: Clipe redimensionado
        """
        try:
            # Calcular escala para manter proporção
            original_w, original_h = clip.w, clip.h
            target_w, target_h = target_resolution
            
            # Escalar para preencher a altura
            scale = target_h / original_h
            new_w = int(original_w * scale)
            
            # Redimensionar
            resized_clip = clip.resize(height=target_h)
            
            # Se a largura for maior que o alvo, cortar o centro
            if new_w > target_w:
                x_center = new_w // 2
                x_start = x_center - (target_w // 2)
                resized_clip = resized_clip.crop(x1=x_start, x2=x_start + target_w)
            
            return resized_clip
            
        except Exception as e:
            raise Exception(f"Erro ao redimensionar vídeo: {str(e)}")
    
    def create_short_from_moment(self, video_path: Path, moment: Dict[str, Any], 
                                output_filename: Optional[str] = None) -> Path:
        """
        Cria um short a partir de um momento identificado.
        
        Args:
            video_path: Caminho para o vídeo original
            moment: Dicionário com informações do momento
            output_filename: Nome do arquivo de saída (opcional)
            
        Returns:
            Path: Caminho para o short criado
        """
        if not output_filename:
            safe_title = "".join(c for c in moment['title'] if c.isalnum() or c in (' ', '-', '_')).rstrip()
            output_filename = f"short_{safe_title[:30]}.mp4"
        
        output_path = self.output_dir / output_filename
        
        try:
            # Extrair segmento
            clip = self.extract_video_segment(
                video_path, 
                moment['start'], 
                moment['end']
            )
            
            # Redimensionar para formato de shorts
            clip = self.resize_for_shorts(clip)
            
            # Adicionar texto com título do momento
            if moment.get('title'):
                clip = self.add_text_overlay(clip, moment['title'], 'top')
            
            # Limitar duração se necessário
            if clip.duration > SHORT_DURATION:
                clip = clip.subclip(0, SHORT_DURATION)
            
            # Exportar vídeo
            print(f"Criando short: {output_filename}")
            clip.write_videofile(
                str(output_path),
                codec='libx264',
                audio_codec='aac',
                temp_audiofile='temp-audio.m4a',
                remove_temp=True,
                verbose=False,
                logger=None
            )
            
            # Limpar recursos
            clip.close()
            
            print(f"Short criado: {output_path}")
            return output_path
            
        except Exception as e:
            raise Exception(f"Erro ao criar short: {str(e)}")
    
    def create_compilation_short(self, video_path: Path, moments: List[Dict[str, Any]], 
                               max_duration: float = SHORT_DURATION) -> Path:
        """
        Cria um short de compilação com múltiplos momentos.
        
        Args:
            video_path: Caminho para o vídeo original
            moments: Lista de momentos a serem incluídos
            max_duration: Duração máxima do short
            
        Returns:
            Path: Caminho para o short de compilação
        """
        output_path = self.output_dir / "compilation_short.mp4"
        
        try:
            clips = []
            total_duration = 0
            
            # Ordenar momentos por prioridade
            sorted_moments = sorted(moments, key=lambda x: x['priority'], reverse=True)
            
            for moment in sorted_moments:
                if total_duration >= max_duration:
                    break
                
                # Calcular duração disponível
                remaining_time = max_duration - total_duration
                moment_duration = min(moment['duration'], remaining_time)
                
                # Extrair segmento
                clip = self.extract_video_segment(
                    video_path,
                    moment['start'],
                    moment['start'] + moment_duration
                )
                
                # Redimensionar
                clip = self.resize_for_shorts(clip)
                
                # Adicionar texto
                if moment.get('title'):
                    clip = self.add_text_overlay(clip, moment['title'], 'bottom')
                
                clips.append(clip)
                total_duration += moment_duration
            
            if not clips:
                raise Exception("Nenhum clipe válido para compilação")
            
            # Concatenar clipes
            final_clip = concatenate_videoclips(clips, method="compose")
            
            # Exportar
            print("Criando short de compilação...")
            final_clip.write_videofile(
                str(output_path),
                codec='libx264',
                audio_codec='aac',
                temp_audiofile='temp-audio.m4a',
                remove_temp=True,
                verbose=False,
                logger=None
            )
            
            # Limpar recursos
            for clip in clips:
                clip.close()
            final_clip.close()
            
            print(f"Short de compilação criado: {output_path}")
            return output_path
            
        except Exception as e:
            raise Exception(f"Erro ao criar compilação: {str(e)}")
    
    def create_shorts(self, video_path: Path, moments: List[Dict[str, Any]], 
                     create_individual: bool = True, create_compilation: bool = True) -> List[Path]:
        """
        Método principal para criar shorts.
        
        Args:
            video_path: Caminho para o vídeo original
            moments: Lista de momentos identificados
            create_individual: Se deve criar shorts individuais
            create_compilation: Se deve criar short de compilação
            
        Returns:
            List[Path]: Lista de caminhos para os shorts criados
        """
        created_shorts = []
        
        if not moments:
            print("Nenhum momento engraçado encontrado para criar shorts")
            return created_shorts
        
        try:
            # Criar shorts individuais
            if create_individual:
                print(f"Criando {len(moments)} shorts individuais...")
                for i, moment in enumerate(moments[:5]):  # Limitar a 5 shorts
                    try:
                        short_path = self.create_short_from_moment(
                            video_path, moment, f"short_{i+1:02d}.mp4"
                        )
                        created_shorts.append(short_path)
                    except Exception as e:
                        print(f"Erro ao criar short {i+1}: {e}")
            
            # Criar compilação
            if create_compilation and len(moments) > 1:
                try:
                    compilation_path = self.create_compilation_short(video_path, moments)
                    created_shorts.append(compilation_path)
                except Exception as e:
                    print(f"Erro ao criar compilação: {e}")
            
            print(f"Total de shorts criados: {len(created_shorts)}")
            return created_shorts
            
        except Exception as e:
            raise Exception(f"Erro geral na criação de shorts: {str(e)}")

