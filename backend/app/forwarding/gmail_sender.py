from ..gmail.adapter import NormalizedEmail
from ..classifier.base import ClassificationResult


def build_forward_body(email: NormalizedEmail, result: ClassificationResult) -> str:
    return (f"MAIL AUTOMATION\nClassification: {result.category.value}\nConfidence: {result.confidence:.2f}\n"
            f"Original sender: {email.sender}\nOriginal subject: {email.subject}\n\n--------------------------------\n\n{email.body_text}")


class GmailForwarder:
    def send(self, destination: str, email: NormalizedEmail, result: ClassificationResult) -> None:
        """Integration point for Gmail users.messages.send; intentionally never logs email bodies."""
        raise NotImplementedError("Configure Gmail API credentials to enable sending.")
