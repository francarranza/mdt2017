# encoding=utf8
import re  # Para expresioones regulares
import nltk
import numpy
from sklearn.cluster import KMeans
from scipy.sparse import dok_matrix
import bisect
import itertools # para iterar un generator

EOL = '\n'
STOPWORDS = nltk.corpus.stopwords.words('spanish')


# Forma muy eficiente de buscar un elemento en una lista ordenada
def find_index(vocab, w):
    i = bisect.bisect_left(vocab, w)
    if i != len(vocab) and vocab[i] == w:
        return i
    return False


# Devuelve una lista con las oraciones de un texto
def get_sentences(text):
    sentences = []
    sentences = nltk.sent_tokenize(text, 'spanish')

    return sentences


def preprocess(corpus):
    # Transformar el texto a lowercase
    text = str(open(corpus).read().lower())

    # dejo solo un espacio
    text = re.sub(' +',' ', text)

    # Me deshago de todos los numeros
    text = re.sub(r"[0-9]+", "", text)

    sentences = get_sentences(text)
    return sentences, text

# Limpia la palabra de signos de puntuacion
def clean_word(word):
    clean_word = ''

    for character in word:
        if character.isalpha():
            clean_word += character

    return clean_word


# Chequea que una palabra no sea stopwords y que no tenga menos de 2 caracteres
def is_nice_word(word):
    status = True

    if find_index(STOPWORDS, word)  or len(word)<2:
        status = False

    return status


def get_clean(sentences):
    # aprovechamos y limpiamos las stopwords
    clean_words = []

    # clean_sents es una lista de oraciones tokenizadas o sea lista de listas
    clean_sents = []

    j = 0
    for sent in sentences:
        j+=1
        if j % 1000 == 0:
            print (j, "mil")
        aux_sent = []
        words = sent.split(' ')
        for token in words:
            token = clean_word(token)

            if is_nice_word(token):
                aux_sent.append(token)
                clean_words.append(token)

        clean_sents.append(aux_sent)

    return (clean_words, clean_sents)


# Crea una lista con palabras unicas
def make_vocab(words):
    vocab = []

    for w in words:
        position = bisect.bisect_left(vocab, w)
        if position == len(vocab) or vocab[position] != w:
            vocab.insert(position, w)

    return vocab


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


def print_clusters(clusters_n, labels, list_index):
    for i in range(clusters_n):
        print("------------", "Cluser: ", i, "-----------")
        for t in itertools.islice(labels, 20):
            if(t[1] == i):
                print (list_index[t[0]])


# pre procesamos el texto, limpiamos lo que no queremos
filename = 'corpus_lavoz.txt'
sentences, clean_text = preprocess(filename)
print ("pre procesado listo")
print (len(sentences))

# Obtenemos las palabras
clean_words, clean_sents = get_clean(sentences[:1000])
print ("listo el get clean")

vocab = make_vocab(clean_words)
print ("listo el vocab", len(vocab))

# Hacemos la matriz
matrix = make_matrix(vocab, clean_words)
print ("lista la matriz")

# Ahora hacemos los clusters con KMeans
n_clusters = 10
n_jobs = -1
clusters = KMeans(n_clusters=n_clusters, n_jobs=n_jobs).fit(matrix)

print_clusters(n_clusters, clusters.labels_, vocab)
