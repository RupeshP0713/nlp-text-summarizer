import nltk
import networkx as nx
import numpy as np
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer


def _ensure_nltk_data() -> None:
    for resource in ("punkt", "punkt_tab", "stopwords", "wordnet"):
        try:
            nltk.download(resource, quiet=True)
        except Exception:
            # If data download fails, NLTK will raise a clear error at runtime.
            pass


_ensure_nltk_data()
STOP_WORDS = set(stopwords.words("english"))
LEMMATIZER = WordNetLemmatizer()


def preprocess_text(text: str) -> tuple[list[str], dict[str, float]]:
    sentences = nltk.sent_tokenize(text)
    word_freq: dict[str, float] = {}

    for sentence in sentences:
        words = nltk.word_tokenize(sentence.lower())
        for word in words:
            if word.isalpha() and word not in STOP_WORDS:
                lemma = LEMMATIZER.lemmatize(word)
                word_freq[lemma] = word_freq.get(lemma, 0.0) + 1.0

    if not word_freq:
        return sentences, word_freq

    max_freq = max(word_freq.values())
    for word in word_freq:
        word_freq[word] = word_freq[word] / max_freq

    return sentences, word_freq


def sentence_similarity(s1: str, s2: str, word_freq: dict[str, float]) -> float:
    words1 = [
        LEMMATIZER.lemmatize(w.lower())
        for w in nltk.word_tokenize(s1)
        if w.isalpha() and w.lower() not in STOP_WORDS
    ]
    words2 = [
        LEMMATIZER.lemmatize(w.lower())
        for w in nltk.word_tokenize(s2)
        if w.isalpha() and w.lower() not in STOP_WORDS
    ]
    common = set(words1).intersection(words2)
    if not common:
        return 0.0
    return sum(word_freq.get(word, 0.0) for word in common)


def build_similarity_matrix(sentences: list[str], word_freq: dict[str, float]) -> np.ndarray:
    n = len(sentences)
    matrix = np.zeros((n, n))
    for i in range(n):
        for j in range(i + 1, n):
            score = sentence_similarity(sentences[i], sentences[j], word_freq)
            matrix[i][j] = score
            matrix[j][i] = score
    return matrix


def get_top_keywords(text: str, top_n: int = 10) -> list[str]:
    _, word_freq = preprocess_text(text)
    if not word_freq:
        return []
    sorted_words = sorted(word_freq.items(), key=lambda item: item[1], reverse=True)[:top_n]
    return [word for word, _ in sorted_words]


def generate_summary(
    text: str,
    num_sentences: int,
    bullet_mode: bool = False,
    boost_keywords: list[str] | None = None,
) -> str:
    sentences, word_freq = preprocess_text(text)
    if not sentences:
        return ""

    if boost_keywords:
        boost_set = {w.lower() for w in boost_keywords}
        for sentence in sentences:
            words_in_sentence = {
                LEMMATIZER.lemmatize(w.lower())
                for w in nltk.word_tokenize(sentence)
                if w.isalpha()
            }
            overlap = words_in_sentence.intersection(boost_set)
            for word in overlap:
                if word in word_freq:
                    word_freq[word] = word_freq[word] * 1.5

    matrix = build_similarity_matrix(sentences, word_freq)
    graph = nx.from_numpy_array(matrix)
    scores = nx.pagerank(graph)

    ranked = sorted(((scores[i], s, i) for i, s in enumerate(sentences)), reverse=True)
    take = max(1, min(num_sentences, len(ranked)))
    top = sorted(ranked[:take], key=lambda item: item[2])
    summary_sentences = [sentence for _, sentence, _ in top]

    if bullet_mode:
        return "\n• " + "\n• ".join(summary_sentences)
    return " ".join(summary_sentences)


def paraphrase_summary(text: str) -> str:
    if not text.strip():
        return text

    sentences = nltk.sent_tokenize(text)
    result = []
    for sentence in sentences:
        sentence = sentence.strip()
        if not sentence:
            continue
        if sentence.startswith("•"):
            result.append(sentence)
        else:
            sentence = sentence[0].upper() + sentence[1:] if len(sentence) > 1 else sentence.upper()
            result.append(sentence)

    if text.strip().startswith("•"):
        return "\n".join(result)
    return " ".join(result)
