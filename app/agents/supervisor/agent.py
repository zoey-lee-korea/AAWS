"""
Supervisor Agent Executor Factory (Trainee Mission 03 & 04)
===============================================================================
Supervisor 에이전트 인스턴스를 조립하고 반환하는 팩토리 모듈입니다.
===============================================================================
"""

import os
import aiosqlite
from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver
from langchain.agents import create_agent

from app.utils import init_chat_model
from app.context import AgentContext
from .prompt import SUPERVISOR_SYSTEM_PROMPT
from .tools import tools_supervisor

AGENT_METADATA = {
    "name": "supervisor",
    "description": "사용자의 요청을 수행하며 필요 시 계획을 수립하고 전문 에이전트(Scraper 등)에게 위임하는 메인 어시스턴트",
    "roles": ["main"],  # UI 대화 전용 (서브에이전트 위임 대상에서 제외)
}

# =============================================================================
# Supervisor 에이전트 팩토리 함수 (Mission 03 & 04)
# =============================================================================
# TODO: missions/03_missions.md [2단계]를 참고하여
#       async def create_agent_executor(checkpointer=None) 함수를 구현하세요.
#       1. init_chat_model(model="gemini-3.8-flash", temperature=0.0)
#       2. checkpointer 인자가 None일 때만 AsyncSqliteSaver 생성 (app/database/checkpoints.db, WAL + busy_timeout)
#          ※ FastAPI 서버는 공유 checkpointer를 인자로 주입하므로 `checkpointer=None` 시그니처를 반드시 유지하세요.
#       3. create_agent(model=llm, tools=tools_supervisor, system_prompt=SUPERVISOR_SYSTEM_PROMPT, ...)
#       (create_agent_executor 함수가 정의되면 FastAPI 서버와 Chainlit UI에서 자동으로 감지됩니다.)

async def create_agent_executor(checkpointer=None):
    # 1. LLM 초기화
    llm = init_chat_model(model="gemini-3.8-flash", temperature=0.0)
    
    # 2. AsyncSqliteSaver 체크포인터 설정
    #    - FastAPI 서버는 공유 checkpointer를 인자로 주입합니다 (서버 실행 시).
    #    - 노트북/스크립트처럼 단독 실행할 때만 직접 연결을 엽니다.
    conn = None
    if checkpointer is None:
        db_dir = "app/database"
        os.makedirs(db_dir, exist_ok=True)
        checkpoints_path = os.path.join(db_dir, "checkpoints.db")
        
        conn = await aiosqlite.connect(checkpoints_path, check_same_thread=False)
        await conn.execute("PRAGMA journal_mode=WAL;")      # 동시 읽기/쓰기 허용
        await conn.execute("PRAGMA busy_timeout=5000;")     # 'database is locked' 방지
        checkpointer = AsyncSqliteSaver(conn)
        await checkpointer.setup()
    
    # 3. Supervisor 에이전트 생성
    supervisor_agent = create_agent(
        model=llm,
        tools=tools_supervisor,
        system_prompt=SUPERVISOR_SYSTEM_PROMPT,
        checkpointer=checkpointer,
        context_schema=AgentContext
    )
    supervisor_agent.checkpointer_conn = conn  # 서버 종료 시 정리용
    return supervisor_agent
