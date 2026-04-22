"""
Multi-agent orchestration layer.

Design and implement your own orchestration strategy here.
This file is entirely yours — there is no single correct answer.
"""

from src.agent.base import BaseAgent
from src.agent.prompts import (
    ANALYST_PROMPT,
    FACT_CHECKER_PROMPT,
    PLANNER_PROMPT,
    RESEARCHER_PROMPT,
    WRITER_PROMPT,
)
from src.config import settings


class OrchestratorAgent:
    """
    Your multi-agent orchestrator. Design your own pipeline.

    You have access to:
    - BaseAgent: a single ReAct agent you can instantiate with any system prompt
    - prompts.py: ready-made prompts (RESEARCHER_PROMPT, ANALYST_PROMPT,
      WRITER_PROMPT, FACT_CHECKER_PROMPT, PLANNER_PROMPT)
    - The tool registry: search_web and read_webpage are available once
      you've completed the tools/registry.py TODO.

    Ideas to get you started:
    - Chain researcher → analyst → writer in sequence
    - Run researcher and fact-checker in PARALLEL with asyncio.gather(),
      then synthesize their outputs
    - Build a retry loop: if confidence is low, re-run the researcher
    - Add a planner agent that breaks the query into sub-tasks first
    - Invent your own pattern!

    The only requirement: return {"answer": "...", "metadata": {...}}
    """

    def __init__(self, model: str = None, max_steps: int = 10):
        resolved_model = model or settings.model_name
        
        self.researcher = BaseAgent(
            model=resolved_model,
            max_steps=max_steps,
            agent_name="Researcher",
            system_prompt=RESEARCHER_PROMPT,
        )
        
        self.writer = BaseAgent(
            model=resolved_model,
            max_steps=max_steps,
            agent_name="Writer",
            system_prompt=WRITER_PROMPT,
        )

    async def run(self, query: str) -> dict:
        # 1. Research
        research_result = await self.researcher.run(query)
        research_findings = research_result.get("answer", "")
        
        # 2. Write based on findings
        writer_query = (
            f"Original User Request: {query}\n\n"
            f"Research Findings:\n{research_findings}\n\n"
            f"Please write a comprehensive report."
        )
        writer_result = await self.writer.run(writer_query)
        
        return {
            "answer": writer_result.get("answer", ""),
            "metadata": {
                "researcher_trace": research_result.get("metadata", {}).get("trace_id"),
                "writer_trace": writer_result.get("metadata", {}).get("trace_id"),
                "total_steps": (
                    research_result.get("metadata", {}).get("total_steps", 0) + 
                    writer_result.get("metadata", {}).get("total_steps", 0)
                )
            }
        }
