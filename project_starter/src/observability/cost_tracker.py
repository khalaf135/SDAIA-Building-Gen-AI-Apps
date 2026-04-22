import logging
from dataclasses import dataclass, field
from litellm import completion_cost

logger = logging.getLogger(__name__)

@dataclass
class StepCost:
    step_number: int
    model: str
    input_tokens: int
    output_tokens: int
    cost_usd: float
    is_tool_call: bool = False

@dataclass
class QueryCost:
    query: str
    steps: list[StepCost] = field(default_factory=list)
    total_cost_usd: float = 0.0
    total_input_tokens: int = 0
    total_output_tokens: int = 0

    def add_step(self, step: StepCost):
        self.steps.append(step)
        self.total_cost_usd += step.cost_usd
        self.total_input_tokens += step.input_tokens
        self.total_output_tokens += step.output_tokens

class CostTracker:
    """
    Tracks costs across agent executions.
    """
    def __init__(self):
        self.queries: list[QueryCost] = []
        self._current_query: QueryCost | None = None

    def start_query(self, query: str):
        self._current_query = QueryCost(query=query)

    def log_completion(self, step_number: int, response, is_tool_call: bool = False):
        """
        Log a completion response's cost.
        """
        if not self._current_query:
            return

        usage = getattr(response, "usage", None)
        input_tokens = getattr(usage, "prompt_tokens", 0) if usage else 0
        output_tokens = getattr(usage, "completion_tokens", 0) if usage else 0

        try:
            cost_usd = completion_cost(completion_response=response)
        except Exception as e:
            logger.warning(f"Could not calculate completion cost: {e}")
            cost_usd = 0.0

        model = getattr(response, "model", "unknown")

        step_cost = StepCost(
            step_number=step_number,
            model=model,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            cost_usd=cost_usd,
            is_tool_call=is_tool_call
        )
        self._current_query.add_step(step_cost)

    def end_query(self):
        if self._current_query:
            self.queries.append(self._current_query)
            self._current_query = None

    def print_cost_breakdown(self):
        if not self.queries:
            print("No completed queries to display.")
            return
            
        print("\n=== Cost Breakdown ===")
        for i, query in enumerate(self.queries, 1):
            print(f"\nQuery {i}: {query.query}")
            print(f"Total Cost: ${query.total_cost_usd:.6f}")
            print(f"Tokens: {query.total_input_tokens} in / {query.total_output_tokens} out")
            print("Steps:")
            for step in query.steps:
                tool_label = " (Tool Call)" if step.is_tool_call else ""
                print(f"  - Step {step.step_number}{tool_label} [{step.model}]: "
                      f"${step.cost_usd:.6f} ({step.input_tokens} in, {step.output_tokens} out)")
        print("======================")

