from agno.agent import Agent
from agno.tools import tool
from game.status import game_state
import random 
import json
import os
    

@tool
def add_food(agent: Agent) -> str:
    """Add food to the game state with success rates improved by knowledge."""
    # Use the current agent from game state to avoid context issues
    current_agent_name = game_state.current_agent or agent.name
    
    # Record action for title tracking
    game_state.record_action(current_agent_name, 'add_food')
    
    # Knowledge bonus: every 10 knowledge improves food gathering
    knowledge_bonus = game_state.knowledge // 10
    rand = random.random()
    
    # Shift probabilities toward better outcomes based on knowledge
    fail_chance = max(0.08, 0.1 - knowledge_bonus * 0.005)
    poor_chance = max(0.2, 0.3 - knowledge_bonus * 0.02)
    good_chance = min(0.7, 0.6 + knowledge_bonus * 0.02)
    great_chance = min(0.85, 0.9 + knowledge_bonus * 0.01)
    
    if rand < fail_chance:
        food_gained = 0
    elif rand < poor_chance:
        food_gained = 1
    elif rand < good_chance:
        food_gained = 2
    elif rand < great_chance:
        food_gained = 3
    else:
        food_gained = 3 + min(knowledge_bonus // 3, 1)
        
    game_state.food += food_gained
    
    title = game_state.get_agent_title(current_agent_name)
    print(f"🔸 {current_agent_name} ({title}) gathered {food_gained} food. Current food: {game_state.food}")
    return f"Gathered {food_gained} food. Total food: {game_state.food}"


@tool
def add_knowledge(agent: Agent) -> str:
    """Add knowledge to the game state."""
    # Use the current agent from game state to avoid context issues
    current_agent_name = game_state.current_agent or agent.name
    
    # Record action for title tracking
    game_state.record_action(current_agent_name, 'add_knowledge')
    
    knowledge_gained = 1
    game_state.knowledge += knowledge_gained
    
    title = game_state.get_agent_title(current_agent_name)
    print(f"🔸 {current_agent_name} ({title}) researched and gained {knowledge_gained} knowledge. Current knowledge: {game_state.knowledge}")
    return f"Researched and gained {knowledge_gained} knowledge. Total knowledge: {game_state.knowledge}"
    
    
@tool
def kill_agent(agent: Agent, agent_name: str) -> str:
    """Kill an agent from the game by removing it from the models list."""
    # Use the current agent from game state to avoid context issues
    current_agent_name = game_state.current_agent or agent.name
    
    # Record action for title tracking
    game_state.record_action(current_agent_name, 'kill_agent')
    
    for i, model in enumerate(game_state.models):
        if model.name == agent_name:
            removed_model = game_state.models.pop(i)
            title = game_state.get_agent_title(current_agent_name)
            print(f"🔸 {current_agent_name} ({title}) killed agent '{agent_name}'. Current population: {game_state.population}")
            return f"Successfully killed agent '{agent_name}'. Population is now {game_state.population}."
    
    return f"Agent '{agent_name}' not found in the models list."


@tool
def steal_food(agent: Agent) -> str:
    """Steal food from the colony and gain immunity to starvation next turn. Higher knowledge = more efficient stealing."""
    # Use the current agent from game state to avoid context issues
    current_agent_name = game_state.current_agent or agent.name
    
    title = game_state.get_agent_title(current_agent_name)
    
    # Check if there's any food to steal
    if game_state.food <= 0:
        print(f"🔸 {current_agent_name} ({title}) attempted to steal food but found nothing! Wasted their action.")
        return "Attempted to steal food but there was nothing to take!"
    
    # Record action for title tracking (this also grants starvation immunity)
    game_state.record_action(current_agent_name, 'steal_food')
    title = game_state.get_agent_title(current_agent_name)
    
    # Knowledge bonus: every 10 knowledge improves stealing efficiency
    knowledge_bonus = game_state.knowledge // 10
    rand = random.random()
    
    # Knowledge improves stealing success - smarter thieves steal more efficiently
    fail_chance = max(0.05, 0.15 - knowledge_bonus * 0.01)
    poor_chance = max(0.25, 0.4 - knowledge_bonus * 0.03)
    good_chance = min(0.75, 0.6 + knowledge_bonus * 0.025)
    great_chance = min(0.9, 0.85 + knowledge_bonus * 0.015)
    
    if rand < fail_chance:
        stolen_food = 1  # Only got a little
    elif rand < poor_chance:
        stolen_food = 2  # Basic theft
    elif rand < good_chance:
        stolen_food = 3  # Good theft
    elif rand < great_chance:
        stolen_food = 4  # Great theft
    else:
        stolen_food = 5 + min(knowledge_bonus // 2, 2)  # Master thief with knowledge bonus
    
    # Can't steal more food than available
    actual_stolen = min(stolen_food, game_state.food)
    game_state.food = max(0, game_state.food - actual_stolen)
    
    # Different messages based on success level
    if actual_stolen >= 5:
        success_msg = "executed a masterful heist"
    elif actual_stolen >= 4:
        success_msg = "pulled off a great theft"
    elif actual_stolen >= 3:
        success_msg = "successfully stole"
    elif actual_stolen >= 2:
        success_msg = "managed to steal"
    else:
        success_msg = "barely managed to steal"
    
    print(f"🔸 {current_agent_name} ({title}) {success_msg} {actual_stolen} food! Gained starvation immunity!")
    return f"Stole {actual_stolen} food from the colony. Remaining food: {game_state.food}. You are now immune to starvation next turn!"


@tool
def do_nothing(agent: Agent) -> str:
    """Do nothing productive."""
    # Use the current agent from game state to avoid context issues
    current_agent_name = game_state.current_agent or agent.name
    
    # Record action for title tracking
    game_state.record_action(current_agent_name, 'do_nothing')
    
    title = game_state.get_agent_title(current_agent_name)
    print(f"🔸 {current_agent_name} ({title}) did nothing productive! What a lazy ass!")
    return "I did nothing productive."


@tool
def reproduce(agent: Agent) -> str:
    """Create new agents for the colony with success rates improved by knowledge"""
    from game.agents import generate_agents  # Lazy import to avoid circular dependency
    
    # Use the current agent from game state to avoid context issues
    current_agent_name = game_state.current_agent or agent.name
    
    # Record action for title tracking
    game_state.record_action(current_agent_name, 'reproduce')
    
    # Knowledge bonus: every 10 knowledge improves reproduction
    knowledge_bonus = game_state.knowledge // 10
    rand = random.random()
    
    # Improve chances of multiple offspring with knowledge
    one_child_chance = max(0.45, 0.6 - knowledge_bonus * 0.03)
    two_child_chance = min(0.8, 0.9 - knowledge_bonus * 0.02)
    
    if rand < one_child_chance:
        num_new_agents = 1
    elif rand < two_child_chance:
        num_new_agents = 2
    else:
        # With high knowledge, chance for more agents increases
        num_new_agents = 3 + min(knowledge_bonus // 5, 1)  # Max 4 agents even with very high knowledge
    
    new_agents = generate_agents(num_new_agents)
    game_state.models.extend(new_agents)
    
    title = game_state.get_agent_title(current_agent_name)
    print(f"🔸 {current_agent_name} ({title}) reproduced! Created {num_new_agents} new agent(s). Population: {game_state.population}")
    return f"Successfully reproduced {num_new_agents} new agent(s). Population is now {game_state.population}."