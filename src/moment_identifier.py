import json
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional
from openai import OpenAI
from config.settings import (
    OPENAI_API_KEY, OPENAI_API_BASE, LLM_MODEL, 
    LLM_TEMPERATURE, LLM_MAX_TOKENS, MIN_MOMENT_DURATION
)


class MomentIdentifier:
    """Classe responsável por identificar momentos engraçados usando LLM."""
    
    def __init__(self):
        self.client = OpenAI(
            api_key=OPENAI_API_KEY,
            base_url=OPENAI_API_BASE
        )
        
    def analyze_segments(self, segments: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Analisa os segmentos de transcrição para identificar momentos engraçados.
        
        Args:
            segments: Lista de segmentos da transcrição
            
        Returns:
            List: Lista de momentos engraçados identificados
        """
        # Preparar o texto para análise
        full_text = self._prepare_text_for_analysis(segments)
        
        # Criar prompt para o LLM
        prompt = self._create_analysis_prompt(full_text)
        
        try:
            print("Analisando transcrição com LLM...")
            response = self.client.chat.completions.create(
                model=LLM_MODEL,
                messages=[
                    {
                        "role": "system",
                        "content": "Você é um especialista em identificar momentos engraçados e interessantes em transmissões ao vivo e vídeos. Sua tarefa é analisar transcrições e identificar os melhores momentos para criar shorts virais."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=LLM_TEMPERATURE,
                max_tokens=LLM_MAX_TOKENS,
                response_format={"type": "json_object"}
            )
            
            # Processar resposta
            analysis_result = json.loads(response.choices[0].message.content)
            
            # Converter para formato interno
            funny_moments = self._process_llm_response(analysis_result, segments)
            
            print(f"Identificados {len(funny_moments)} momentos engraçados")
            return funny_moments
            
        except Exception as e:
            raise Exception(f"Erro na análise com LLM: {str(e)}")
    
    def _prepare_text_for_analysis(self, segments: List[Dict[str, Any]]) -> str:
        """Prepara o texto da transcrição para análise."""
        text_with_timestamps = []
        
        for i, segment in enumerate(segments):
            start_time = self._format_timestamp(segment['start'])
            text_with_timestamps.append(f"[{start_time}] {segment['text']}")
        
        return "\n".join(text_with_timestamps)
    
    def _create_analysis_prompt(self, text: str) -> str:
        """Cria o prompt para análise do LLM."""
        return f"""
Analise a seguinte transcrição de uma transmissão ao vivo e identifique os momentos mais engraçados, interessantes ou virais que seriam ideais para criar shorts de vídeo.

TRANSCRIÇÃO:
{text}

INSTRUÇÕES:
1. Identifique momentos que sejam:
   - Engraçados ou cômicos
   - Surpreendentes ou inesperados
   - Emocionalmente impactantes
   - Que gerem reações fortes
   - Que tenham potencial viral

2. Para cada momento identificado, forneça:
   - Timestamp de início (formato HH:MM:SS)
   - Timestamp de fim (formato HH:MM:SS)
   - Título/descrição do momento
   - Razão pela qual é interessante
   - Nível de prioridade (1-10, sendo 10 o mais viral)

3. Priorize momentos com duração entre 10-60 segundos.

4. Retorne a resposta em formato JSON com a seguinte estrutura:
{{
    "moments": [
        {{
            "start_time": "HH:MM:SS",
            "end_time": "HH:MM:SS",
            "title": "Título do momento",
            "description": "Descrição detalhada",
            "reason": "Por que é engraçado/interessante",
            "priority": 8,
            "tags": ["tag1", "tag2"]
        }}
    ],
    "summary": "Resumo geral da análise"
}}
"""
    
    def _process_llm_response(self, analysis_result: Dict[str, Any], segments: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Processa a resposta do LLM e converte para formato interno."""
        funny_moments = []
        
        for moment in analysis_result.get('moments', []):
            try:
                # Converter timestamps para segundos
                start_seconds = self._timestamp_to_seconds(moment['start_time'])
                end_seconds = self._timestamp_to_seconds(moment['end_time'])
                
                # Validar duração mínima
                duration = end_seconds - start_seconds
                if duration < MIN_MOMENT_DURATION:
                    continue
                
                # Encontrar segmentos correspondentes
                relevant_segments = self._find_segments_in_range(
                    segments, start_seconds, end_seconds
                )
                
                funny_moment = {
                    'start': start_seconds,
                    'end': end_seconds,
                    'duration': duration,
                    'title': moment.get('title', 'Momento Engraçado'),
                    'description': moment.get('description', ''),
                    'reason': moment.get('reason', ''),
                    'priority': moment.get('priority', 5),
                    'tags': moment.get('tags', []),
                    'segments': relevant_segments
                }
                
                funny_moments.append(funny_moment)
                
            except Exception as e:
                print(f"Erro ao processar momento: {e}")
                continue
        
        # Ordenar por prioridade
        funny_moments.sort(key=lambda x: x['priority'], reverse=True)
        
        return funny_moments
    
    def _find_segments_in_range(self, segments: List[Dict[str, Any]], start: float, end: float) -> List[Dict[str, Any]]:
        """Encontra segmentos que estão dentro do range de tempo especificado."""
        relevant_segments = []
        
        for segment in segments:
            # Verifica se o segmento tem sobreposição com o range
            if (segment['start'] < end and segment['end'] > start):
                relevant_segments.append(segment)
        
        return relevant_segments
    
    def _timestamp_to_seconds(self, timestamp: str) -> float:
        """Converte timestamp HH:MM:SS para segundos."""
        try:
            parts = timestamp.split(':')
            if len(parts) == 3:
                hours, minutes, seconds = map(float, parts)
                return hours * 3600 + minutes * 60 + seconds
            elif len(parts) == 2:
                minutes, seconds = map(float, parts)
                return minutes * 60 + seconds
            else:
                return float(parts[0])
        except:
            return 0.0
    
    def _format_timestamp(self, seconds: float) -> str:
        """Formata timestamp em formato HH:MM:SS."""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"
    
    def save_analysis_results(self, moments: List[Dict[str, Any]], output_path: Optional[Path] = None) -> Path:
        """Salva os resultados da análise em um arquivo JSON."""
        if not output_path:
            from config.settings import DATA_DIR
            output_path = DATA_DIR / "funny_moments.json"
        
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump({
                    'moments': moments,
                    'total_moments': len(moments),
                    'analysis_timestamp': str(datetime.now())
                }, f, indent=2, ensure_ascii=False)
            
            print(f"Análise salva: {output_path}")
            return output_path
            
        except Exception as e:
            raise Exception(f"Erro ao salvar análise: {str(e)}")
    
    def identify_moments(self, segments: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Método principal para identificar momentos engraçados.
        
        Args:
            segments: Lista de segmentos da transcrição
            
        Returns:
            List: Lista de momentos engraçados identificados
        """
        moments = self.analyze_segments(segments)
        
        # Salvar resultados
        self.save_analysis_results(moments)
        
        return moments

