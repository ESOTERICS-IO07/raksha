from .providers import IntentProvider, MockIntentProvider
from .schemas import IntentResult


class IntentService:
    def __init__(self, provider: IntentProvider | None = None):
        self.provider = provider or MockIntentProvider()

    def analyze(self, reason: str | None) -> IntentResult:
        return self.provider.classify(reason or "")