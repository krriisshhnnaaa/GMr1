from dataclasses import dataclass
from typing import Protocol
from ..gmail.adapter import NormalizedEmail
from ..models import Category


@dataclass
class ClassificationResult:
    category: Category
    confidence: float
    reason: str
    model: str


class EmailClassifier(Protocol):
    def classify(self, email: NormalizedEmail) -> ClassificationResult: ...
