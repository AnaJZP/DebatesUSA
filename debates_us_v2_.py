# -*- coding: utf-8 -*-
"""Debates US V2 .ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1Tw8CtORCl_ebcVuf9SssPDqKo6O_PWyU
"""

!pip install --upgrade pip setuptools wheel

!pip install transformers
!pip install torch
!pip install pandas
!pip install numpy
!pip install scipy
!pip install sklearn

import pandas as pd
import numpy as np
from transformers import (
    BertTokenizer,
    BertModel,
    AutoTokenizer,
    AutoModelForSequenceClassification,
    pipeline
)
import torch
from sklearn.metrics.pairwise import cosine_similarity
import re
from tqdm import tqdm
import seaborn as sns
import matplotlib.pyplot as plt

class DebateAnalyzer:
    def __init__(self):
        # Inicializar modelos BERT y RoBERTa
        self.bert_tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
        self.bert_model = BertModel.from_pretrained('bert-base-uncased')
        self.sentiment_analyzer = pipeline(
            "sentiment-analysis",
            model="cardiffnlp/twitter-roberta-base-sentiment",
            tokenizer="cardiffnlp/twitter-roberta-base-sentiment"
        )

    def preprocess_text(self, text):
        """Preprocesamiento avanzado del texto."""
        # Limpieza básica
        text = re.sub(r'\[.*?\]', '', text)
        text = re.sub(r'\(.*?\)', '', text)
        text = re.sub(r'\s+', ' ', text)
        text = text.strip()
        return text

    def extract_speaker_segments(self, text, speaker):
        """Extrae segmentos de un hablante específico."""
        pattern = f"{speaker}:\\s+(.*?)(?=\\n\\w+:|$)"
        segments = re.findall(pattern, text, re.DOTALL)
        return [self.preprocess_text(s) for s in segments]

    def get_bert_embeddings(self, text):
        """Obtiene embeddings contextuales usando BERT."""
        inputs = self.bert_tokenizer(text, return_tensors="pt", padding=True, truncation=True, max_length=512)
        outputs = self.bert_model(**inputs)
        return outputs.last_hidden_state.mean(dim=1).detach().numpy()

    def analyze_sentiment_roberta(self, text, chunk_size=500):
        """Análisis de sentimiento avanzado usando RoBERTa."""
        chunks = [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]
        sentiments = []

        for chunk in chunks:
            try:
                result = self.sentiment_analyzer(chunk)[0]
                sentiments.append({
                    'label': result['label'],
                    'score': result['score']
                })
            except Exception as e:
                print(f"Error en chunk: {e}")
                continue

        # Calcular sentimiento promedio
        if sentiments:
            avg_sentiment = np.mean([s['score'] for s in sentiments])
            dominant_label = max(set([s['label'] for s in sentiments]),
                               key=[s['label'] for s in sentiments].count)
            return {'sentiment_score': avg_sentiment, 'dominant_label': dominant_label}
        return {'sentiment_score': 0, 'dominant_label': 'NEUTRAL'}

    def analyze_debate(self, debate_text, speakers):
        """Análisis completo del debate."""
        results = {}

        for speaker in speakers:
            segments = self.extract_speaker_segments(debate_text, speaker)
            if not segments:
                continue

            # Análisis por segmento
            segment_analysis = []
            for segment in tqdm(segments, desc=f"Analizando {speaker}"):
                if len(segment.split()) < 5:  # Skip very short segments
                    continue

                embeddings = self.get_bert_embeddings(segment)
                sentiment = self.analyze_sentiment_roberta(segment)

                segment_analysis.append({
                    'text': segment[:100] + '...',
                    'embeddings': embeddings,
                    'sentiment': sentiment
                })

            results[speaker] = {
                'segments': segment_analysis,
                'total_segments': len(segment_analysis),
                'avg_sentiment': np.mean([s['sentiment']['sentiment_score'] for s in segment_analysis])
            }

        return results

    def compare_speakers(self, results):
        """Compara los patrones de habla entre los oradores."""
        comparisons = {}
        speakers = list(results.keys())

        for i in range(len(speakers)):
            for j in range(i+1, len(speakers)):
                speaker1, speaker2 = speakers[i], speakers[j]

                # Comparar embeddings promedio
                emb1 = np.mean([s['embeddings'] for s in results[speaker1]['segments']], axis=0)
                emb2 = np.mean([s['embeddings'] for s in results[speaker2]['segments']], axis=0)
                similarity = cosine_similarity(emb1.reshape(1, -1), emb2.reshape(1, -1))[0][0]

                comparisons[f"{speaker1}_vs_{speaker2}"] = {
                    'semantic_similarity': similarity,
                    'sentiment_diff': abs(results[speaker1]['avg_sentiment'] -
                                       results[speaker2]['avg_sentiment'])
                }

        return comparisons

    def plot_sentiment_evolution(self, results, speaker):
        """Visualiza la evolución del sentimiento durante el debate."""
        sentiments = [s['sentiment']['sentiment_score'] for s in results[speaker]['segments']]
        plt.figure(figsize=(12, 6))
        plt.plot(sentiments)
        plt.title(f'Sentiment Evolution - {speaker}')
        plt.xlabel('Debate Segment')
        plt.ylabel('Sentiment Score')
        plt.grid(True)
        plt.show()

# Uso del analizador
if __name__ == "__main__":
    # Cargar los debates
    with open('debate.txt', 'r', encoding='utf-8') as f:
        debate1_text = f.read()

    with open('debate2.txt', 'r', encoding='utf-8') as f:
        debate2_text = f.read()

    analyzer = DebateAnalyzer()

    # Analizar primer debate
    print("Analizando Primer Debate...")
    debate1_results = analyzer.analyze_debate(debate1_text, ['TRUMP', 'BIDEN'])

    # Analizar segundo debate
    print("\nAnalizando Segundo Debate...")
    debate2_results = analyzer.analyze_debate(debate2_text, ['TRUMP', 'HARRIS'])

    # Comparar oradores
    print("\nComparando oradores...")
    debate1_comparisons = analyzer.compare_speakers(debate1_results)
    debate2_comparisons = analyzer.compare_speakers(debate2_results)

    # Imprimir resultados
    print("\nResultados del Primer Debate:")
    for speaker, data in debate1_results.items():
        print(f"\n{speaker}:")
        print(f"Segmentos totales: {data['total_segments']}")
        print(f"Sentimiento promedio: {data['avg_sentiment']:.3f}")

    print("\nResultados del Segundo Debate:")
    for speaker, data in debate2_results.items():
        print(f"\n{speaker}:")
        print(f"Segmentos totales: {data['total_segments']}")
        print(f"Sentimiento promedio: {data['avg_sentiment']:.3f}")

    # Visualizar evolución del sentimiento
    for speaker in debate1_results:
        analyzer.plot_sentiment_evolution(debate1_results, speaker)

    for speaker in debate2_results:
        analyzer.plot_sentiment_evolution(debate2_results, speaker)

import re
import numpy as np
from collections import defaultdict
import nltk
from nltk.tokenize import word_tokenize
nltk.download('punkt_tab')

# Descargar recursos necesarios de NLTK
nltk.download('punkt')
nltk.download('stopwords')
from nltk.corpus import stopwords

class LexicalDiversityAnalyzer:
    def __init__(self, min_factor_length=10):
        self.min_factor_length = min_factor_length
        self.stop_words = set(stopwords.words('english'))

    def calculate_mtld(self, text, ttr_threshold=0.72):
        """Calculate MTLD score"""
        tokens = [t.lower() for t in word_tokenize(text) if t.lower() not in self.stop_words]
        if len(tokens) < self.min_factor_length:
            return 0

        def factor_count(tokens_list, forward=True):
            factors = 0
            token_count = 0
            types = set()

            if not forward:
                tokens_list = tokens_list[::-1]

            for token in tokens_list:
                token_count += 1
                types.add(token)
                ttr = len(types) / token_count

                if ttr <= ttr_threshold:
                    factors += 1
                    token_count = 0
                    types = set()

            if token_count > 0:
                ttr = len(types) / token_count
                factors += (1 - ttr) / (1 - ttr_threshold)

            return factors

        forward_factors = factor_count(tokens)
        backward_factors = factor_count(tokens, forward=False)

        if forward_factors == 0 or backward_factors == 0:
            return 0

        mtld = len(tokens) / ((forward_factors + backward_factors) / 2)
        return mtld

def extract_speeches(text, candidates):
    """Extract speeches for each candidate from debate text"""
    speeches = defaultdict(str)
    lines = text.split('\n')
    current_speaker = None

    for line in lines:
        # Buscar indicadores de orador (nombres en mayúsculas seguidos de dos puntos)
        speaker_match = re.match(r'^([A-Z][A-Z\s]+):', line)

        if speaker_match:
            speaker = speaker_match.group(1).strip()
            if speaker in candidates:
                current_speaker = speaker
            else:
                current_speaker = None
            continue

        if current_speaker:
            speeches[current_speaker] += line.strip() + " "

    # Limpiar espacios extra
    for candidate in speeches:
        speeches[candidate] = re.sub(r'\s+', ' ', speeches[candidate]).strip()

    return dict(speeches)

def analyze_debates(debate1_text, debate2_text):
    """Analyze both debates"""
    # Extraer discursos del primer debate
    debate1_speeches = extract_speeches(debate1_text, ['TRUMP', 'BIDEN'])

    # Extraer discursos del segundo debate
    debate2_speeches = extract_speeches(debate2_text, ['TRUMP', 'HARRIS'])

    return {
        'debate1': debate1_speeches,
        'debate2': debate2_speeches
    }

def analyze_all_speeches(debates):
    """Analyze lexical diversity for all speeches"""
    analyzer = LexicalDiversityAnalyzer()
    results = {}

    for debate_name, speeches in debates.items():
        results[debate_name] = {}
        for candidate, speech in speeches.items():
            results[debate_name][candidate] = {
                'mtld': analyzer.calculate_mtld(speech),
                'word_count': len(speech.split())
            }

    return results

# Ahora podemos usar el código para analizar los debates
def run_analysis(debate1_text, debate2_text):
    # Analizar los debates
    debates = analyze_debates(debate1_text, debate2_text)

    # Calcular métricas de diversidad léxica
    results = analyze_all_speeches(debates)

    # Imprimir resultados
    for debate_name, debate_results in results.items():
        print(f"\nResultados para {debate_name}:")
        for candidate, scores in debate_results.items():
            print(f"\n{candidate}:")
            print(f"Palabras totales: {scores['word_count']}")
            print(f"MTLD Score: {scores['mtld']:.2f}")


    return results

# Asumiendo que tienes los textos de los debates en variables
results = run_analysis(debate1_text, debate2_text)

