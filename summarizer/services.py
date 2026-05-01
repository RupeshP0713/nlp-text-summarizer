from dataclasses import dataclass

import nltk

from app.core.nlp_engine import generate_summary, get_top_keywords


@dataclass
class SummaryStats:
    words: int
    sentences: int


@dataclass
class SummaryResult:
    summary: str
    stats: SummaryStats


def _num_sentences_from_ratio(length_ratio: float) -> int:
    return max(2, int(5 + length_ratio * 15))


def _stats(text: str) -> SummaryStats:
    stripped = text.strip()
    if not stripped:
        return SummaryStats(words=0, sentences=0)
    return SummaryStats(words=len(stripped.split()), sentences=len(nltk.sent_tokenize(stripped)))


def create_summary(text: str, mode: str, length_ratio: float, keywords: list[str]) -> SummaryResult:
    summary = generate_summary(
        text=text,
        num_sentences=_num_sentences_from_ratio(length_ratio),
        bullet_mode=mode == "bullet",
        boost_keywords=keywords or None,
    )
    return SummaryResult(summary=summary, stats=_stats(summary))


def extract_keywords(text: str, top_n: int = 8) -> list[str]:
    return get_top_keywords(text=text, top_n=top_n)
