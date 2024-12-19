# -*- coding: utf-8 -*-
"""Debates US V1.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1EbxIRKXe8OgMhuBZOF3P_hY7fgSXgqK4
"""

!pip install gensim textstat
import re
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.util import ngrams
from collections import Counter
from wordcloud import WordCloud
from nltk.probability import FreqDist
import matplotlib.pyplot as plt
import networkx as nx
from textblob import TextBlob
import plotly.graph_objs as go
from plotly.subplots import make_subplots
import gensim
from gensim import corpora
import textstat
import math

# Descarga recursos necesarios de NLTK (solo si no están ya descargados)
nltk.download('punkt', quiet=True)
nltk.download('stopwords', quiet=True)
nltk.download('punkt_tab')

def extract_speaker_text(text, speakers_to_include):
    pattern = r'([A-Z]+):\s*(.+?)(?=\n[A-Z]+:|\Z)'
    matches = re.findall(pattern, text, re.DOTALL)
    extracted_text = {speaker: [] for speaker in speakers_to_include}
    for speaker, content in matches:
        if speaker in speakers_to_include:
            extracted_text[speaker].append(content.strip())
    return {speaker: ' '.join(texts) for speaker, texts in extracted_text.items()}

def preprocess_text(text):
    stop_words = set(stopwords.words('english'))
    words = word_tokenize(text.lower())
    return [word for word in words if word.isalnum() and word not in stop_words]

def generate_wordcloud_and_stats(text, title, top_n=20):
    filtered_words = preprocess_text(text)
    word_counts = Counter(filtered_words)
    bigrams = list(ngrams(filtered_words, 2))
    trigrams = list(ngrams(filtered_words, 3))
    bigram_counts = Counter(bigrams)
    trigram_counts = Counter(trigrams)

    def generate_cloud(counts, title_suffix):
        wordcloud = WordCloud(width=800, height=400, background_color='white').generate_from_frequencies(counts)
        plt.figure(figsize=(10, 5))
        plt.imshow(wordcloud, interpolation='bilinear')
        plt.axis('off')
        plt.title(f'{title} {title_suffix}')
        plt.show()

    def generate_bar_plot(counts, title_suffix, top_n=20):
        if isinstance(counts, Counter):
            top_items = dict(counts.most_common(top_n))
        else:
            # Si counts es un diccionario, ordenamos manualmente
            top_items = dict(sorted(counts.items(), key=lambda x: x[1], reverse=True)[:top_n])

        plt.figure(figsize=(12, 6))
        plt.barh(list(top_items.keys()), list(top_items.values()))
        plt.title(f'Top {top_n} {title_suffix}')
        plt.xlabel('Frecuencia')
        plt.gca().invert_yaxis()
        plt.tight_layout()
        plt.show()

    generate_cloud(word_counts, 'Word Cloud')
    generate_cloud({' '.join(k): v for k, v in bigram_counts.items()}, 'Bigram Cloud')
    generate_cloud({' '.join(k): v for k, v in trigram_counts.items()}, 'Trigram Cloud')

    generate_bar_plot(word_counts, 'palabras más frecuentes')
    generate_bar_plot({' '.join(k): v for k, v in bigram_counts.items()}, 'bigramas más frecuentes')
    generate_bar_plot({' '.join(k): v for k, v in trigram_counts.items()}, 'trigramas más frecuentes')

    print(f"\nEstadísticas para {title}:")
    print(f"Total de palabras (sin stopwords): {len(filtered_words)}")
    print(f"\nTop {top_n} palabras más frecuentes:")
    for word, count in word_counts.most_common(top_n):
        print(f"{word}: {count}")

    print(f"\nTop {top_n} bigramas más frecuentes:")
    for bigram, count in bigram_counts.most_common(top_n):
        print(f"{' '.join(bigram)}: {count}")

    print(f"\nTop {top_n} trigramas más frecuentes:")
    for trigram, count in trigram_counts.most_common(top_n):
        print(f"{' '.join(trigram)}: {count}")

def generate_word_network(text, title, n=30):
    words = preprocess_text(text)
    word_freq = Counter(words)
    top_words = [word for word, _ in word_freq.most_common(n)]

    G = nx.Graph()
    for i in range(len(words)-1):
        if words[i] in top_words and words[i+1] in top_words:
            if G.has_edge(words[i], words[i+1]):
                G[words[i]][words[i+1]]['weight'] += 1
            else:
                G.add_edge(words[i], words[i+1], weight=1)

    plt.figure(figsize=(16,12))
    pos = nx.spring_layout(G, k=0.5, iterations=50)
    nx.draw(G, pos, node_color='lightblue', node_size=3000, with_labels=True, font_size=8,
            width=[G[u][v]['weight'] for u,v in G.edges()])
    plt.title(f'{title} Word Network')
    plt.show()

def sentiment_over_time(text, title, window_size=100):
    sentences = sent_tokenize(text)
    sentiments = [TextBlob(sentence).sentiment.polarity for sentence in sentences]

    plt.figure(figsize=(12,6))
    plt.plot(sentiments)
    plt.title(f'{title} Sentiment Over Time')
    plt.xlabel('Sentences')
    plt.ylabel('Sentiment (-1 negative, +1 positive)')
    plt.axhline(y=0, color='r', linestyle='--')
    plt.show()

    avg_sentiment = sum(sentiments) / len(sentiments)
    print(f"Promedio de sentimiento: {avg_sentiment:.2f}")
    print(f"Sentencia más positiva: {sentences[sentiments.index(max(sentiments))]}")
    print(f"Sentencia más negativa: {sentences[sentiments.index(min(sentiments))]}")

def comparative_wordcloud(text1, text2, title1, title2):
    words1 = preprocess_text(text1)
    words2 = preprocess_text(text2)
    freq1 = Counter(words1)
    freq2 = Counter(words2)

    diff = {word: freq1[word] - freq2[word] for word in set(words1 + words2)}

    wc = WordCloud(width=800, height=400, background_color='white')
    wc.generate_from_frequencies(diff)

    plt.figure(figsize=(12,6))
    plt.imshow(wc, interpolation='bilinear')
    plt.axis('off')
    plt.title(f'Comparative Wordcloud: {title1} vs {title2}')
    plt.show()

def analyze_debate(file_path, speakers_to_include):
    with open(file_path, 'r', encoding='utf-8') as file:
        debate_text = file.read()

    extracted_texts = extract_speaker_text(debate_text, speakers_to_include)

    all_words = []
    speaker_words = {}

    for speaker, text in extracted_texts.items():
        print(f"\nAnálisis para {speaker}:")
        words = word_tokenize(text.lower())
        all_words.extend(words)
        speaker_words[speaker] = words

        print(f"Total de palabras: {len(words)}")

        # Calcular y mostrar TTR
        ttr = calculate_ttr(text)
        print(f"Type-Token Ratio (TTR): {ttr:.4f}")

        generate_wordcloud_and_stats(text, speaker)
        generate_word_network(text, speaker)
        sentiment_over_time(text, speaker)

        # Nuevos análisis
        analyze_topics(text)
        analyze_readability(text)

    # Calcular Log-Likelihood entre los dos primeros speakers
    speaker1, speaker2 = speakers_to_include[:2]
    words1 = speaker_words[speaker1]
    words2 = speaker_words[speaker2]

    freq1 = Counter(words1)
    freq2 = Counter(words2)

    total1 = len(words1)
    total2 = len(words2)

    all_unique_words = set(freq1.keys()) | set(freq2.keys())

    print(f"\nTop 20 palabras con mayor Log-Likelihood entre {speaker1} y {speaker2}:")
    ll_scores = []
    for word in all_unique_words:
        count1 = freq1[word]
        count2 = freq2[word]
        ll = calculate_log_likelihood(count1, count2, total1, total2)
        ll_scores.append((word, ll))

    for word, ll in sorted(ll_scores, key=lambda x: x[1], reverse=True)[:20]:
        print(f"{word}: {ll:.2f}")

    comparative_wordcloud(extracted_texts[speaker1], extracted_texts[speaker2], speaker1, speaker2)


def analyze_topics(text, num_topics=5, num_words=10):
    """
    Realiza un análisis de temas utilizando LDA.
    """
    words = preprocess_text(text)
    # Crear diccionario
    dictionary = corpora.Dictionary([words])

    # Crear corpus
    corpus = [dictionary.doc2bow(words)]

    # Entrenar modelo LDA
    lda_model = gensim.models.LdaMulticore(corpus=corpus, id2word=dictionary, num_topics=num_topics)

    print(f"\nTemas principales (LDA):")
    for idx, topic in lda_model.print_topics(-1, num_words=num_words):
        print(f"Tema {idx + 1}: {topic}")

def analyze_readability(text):
    """
    Analiza la complejidad del discurso utilizando diferentes métricas de legibilidad.
    """
    print("\nAnálisis de complejidad del discurso:")
    print(f"Índice Flesch-Kincaid Grade: {textstat.flesch_kincaid_grade(text)}")
    print(f"Índice de legibilidad Flesch: {textstat.flesch_reading_ease(text)}")
    print(f"Índice SMOG: {textstat.smog_index(text)}")
    print(f"Índice Coleman-Liau: {textstat.coleman_liau_index(text)}")
    print(f"Índice de legibilidad automatizado: {textstat.automated_readability_index(text)}")


def compare_debates(debate1_path, debate2_path, speakers1, speakers2):
    with open(debate1_path, 'r', encoding='utf-8') as file:
        debate1_text = file.read()
    with open(debate2_path, 'r', encoding='utf-8') as file:
        debate2_text = file.read()

    trump1_text = extract_speaker_text(debate1_text, ['TRUMP'])['TRUMP']
    trump2_text = extract_speaker_text(debate2_text, ['TRUMP'])['TRUMP']

    print("\nComparación de Trump entre debates:")
    comparative_wordcloud(trump1_text, trump2_text, 'Trump (Debate 1)', 'Trump (Debate 2)')

    sentiment1 = TextBlob(trump1_text).sentiment.polarity
    sentiment2 = TextBlob(trump2_text).sentiment.polarity

    print(f"Sentimiento de Trump en Debate 1: {sentiment1:.2f}")
    print(f"Sentimiento de Trump en Debate 2: {sentiment2:.2f}")

def calculate_jaccard_similarity(text1, text2, n=1):
    # Preprocess texts
    stop_words = set(stopwords.words('english'))
    words1 = [word.lower() for word in word_tokenize(text1) if word.isalnum() and word.lower() not in stop_words]
    words2 = [word.lower() for word in word_tokenize(text2) if word.isalnum() and word.lower() not in stop_words]

    # Generate n-grams
    ngrams1 = set(ngrams(words1, n))
    ngrams2 = set(ngrams(words2, n))

    # Calculate Jaccard similarity
    intersection = len(ngrams1.intersection(ngrams2))
    union = len(ngrams1.union(ngrams2))

    return intersection / union if union != 0 else 0

def compare_debates_jaccard(debate1_path, debate2_path, speakers1, speakers2):
    with open(debate1_path, 'r', encoding='utf-8') as file:
        debate1_text = file.read()
    with open(debate2_path, 'r', encoding='utf-8') as file:
        debate2_text = file.read()

    trump1_text = extract_speaker_text(debate1_text, ['TRUMP'])['TRUMP']
    trump2_text = extract_speaker_text(debate2_text, ['TRUMP'])['TRUMP']

    print("\nJaccard Similarity Analysis for Trump's speeches:")
    for n in [1, 2, 3]:
        similarity = calculate_jaccard_similarity(trump1_text, trump2_text, n)
        print(f"{n}-gram Jaccard Similarity: {similarity:.4f}")

def calculate_ttr(text):
    words = word_tokenize(text.lower())
    return len(set(words)) / len(words)

def calculate_log_likelihood(count1, count2, total1, total2):
    expected1 = total1 * (count1 + count2) / (total1 + total2)
    expected2 = total2 * (count1 + count2) / (total1 + total2)
    ll = 2 * (count1 * math.log(count1 / expected1 if count1 != 0 else 1) +
               count2 * math.log(count2 / expected2 if count2 != 0 else 1))
    return ll

if __name__ == "__main__":
    print("Analizando el primer debate (Trump vs Biden):")
    analyze_debate('debate.txt', ['TRUMP', 'BIDEN'])

    print("\nAnalizando el segundo debate (Trump vs Harris):")
    analyze_debate('debate2.txt', ['TRUMP', 'HARRIS'])

    compare_debates('debate.txt', 'debate2.txt', ['TRUMP', 'BIDEN'], ['TRUMP', 'HARRIS'])
    compare_debates_jaccard('debate.txt', 'debate2.txt', ['TRUMP', 'BIDEN'], ['TRUMP', 'HARRIS'])

# Import required libraries
!pip install transformers torch pandas numpy seaborn sklearn nltk textblob vaderSentiment bertopic
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification, pipeline
from bertopic import BERTopic
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.metrics.pairwise import cosine_similarity
from nltk.tokenize import sent_tokenize
import re
import os

class AdvancedDebateAnalyzer:
    def __init__(self):
        # Initialize BERT model for sentiment analysis
        self.sentiment_model = pipeline(
            "sentiment-analysis",
            model="nlptown/bert-base-multilingual-uncased-sentiment"
        )

        # Initialize BERT model for embeddings
        self.tokenizer = AutoTokenizer.from_pretrained('bert-base-uncased')
        self.model = AutoModelForSequenceClassification.from_pretrained('bert-base-uncased')

        # Initialize VADER for comparison
        self.vader = SentimentIntensityAnalyzer()

        # Initialize BERTopic for topic modeling
        self.topic_model = BERTopic(language="english")

    def extract_speaker_text(self, text, speaker):
        """Extract text for specific speaker using improved regex"""
        pattern = rf'{speaker}:\s*(.*?)(?=\n[A-Z]+:|$)'
        matches = re.findall(pattern, text, re.DOTALL | re.MULTILINE)
        return ' '.join([m.strip() for m in matches])

    def get_bert_embeddings(self, text):
        """Generate BERT embeddings for text with chunking for long texts"""
        # Tokenize the text
        tokens = self.tokenizer(
            text,
            padding=True,
            truncation=True,
            max_length=512,  # BERT's maximum sequence length
            return_tensors="pt"
        )

        # Process in chunks if text is too long
        chunk_size = 512
        all_embeddings = []

        for i in range(0, len(tokens['input_ids'][0]), chunk_size):
            chunk_tokens = {
                'input_ids': tokens['input_ids'][:, i:i+chunk_size],
                'attention_mask': tokens['attention_mask'][:, i:i+chunk_size]
            }

            with torch.no_grad():
                outputs = self.model(**chunk_tokens)
                chunk_embeddings = outputs.logits.mean(dim=1).numpy()
                all_embeddings.append(chunk_embeddings)

        # Combine embeddings from all chunks
        if len(all_embeddings) > 1:
            return np.mean(all_embeddings, axis=0)
        else:
            return all_embeddings[0]

    def analyze_sentiment_advanced(self, text):
        """Multi-level sentiment analysis using BERT and VADER with chunking"""
        sentences = sent_tokenize(text)

        # Process sentences in chunks
        chunk_size = 10  # Process 10 sentences at a time
        bert_sentiments = []

        for i in range(0, len(sentences), chunk_size):
            chunk = sentences[i:i+chunk_size]
            chunk_text = ' '.join(chunk)
            chunk_sentiments = self.sentiment_model(chunk_text, truncation=True, max_length=512)
            bert_sentiments.extend(chunk_sentiments)

        bert_score = np.mean([float(s['score']) for s in bert_sentiments])

        # VADER analysis (doesn't need chunking)
        vader_scores = [self.vader.polarity_scores(sentence) for sentence in sentences]
        vader_compound = np.mean([score['compound'] for score in vader_scores])

        # Detailed analysis per sentence
        sentence_analysis = []
        for i, (sentence, vader_score) in enumerate(zip(sentences, vader_scores)):
            bert_sent = bert_sentiments[i] if i < len(bert_sentiments) else bert_sentiments[-1]
            sentence_analysis.append({
                'sentence': sentence,
                'bert_score': float(bert_sent['score']),
                'vader_compound': vader_score['compound'],
                'context': self._analyze_context(sentence)
            })

        return {
            'bert_overall': bert_score,
            'vader_overall': vader_compound,
            'sentence_analysis': sentence_analysis
        }

    def _analyze_context(self, sentence):
        """Analyze contextual elements like sarcasm and rhetoric"""
        context_indicators = {
            'sarcasm': ['really', 'obviously', 'clearly', 'oh sure', 'right'],
            'rhetoric': ['isn\'t it', 'don\'t you think', 'how about', 'what if'],
            'emphasis': ['very', 'extremely', 'absolutely', 'totally']
        }

        found_contexts = []
        lower_sentence = sentence.lower()

        for context_type, indicators in context_indicators.items():
            if any(indicator in lower_sentence for indicator in indicators):
                found_contexts.append(context_type)

        return found_contexts

    def analyze_topics(self, text):
        """Perform topic modeling using BERTopic with chunking"""
        try:
            # Split text into smaller chunks to handle long texts
            sentences = sent_tokenize(text)

            # Asegurarse de que tenemos suficientes documentos para el análisis
            if len(sentences) < 10:
                print("Warning: Not enough text for meaningful topic analysis")
                return {
                    'topic_model': None,
                    'topics': [],
                    'topic_info': pd.DataFrame(),
                    'topic_representations': {}
                }

            # Usar chunks más pequeños y manejar documentos vacíos
            chunk_size = min(50, len(sentences))  # Ajustar el tamaño del chunk
            chunks = [' '.join(sentences[i:i+chunk_size]) for i in range(0, len(sentences), chunk_size)]
            chunks = [chunk for chunk in chunks if len(chunk.strip()) > 0]

            # Configurar BERTopic con parámetros más conservadores
            self.topic_model = BERTopic(
                nr_topics=min(10, len(chunks)),  # Limitar número de tópicos
                language="english",
                verbose=True
            )

            # Fit y transform
            topics, _ = self.topic_model.fit_transform(chunks)

            return {
                'topic_model': self.topic_model,
                'topics': topics,
                'topic_info': self.topic_model.get_topic_info(),
                'topic_representations': self.topic_model.get_topics()
            }
        except Exception as e:
            print(f"Error in topic analysis: {str(e)}")
            return {
                'topic_model': None,
                'topics': [],
                'topic_info': pd.DataFrame(),
                'topic_representations': {}
            }

    def calculate_semantic_similarity(self, text1, text2):
        """Calculate semantic similarity using BERT embeddings"""
        emb1 = self.get_bert_embeddings(text1)
        emb2 = self.get_bert_embeddings(text2)

        return cosine_similarity(emb1.reshape(1, -1), emb2.reshape(1, -1))[0][0]

    def analyze_debate(self, debate_text, speakers):
        """Perform comprehensive debate analysis"""
        results = {}

        for speaker in speakers:
            print(f"\nAnalyzing {speaker}'s speech...")
            speaker_text = self.extract_speaker_text(debate_text, speaker)

            # Sentiment Analysis
            print(f"Performing sentiment analysis for {speaker}...")
            sentiment_results = self.analyze_sentiment_advanced(speaker_text)

            # Topic Analysis
            print(f"Performing topic analysis for {speaker}...")
            topic_results = self.analyze_topics(speaker_text)

            # Store results
            results[speaker] = {
                'sentiment': sentiment_results,
                'topics': topic_results
            }

        return results

    def compare_debates(self, debate1_text, debate2_text, speaker):
        """Compare two debates for the same speaker"""
        print(f"\nComparing {speaker}'s speeches across debates...")

        text1 = self.extract_speaker_text(debate1_text, speaker)
        text2 = self.extract_speaker_text(debate2_text, speaker)

        similarity = self.calculate_semantic_similarity(text1, text2)

        sentiment1 = self.analyze_sentiment_advanced(text1)
        sentiment2 = self.analyze_sentiment_advanced(text2)

        topics1 = self.analyze_topics(text1)
        topics2 = self.analyze_topics(text2)

        return {
            'semantic_similarity': similarity,
            'sentiment_comparison': {
                'debate1': sentiment1,
                'debate2': sentiment2
            },
            'topic_comparison': {
                'debate1': topics1,
                'debate2': topics2
            }
        }

    def visualize_results(self, results, output_dir='./visualizations'):
        """Generate visualizations for analysis results"""
        # Ensure output directory exists
        os.makedirs(output_dir, exist_ok=True)

        # Sentiment visualization
        plt.figure(figsize=(15, 8))
        for speaker, data in results.items():
            sentiment_data = pd.DataFrame(data['sentiment']['sentence_analysis'])
            plt.plot(sentiment_data['bert_score'], label=f'{speaker} BERT', alpha=0.7)
            plt.plot(sentiment_data['vader_compound'], label=f'{speaker} VADER', alpha=0.7, linestyle='--')

        plt.title('Sentiment Analysis Over Time', fontsize=14)
        plt.xlabel('Sentence Number', fontsize=12)
        plt.ylabel('Sentiment Score', fontsize=12)
        plt.legend(fontsize=10)
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.savefig(f'{output_dir}/sentiment_analysis.png', dpi=300, bbox_inches='tight')
        plt.close()

        # Topic visualization using BERTopic
        for speaker, data in results.items():
            try:
                topic_model = data['topics']['topic_model']
                # Asegurarse de que haya tópicos antes de visualizar
                if len(topic_model.get_topic_info()) > 0:
                    # Crear visualización estática en lugar de interactiva
                    fig, ax = plt.subplots(figsize=(15, 8))
                    topic_info = topic_model.get_topic_info()
                    top_topics = topic_info.head(10)  # Mostrar solo los 10 principales tópicos

                    # Crear gráfico de barras para los tópicos
                    ax.barh(range(len(top_topics)), top_topics['Count'])
                    ax.set_yticks(range(len(top_topics)))
                    ax.set_yticklabels([f"Topic {i}" for i in range(len(top_topics))])

                    plt.title(f'Top 10 Topics for {speaker}')
                    plt.xlabel('Count')
                    plt.ylabel('Topics')
                    plt.tight_layout()
                    plt.savefig(f'{output_dir}/{speaker}_topics.png', dpi=300, bbox_inches='tight')
                    plt.close()

                else:
                    print(f"No topics found for {speaker}")
            except Exception as e:
                print(f"Error visualizing topics for {speaker}: {str(e)}")
                continue

def main():
    # Initialize the analyzer
    analyzer = AdvancedDebateAnalyzer()

    # Read debate texts
    print("Reading debate texts...")
    with open('debate.txt', 'r', encoding='utf-8') as f:
        debate1_text = f.read()
    with open('debate2.txt', 'r', encoding='utf-8') as f:
        debate2_text = f.read()

    # Analyze first debate
    print("\nAnalyzing first debate...")
    debate1_results = analyzer.analyze_debate(
        debate1_text,
        ['TRUMP', 'BIDEN']
    )

    # Analyze second debate
    print("\nAnalyzing second debate...")
    debate2_results = analyzer.analyze_debate(
        debate2_text,
        ['TRUMP', 'HARRIS']
    )

    # Compare Trump's performance across debates
    print("\nComparing Trump's performance across debates...")
    trump_comparison = analyzer.compare_debates(
        debate1_text,
        debate2_text,
        'TRUMP'
    )

    # Generate visualizations
    print("\nGenerating visualizations...")
    analyzer.visualize_results(debate1_results)
    analyzer.visualize_results(debate2_results)

    # Print summary statistics
    print("\nDebate 1 Analysis:")
    for speaker, results in debate1_results.items():
        print(f"\n{speaker}:")
        print(f"Average BERT sentiment: {results['sentiment']['bert_overall']:.3f}")
        print(f"Average VADER sentiment: {results['sentiment']['vader_overall']:.3f}")
        print("Top topics:", results['topics']['topic_info'].head())

    print("\nDebate 2 Analysis:")
    for speaker, results in debate2_results.items():
        print(f"\n{speaker}:")
        print(f"Average BERT sentiment: {results['sentiment']['bert_overall']:.3f}")
        print(f"Average VADER sentiment: {results['sentiment']['vader_overall']:.3f}")
        print("Top topics:", results['topics']['topic_info'].head())

    print("\nTrump Debate Comparison:")
    print(f"Semantic similarity between debates: {trump_comparison['semantic_similarity']:.3f}")

if __name__ == "__main__":
    main()