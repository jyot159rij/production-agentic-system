class BudgetExceededError(Exception):
    pass

class BudgetTracker:
    # Claude Haiku pricing per 1K tokens
    COST_PER_1K_INPUT = 0.001
    COST_PER_1K_OUTPUT = 0.005

    def __init__(self, max_usd: float = 0.10):
        self.max_usd = max_usd
        self.input_tokens = 0
        self.output_tokens = 0

    def add(self, input_tokens: int, output_tokens: int):
        self.input_tokens += input_tokens
        self.output_tokens += output_tokens

    @property
    def cost_usd(self):
        return (
            self.input_tokens / 1000 * self.COST_PER_1K_INPUT +
            self.output_tokens / 1000 * self.COST_PER_1K_OUTPUT
        )

    def check(self):
        if self.cost_usd > self.max_usd:
            raise BudgetExceededError(
                f"Budget ${self.max_usd:.4f} exceeded. "
                f"Current cost: ${self.cost_usd:.4f}"
            )

    def summary(self):
        return {
            "input_tokens": self.input_tokens,
            "output_tokens": self.output_tokens,
            "total_tokens": self.input_tokens + self.output_tokens,
            "cost_usd": round(self.cost_usd, 6)
        }