import math


def cosine_similarity(vec1, vec2):
    """
    Calculate the Cosine Similarity between two TF-IDF vectors.

    Formula:
        Cosine Similarity = (A · B) / (||A|| × ||B||)

    where:
        A · B  = Dot Product of two vectors
        ||A||  = Magnitude of vector A
        ||B||  = Magnitude of vector B
    """

    # --------------------------------------------
    # Step 1: Calculate the dot product
    # Multiply the TF-IDF weights of common terms
    # between the two vectors.
    # --------------------------------------------

    dot = 0

    for word in vec1:
        dot += vec1[word] * vec2.get(word, 0)

    # --------------------------------------------
    # Step 2: Calculate the magnitude (length)
    # of each TF-IDF vector.
    # --------------------------------------------

    mag1 = math.sqrt(sum(value * value for value in vec1.values()))
    mag2 = math.sqrt(sum(value * value for value in vec2.values()))

    # --------------------------------------------
    # Step 3: Prevent division by zero.
    # If either vector has zero magnitude,
    # similarity is defined as zero.
    # --------------------------------------------

    if mag1 == 0 or mag2 == 0:
        return 0

    # --------------------------------------------
    # Step 4: Compute the cosine similarity score.
    # The result ranges from 0 to 1:
    # 0 = No similarity
    # 1 = Identical documents
    # --------------------------------------------

    return dot / (mag1 * mag2)


def similarity_matrix(vectors):
    """
    Generate a similarity matrix by comparing
    every TF-IDF vector with every other vector.

    Returns:
        A two-dimensional matrix where each cell
        represents the cosine similarity score
        between two courses.
    """

    matrix = []

    # Compare every course with every other course
    for v1 in vectors:

        row = []

        for v2 in vectors:

            # Calculate similarity between two vectors
            row.append(cosine_similarity(v1, v2))

        # Store similarity scores for one course
        matrix.append(row)

    return matrix