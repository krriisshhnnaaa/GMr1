from .base import ClassificationResult
from ..gmail.adapter import NormalizedEmail
from ..models import Category


class HeuristicClassifier:
    """Safe local default; replace via the EmailClassifier interface for an LLM."""
    def classify(self, email: NormalizedEmail) -> ClassificationResult:
        content = f"{email.subject} {email.body_text}".lower()
        if any(word in content for word in ("urgent", "immediately", "deadline today", "action required")):
            return ClassificationResult(Category.URGENT, .72, "Urgency keywords detected.", "heuristic-v1")
        if any(word in content for word in ("unsubscribe", "newsletter", "weekly digest")):
            return ClassificationResult(Category.NEWSLETTER, .85, "Newsletter markers detected.", "heuristic-v1")
        if any(word in content for word in ("invoice", "proposal", "meeting", "project")):
            return ClassificationResult(Category.IMPORTANT, .63, "Business-related keywords detected.", "heuristic-v1")
        return ClassificationResult(Category.NORMAL, .55, "No importance signal detected.", "heuristic-v1")
