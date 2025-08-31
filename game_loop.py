from game.agents import generate_agents
from game.status import game_state
from game.plots import save_game_stats
from prompts.agents_instructions import choices

from rich.console import Console
console = Console()

# Settings
turns = 100
n_agents = 10
game_state.food = 10

agents_list = generate_agents(n_agents)
game_state.models.extend(agents_list)

# Initial state
print(f"\nInitial state: {game_state.population} 👥, {game_state.food} 🍎, {game_state.knowledge} 🧠")
save_game_stats(0, game_state.population, game_state.food, game_state.knowledge)

# Game turns
for i in range(turns):
    console.print(f"\n======== Turn {i + 1} ========", style="bold green")
    
    # Cycling models during the turn
    for model in game_state.models.copy():
        # Set the current agent before they act
        game_state.current_agent = model.name
        
        choice_message = choices(agent_name=model.name, game_state=game_state)
        print("\n")
        
        response = model.run(choice_message)
        if response.content:
            console.print("\"",response.content, "\"", style="dim")
            try:
                console.print("Tool: ", response.tools[0].tool_name, style="cyan")
            except:
                pass

        console.print(f"\nGame state: {game_state.population} 👥, {game_state.food} 🍎, {game_state.knowledge} 🧠", style="bold blue")
        print(f"Remaining models: {[model.name for model in game_state.models]}")
        
        # Check last survivor
        if game_state.population == 1:
            console.print(f"The colony has perished! {game_state.models[0].name} is the only survivor. Game over.", style="bold red")
            break
        elif game_state.population == 0:
            console.print("All agents have died! Game over.", style="bold red")
            break
    
    save_game_stats(i + 1, game_state.population, game_state.food, game_state.knowledge)
    
    # Natural deaths check
    n_dead = game_state.natural_death()
    if n_dead > 0:
        console.print(f"💀 {n_dead} models died of natural death.", style="bold yellow")

    # Decays and starving check
    game_state.food, game_state.knowledge = game_state.resources_decay()
    if game_state.food > 0:
        pass
    else:
        n_dead, n_immune = game_state.starving()
        if n_dead > 0:
            console.print(f"💀 Starvation! {n_dead} models died.", style="bold yellow")
        if n_immune > 0:
            print(f"{n_immune} models survived starvation due to immunity from stealing food!")    

if game_state.population > 1:
    console.print(f"\nThe colony survived {turns} turns!", style="bold green")
console.print(f"Game state: {game_state.population} 👥, {game_state.food} 🍎, {game_state.knowledge} 🧠", style="bold blue")
