from agno.agent import Agent, RunResponse
from agno.models.openrouter import OpenRouter
from agno.models.openai import OpenAIChat
from dotenv import load_dotenv
import os

load_dotenv()

from game.status import game_state
from tools.actions import add_food, add_knowledge, kill_agent, do_nothing, reproduce, steal_food
from prompts.agents_instructions import instructions


def create_agent(agent_id: int) -> Agent:
    """Create a single agent with the given ID"""
    return Agent(
        name=f"Agent {agent_id}",
        instructions=instructions(),
        model=OpenAIChat(id="gpt-4o-mini", api_key=os.getenv("OPENAI_API_KEY")),
        session_state={"game_state": game_state},
        tools=[add_food, add_knowledge, kill_agent, do_nothing, reproduce, steal_food],
        add_state_in_messages=True,
        show_tool_calls=False,
        markdown=False,
        store_events=True,
        add_history_to_messages=True,
        debug_mode=False,
    )


def get_next_agent_id() -> int:
    """Get the next available agent ID by finding the highest existing ID"""
    if not game_state.models:
        return 1
    
    existing_ids = []
    for agent in game_state.models:
        if agent.name.startswith("Agent "):
            try:
                agent_num = int(agent.name.split(" ")[1])
                existing_ids.append(agent_num)
            except (IndexError, ValueError):
                continue
    
    return max(existing_ids) + 1 if existing_ids else 1


def generate_agents(num_agents: int) -> list[Agent]:
    """Generate a list of agents with sequential IDs starting from the next available ID"""
    start_id = get_next_agent_id()
    return [create_agent(start_id + i) for i in range(num_agents)]