import pytest
from agent.budget import BudgetTracker, BudgetExceededError

def test_budget_tracks_tokens():
    b = BudgetTracker(max_usd=0.10)
    b.add(1000, 500)
    assert b.input_tokens == 1000
    assert b.output_tokens == 500

def test_budget_cost_calculation():
    b = BudgetTracker(max_usd=0.10)
    b.add(1000000, 0)  # 1 million input tokens
    assert abs(b.cost_usd - 1.0) < 0.001

def test_budget_exceeded_raises():
    b = BudgetTracker(max_usd=0.000001)
    b.add(10000, 10000)
    with pytest.raises(BudgetExceededError):
        b.check()

def test_budget_summary():
    b = BudgetTracker(max_usd=0.10)
    b.add(500, 200)
    summary = b.summary()
    assert summary["total_tokens"] == 700
    assert "cost_usd" in summary