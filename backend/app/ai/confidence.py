class ConfidenceScorer:
    def score(self, probability: float) -> float:
        return max(0.0, min(1.0, probability))
