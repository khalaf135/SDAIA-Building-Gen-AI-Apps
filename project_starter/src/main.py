import asyncio

import structlog
import typer

from src.agent.orchestration import OrchestratorAgent
from src.config import settings
from src.logger import configure_logging

configure_logging()
logger = structlog.get_logger()

app = typer.Typer(help="AI Research Agent CLI")


@app.command()
def research(
    query: str = typer.Argument(..., help="The research query to run."),
    model: str = typer.Option(None, help="LLM model to use (overrides settings)."),
    max_steps: int = typer.Option(settings.max_steps, help="Max ReAct steps."),
):
    """Run the AI research agent on a query."""
    resolved_model = model or settings.model_name
    agent = OrchestratorAgent(model=resolved_model, max_steps=max_steps)
    
    print(f"Starting research with model: {resolved_model}...")
    result = asyncio.run(agent.run(query))
    
    print("\n--- FINAL REPORT ---\n")
    print(result.get("answer", "No answer returned."))


if __name__ == "__main__":
    app()
