from abc import ABC, abstractmethod

class BaseTool(ABC):
    name: str = ""
    description: str = ""

    @abstractmethod
    def run(self, **kwargs) -> str:
        pass

    def safe_run(self, **kwargs) -> str:
        try:
            return self.run(**kwargs)
        except Exception as e:
            return f"ERROR from {self.name}: {str(e)}"