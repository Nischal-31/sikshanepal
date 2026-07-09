import math
import re
from collections import Counter


def tokenize(text):
    """
    Convert text into lowercase tokens by removing
    punctuation and extracting alphanumeric words.
    """

    return re.findall(r"\b[a-zA-Z0-9]+\b", text.lower())


def compute_tf(tokens):
    """
    Compute the Term Frequency (TF) of each word
    in a document.

    Formula:
        TF = Number of occurrences of a term /
             Total number of terms in the document
    """

    counts = Counter(tokens)
    total = len(tokens)

    tf = {}

    # Calculate normalized frequency of each word
    for word, count in counts.items():
        tf[word] = count / total

    return tf


def compute_idf(tokenized_docs):
    """
    Compute the Inverse Document Frequency (IDF)
    for every word in the collection of documents.

    Formula:
        IDF = log(N / (1 + DF))

    where:
        N  = Total number of documents
        DF = Number of documents containing the word

    Words that appear in many documents receive
    lower weights, while rare words receive higher
    importance.
    """

    N = len(tokenized_docs)

    # Build the complete vocabulary
    vocabulary = set()

    for doc in tokenized_docs:
        vocabulary.update(doc)

    idf = {}

    # Calculate IDF value for every word
    for word in vocabulary:

        # Document Frequency (DF)
        df = sum(word in doc for doc in tokenized_docs)

        idf[word] = math.log(N / (1 + df))

    return idf


def compute_tfidf(texts):
    """
    Generate TF-IDF vectors for a collection of documents.

    Processing Steps:
    1. Tokenize each document.
    2. Calculate TF for each document.
    3. Calculate IDF across all documents.
    4. Multiply TF and IDF to generate TF-IDF vectors.

    Returns:
        A list of TF-IDF vectors representing each document.
    """

    # --------------------------------------------
    # Step 1: Convert each document into tokens
    # --------------------------------------------

    tokenized_docs = [tokenize(text) for text in texts]

    # --------------------------------------------
    # Step 2: Compute Term Frequency for each document
    # --------------------------------------------

    tf_list = [compute_tf(doc) for doc in tokenized_docs]

    # --------------------------------------------
    # Step 3: Compute Inverse Document Frequency
    # for the complete document collection
    # --------------------------------------------

    idf = compute_idf(tokenized_docs)

    # --------------------------------------------
    # Step 4: Generate TF-IDF vectors
    # TF-IDF = TF × IDF
    # --------------------------------------------

    vectors = []

    for tf in tf_list:

        vector = {}

        for word in idf:
            vector[word] = tf.get(word, 0) * idf[word]

        vectors.append(vector)

    return vectors