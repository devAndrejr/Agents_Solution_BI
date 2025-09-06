from abc import ABC, abstractmethod

class BaseLLMAdapter(ABC):
    @abstractmethod
    def get_completion(self, prompt: str) -> str:
        pass
