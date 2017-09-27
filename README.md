MDT 2017: Minería de datos para texto 2017
=========================================

Francisco Carranza
------------------

Práctico 1: Clusterización
--------------------------

### Notas

Habiendo hecho practicamente el trabajo en la librería SpaCy, decidí quedarme
con nltk. La razón es que con éste método que seguí (lo explicaré a continuación)
no le saco mucho provecho.
Dentro de nltk utilizo solo word y sent tokenizer.

Los experimentos que realicé fueron en base al corpus La Voz con una longitud
de 10000 oraciones. El programa en general es muy eficiente y rápido, salvo cuando armo 
la matriz y calculo KMeans.



### 1. Cargo el corpus
Al cargar el corpus, hago un chequeo y una limpieza rápida.
* Paso el texto a lowercase, para no hacer distinción entre mayúsculas y minúsculas
* Le saco todos los números. Considero que los números no aportan información
de semántica al contexto de las palabras.
* Obtengo las oraciones usando sent_tokenize de nltk

notebook:
```python
    def preprocess(corpus):
        # Transformar el texto a lowercase
        text = unicode(open(corpus).read().decode('utf8')).lower()

        # dejo solo un espacio
        text = re.sub(' +',' ', text)

        # Me deshago de todos los numeros
        text = re.sub(r"[0-9]+", "", text)

        sentences = get_sentences(text)
        return sentences, text
```

### 2. Tokenizo
A la hora de tokenizar me baso en estos criterios:
* Descarto las stopwords, es decir, las palabras mas frecuentes del
idioma español
* Limpio cada una de signos de puntuación.
* Intenté lematizar pero no pude, me transformaba las palabras en otras raras.
* Devuelvo una lista con todas las palabras que cumplen éstos criterios 
ordenadas según su aparición en el corpus.

notebook:
```python
    def get_clean(sentences):
        # aprovechamos y limpiamos las stopwords
        clean_words = []

        # clean_sents es una lista de oraciones tokenizadas o sea lista de listas
        clean_sents = []

        for sent in sentences:
            aux_sent = []
            words = sent.split(' ')
            for token in words:
                # quito de la palabra signos de puntuacion
                token = clean_word(token)

                # Si no es una stopword
                if is_nice_word(token):
                    aux_sent.append(token)
                    clean_words.append(token)

            clean_sents.append(aux_sent)

        return (clean_words, clean_sents)
```


### 3. Armo un Vocabulario
La idea de esto es tener una lista con las palabras que aparecen en el corpus
sin repetición. Es una de las tareas más cara computacionalmente. Para sortear
este problema, utilicé la librería bisect, que permite encontrar un elemento 
en una lista ordenada con O(nlogn). De esta forma se aceleró mucho el tiempo de
ejecución.

notebook:
```python
    # Crea una lista con palabras unicas
    def make_vocab(words):
        vocab = []

        for w in words:
            position = bisect.bisect_left(vocab, w)
            if position == len(vocab) or vocab[position] != w:
                vocab.insert(position, w)

        return vocab
```


### 4. Armo una matriz de contextos
Mi ventana de contexto es de 3 palabras. La palabra que me estoy fijando, 
la anterior y la posterior. Mi matriz es cuadrada, donde mis filas y columnas 
son los elementos de mi vocabulario y la posición i,j la cantidad de veces que
una palabra i aparece junto a otra palabra j.

notebook:
```python
    def make_matrix(vocab, clean_words):
        # Inicializamos una matriz con ceros
        # La iesima fila de la matriz correspondera a la iesima palabra
        # de la lista words
        matrix = dok_matrix((len(vocab), len(vocab)))
        for i in range(len(clean_words)):
            try:
                previous = clean_words[i-1]
                current  = clean_words[i]
                nextw    = clean_words[i+1]

                prev_pos = find_index(vocab, previous)
                current_pos = find_index(vocab, current)
                next_pos = find_index(vocab, nextw)

                matrix[current_pos][prev_pos] += 1
                matrix[current_pos][current_pos] += 1
                matrix[current_pos][next_pos] += 1

            except IndexError:
                pass

        return matrix
```


### 5. Computamos los clusters
Utilicé el algoritmo de Kmeans. Ya teniendo la matriz del paso anterior, queda
pasarsela al KMeans. Elegí 10 clusters. El resultado es extraño, tengo algunos 
clusters bastante definidos en cuanto a semántica, otros con muy pocas palabras
y casi siempre uno con la gran mayoría. 

En este ejemplo podemos ver que el cluster 3 si tiene
buena semántica, pero por alguna razón el resto tiene una sola palabra, salvo
el cluster 0 que tiene al resto.
notebook:
```
---------- Cluster 0 -------------------
# Casi todas las palabras del cluster
---------- Cluster 1 -------------------
años
---------- Cluster 2 -------------------
pasado
---------- Cluster 3 -------------------
argentina
capital
carne
gobernador
gobierno
mejor
nacional
provincial
puede
sólo
---------- Cluster 4 -------------------
si
---------- Cluster 5 -------------------
trabajadores
...
```


