"""
Supervisor Agent Tools (Trainee Mission 03 & 04)
===============================================================================
하위 전문 에이전트(Scraper 등)를 호출하는 invoke_sub_agent 도구 및
Supervisor가 사용하는 전체 도구 목록(tools_supervisor)을 정의합니다.
===============================================================================
"""

import os
import asyncio
from typing import List
from pydantic import BaseModel, Field
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage

from app.utils import normalize_content
from app.tools.plan import enter_plan, exit_plan, task_create, task_list, task_update, check_plan_mode_tool_allowed
from app.tools.common import file_read, file_writer, file_edit, glob_search, grep_search, web_search
from app.agents.scraper import create_agent_executor as create_scraper_executor

# ── 1. 프로덕션 Long-Running 도구 모듈 임포트 ──
from app.tools.supervisor_tools import (
    invoke_sub_agent,
    list_sub_agents,
    get_sub_agent_job_status
)

# =============================================================================
# 1. invoke_sub_agent Pydantic 스키마 및 도구 정의 (Mission 03)
# =============================================================================
# TODO: missions/03_missions.md [2단계]를 참고하여
#       InvokeSubAgentInput 스키마와 invoke_sub_agent 도구를 구현하세요.
#
class InvokeSubAgentInput(BaseModel):
    task_instruction: str = Field(
        description="A clear, actionable step-by-step instruction detailing what the worker agent should crawl, calculate, and report."
    )
    target_file_list: List[str] = Field(
        default_factory=list,
        description="List of relative file paths that the sub-agent needs to inspect or generate (including the Shared Plan File path returned by exit_plan, input data paths, and output artifact paths)."
    )
    subagent_role: str = Field(
        default="scraper",
        description="The persona and specialty of the sub-agent (e.g. 'scraper', 'analyst')."
    )

@tool(args_schema=InvokeSubAgentInput)
async def invoke_sub_agent(task_instruction: str, target_file_list: List[str] = [], subagent_role: str = "scraper") -> str:
    """Forks an isolated, sandboxed sub-agent with a dedicated worker persona to execute focused web scraping, discovery, or data analysis tasks.

    The sub-agent operates in an isolated ReAct loop, writes detailed artifacts directly to disk, and returns only a concise 5-line `[TASK REPORT]` summary (or `[BLOCKER: <reason>]` on failure).

    PROTOCOL — BEFORE CALLING:
      1. For multi-step tasks, call enter_plan(intent='new' or 'revise', goal=...) -> perform any needed read-only discovery -> call exit_plan(plan_name, steps) to publish your finalized plan on the Shared Blackboard.
      2. Register a task with task_create() to track this delegation.
      3. Include the Shared Plan File path (returned by exit_plan) along with target input/output artifact paths in target_file_list so the sub-agent shares the full context.

    PROTOCOL — AFTER RECEIVING RESPONSE:
      - [TASK REPORT] + Status: SUCCESS -> Call task_update(task_id, 'COMPLETED').
      - [BLOCKER: <reason>] -> Call task_update(task_id, 'BLOCKED'). When new evidence supports an alternative path, backtrack via enter_plan(intent='revise', goal=...) -> exit_plan(plan_name, steps) -> task_create(), then re-delegate.
    """
    block_msg = check_plan_mode_tool_allowed("invoke_sub_agent")
    if block_msg:
        return block_msg

    scraper = await create_scraper_executor()
    
    file_list_str = ", ".join(target_file_list) if target_file_list else "None"
    
    # 🌟 [3-Layer Architecture] 범용 Sub-Agent Protocol Overlay 주입
    prompt = f"""[SUB-AGENT MODE - STRICT PROTOCOL]
You are operating as a sub-agent under a Main Agent. You MUST follow these rules:
1. NO greetings or conversational responses. Execute the task immediately.
2. Context & Plan: If a plan is shared, refer to it to understand the broader context.
   Do NOT modify the plan yourself. If adjustments are needed, propose them in your report.
3. On ANY blocker (site blocked / selector failure / access denied):
   STOP immediately and return EXACTLY:
   [BLOCKER: <concise reason>]
4. On success: write all detailed results to disk first, then return EXACTLY:
   [TASK REPORT]
   - Status: SUCCESS
   - Target Files: {file_list_str}
   - Artifacts Created: <created file paths>
   - Summary: <1-2 sentence core finding>
   - Issues: None (or proposed plan adjustments)
══════════════════════════════════════════════════════════
Target Files: {file_list_str}
Instruction: {task_instruction}"""
    
    config = {"configurable": {"thread_id": f"sub_{int(asyncio.get_event_loop().time() * 1000)}"}}
    response = await scraper.ainvoke(
        {"messages": [HumanMessage(content=prompt)]},
        config=config
    )
    
    return normalize_content(response["messages"][-1].content)


# =============================================================================
# 2. Supervisor 도구 바인딩 목록 (tools_supervisor)
# =============================================================================
# TODO: invoke_sub_agent 도구를 구현한 후 아래 리스트에 추가하세요.
#       (Mission 04에서는 app.tools.supervisor_tools의 프로덕션 비동기 도구로 교체할 수 있습니다.)

tools_supervisor = [
    # Planning & Task Board (5종)
    enter_plan, exit_plan, task_create, task_list, task_update,
    
    # Sub-Agent Orchestration (3종)
    list_sub_agents, invoke_sub_agent, get_sub_agent_job_status,
    
    # Common File / Search Tools (6종)
    file_read, file_writer, file_edit, glob_search, grep_search, web_search,
]

__all__ = ["tools_supervisor"]
