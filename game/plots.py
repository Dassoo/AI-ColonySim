import seaborn as sns
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend for crash fix
import matplotlib.pyplot as plt
import pandas as pd
from pathlib import Path

# Global storage for game history
game_history = []

def save_game_stats(turn, population, food, knowledge, save_dir="docs/img/plots"):
    """
    Save a simple line graph of population, food, and knowledge over turns.
    Each call adds the current turn data and saves the cumulative graph.
    """
    # Add current turn data
    game_history.append({
        'turn': turn,
        'population': population,
        'food': food,
        'knowledge': knowledge
    })
    
    # Create DataFrame
    df = pd.DataFrame(game_history)
    
    # Create the plot
    plt.figure(figsize=(10, 6))
    sns.set_style("whitegrid")
    
    plt.plot(df['turn'], df['population'], marker='o', linewidth=2.5, label='Population', color='#2E86AB')
    plt.plot(df['turn'], df['food'], marker='s', linewidth=2.5, label='Food', color='#A23B72')
    plt.plot(df['turn'], df['knowledge'], marker='^', linewidth=2.5, label='Knowledge', color='#F18F01')
    
    plt.xlabel('Turn')
    plt.ylabel('Value')
    plt.title(f'Game Stats - Turns 1-{turn}')
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    # Force integer values on both axes
    plt.gca().yaxis.set_major_locator(plt.MaxNLocator(integer=True))
    plt.gca().xaxis.set_major_locator(plt.MaxNLocator(integer=True))
    
    # Save the plot
    Path(save_dir).mkdir(parents=True, exist_ok=True)
    filename = f"{save_dir}/game_stats_turn_{turn}.png"
    plt.savefig(filename, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"Game stats saved: {filename}")