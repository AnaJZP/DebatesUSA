# DebatesUSA

## 📋 **Descripción General**
Este repositorio contiene el análisis de los **debates presidenciales de 2024** entre:
- **Donald Trump vs Joe Biden**
- **Donald Trump vs Kamala Harris**

Se aplican técnicas avanzadas de **Procesamiento de Lenguaje Natural (NLP)** para explorar el discurso de los candidatos, incluyendo análisis de sentimiento, comparación semántica y generación de nubes de palabras.

---

## 🛠️ **Tecnologías y Librerías**
Este análisis se realizó con:
- **Python 3.x**
- **Transformers** (BERT y RoBERTa)
- **PyTorch**
- **NLTK** (Tokenización y preprocesamiento)
- **TextBlob** (Polaridad del sentimiento)
- **Matplotlib y Seaborn** (Visualización)
- **WordCloud** (Nubes de palabras)
- **Scikit-learn** (Similaridad coseno y métricas adicionales)

---

## 📁 **Estructura del Proyecto**


```bash
DebatesUSA/
├── debates_us_v1.py   # Análisis inicial: Nubes de palabras, sentimiento y TTR
├── debates_us_v2_.py  # Análisis avanzado: Embeddings BERT y sentimiento RoBERTa
├── debate.txt         # Transcripción del primer debate (Trump-Biden)
├── debate2.txt        # Transcripción del segundo debate (Trump-Harris)
├── requirements.txt   # Librerías necesarias para ejecutar el proyecto
└── README.md          # Archivo README (este archivo)
```


---

## 🔍 **Características Principales**
1. **Extracción de Segmentos**
   - Separación de los discursos de cada candidato con expresiones regulares.
2. **Análisis de Sentimiento**
   - Evaluación con **RoBERTa** para determinar la polaridad del sentimiento (positivo, negativo, neutral) en segmentos clave.
3. **Embeddings y Comparación Semántica**
   - Uso de **BERT embeddings** y **similaridad coseno** para comparar los patrones discursivos entre candidatos.
4. **Nubes de Palabras y Estadísticas**
   - Generación de **nubes de palabras**, bigramas y trigramas.
5. **Evolución del Sentimiento**
   - Gráficos que muestran cómo evoluciona el sentimiento a lo largo del debate.
6. **Análisis Lexical**
   - Cálculo de métricas de diversidad léxica como **MTLD** y **TTR**.
7. **Comparación de Debates**
   - Comparación de discursos de un mismo candidato (Trump) entre dos debates usando **similaridad de Jaccard**.

---

## 🚀 **Cómo Ejecutar**
### **Requisitos Previos**

1. Clonar el repositorio:
```bash   
   git clone https://github.com/AnaJZP/DebatesUSA.git
```   
2. Crear un entorno virtual y activarlo:
```bash  
python -m venv venv
source venv/bin/activate  # En Linux/Mac
.\venv\Scripts\activate   # En Windows
```

4. Instalar las dependencias necesarias:
```bash
pip install -r requirements.txt
```

6. Ejecución del Análisis
```bash
python debates_us_v1.py
python debates_us_v2_.py
```

## 📊 **Resultados Esperados**
- **Nubes de palabras**: Visualización de las palabras más frecuentes, bigramas y trigramas.
- **Gráficos de Sentimiento**: Evolución del sentimiento a lo largo de los segmentos del debate.
- **Comparación Semántica**: Similitud coseno entre discursos de los candidatos usando embeddings BERT.
- **Análisis Lexical**: Métricas de diversidad léxica como **MTLD** y **TTR**.
- **Análisis de Temas**: Identificación de los temas principales con LDA.
- **Comparación de Debates**: Similitud de **Jaccard** entre discursos de Trump en ambos debates.

## 👤 **Autor**
- **Ana Lorena Jiménez Preciado**  
   Research Professor | Data Scientist AI Factory
   GitHub: [AnaJZP](https://github.com/AnaJZP)  
   LinkedIn: (https://www.linkedin.com/in/anajptrader/)


