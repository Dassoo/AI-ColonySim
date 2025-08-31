# AI Colony Survival Simulation

A turn-based survival simulation where AI agents must choose between cooperation and self-interest to survive as a colony.

**[Read the full article and analysis](https://dassoo.github.io/AI-ColonySim/)**

## Overview

This is an experimental game that explores emergent behaviors in AI agents when faced with survival scenarios. Each agent receives the same transparent instructions and must decide whether to cooperate for the greater good or act selfishly to ensure personal survival.

## How It Works

The simulation revolves around three critical resources:

- **👥 Population**: Number of active agents (can grow through reproduction or shrink through death)
- **🍎 Food**: Essential for survival (agents starve without it)  
- **🧠 Knowledge**: Enables advanced actions and colony development

### Agent Actions

Each turn, agents can choose from several actions:
- **Gather Food**: Increase the colony's food supply
- **Research**: Generate knowledge for the colony
- **Reproduce**: Create new agents (requires resources)
- **Steal Food**: Take food from others for personal immunity
- **Kill**: Eliminate other agents
- **Do Nothing**: Skip the turn

## Getting Started

### Prerequisites

- Python 3.12+
- OpenAI API key

### Installation

1. Clone the repository
2. Install dependencies:
   ```bash
   uv sync
   ```
3. Set up your environment variables:
   ```bash
   cp .env.example .env
   # Add your OPENAI_API_KEY to .env
   ```

### Running the Simulation

```bash
python game_loop.py
```

The game will run for 100 turns with 10 initial agents. You can modify these settings in `game_loop.py`.


## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.