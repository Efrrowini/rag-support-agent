from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

analyzer = SentimentIntensityAnalyzer()

ESCALATION_KEYWORDS = [
    "speak to human", "human agent", "real person",
    "not helpful", "useless", "terrible", "worst",
    "I want a refund", "this is ridiculous", "connect me to agent"
]

NEGATIVE_THRESHOLD = -0.4
ESCALATION_COUNT = 3


def score_message(text: str) -> float:
    scores = analyzer.polarity_scores(text)
    return scores["compound"]


def check_escalation(history_scores: list[float], message: str) -> bool:
    # Keyword check — instant escalation
    message_lower = message.lower()
    for keyword in ESCALATION_KEYWORDS:
        if keyword in message_lower:
            return True

    # Sentiment check — 3+ consecutive negative messages
    if len(history_scores) >= ESCALATION_COUNT:
        last_n = history_scores[-ESCALATION_COUNT:]
        if all(s < NEGATIVE_THRESHOLD for s in last_n):
            return True

    return False