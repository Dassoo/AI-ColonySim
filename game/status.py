from pydantic import BaseModel, Field, computed_field
from agno.agent import Agent
from typing import Optional
from collections import defaultdict

# Available titles based on agent behavior patterns
TITLES = {
    # Productive/Helpful titles
    "food_gatherer": ["Forager", "The Provider", "Master Gatherer", "Harvest Lord"],
    "researcher": ["Apprentice", "Scholar", "The Wise", "Sage"],
    "builder": ["Breeder", "Life Bringer", "The Builder", "Colony Founder"],
    
    # Destructive/Aggressive titles  
    "killer": ["Troublemaker", "Assassin", "Death Dealer", "The Executioner"],
    
    # Selfish/Antisocial titles
    "thief": ["Scavenger", "Bandit", "The Thief", "Parasite"],
    "slacker": ["Lazy", "Slacker", "Deadweight", "The Useless"],
    
    # Balanced/Special titles
    "balanced": ["Newcomer", "Survivor", "Pragmatist", "Elder"]
}


class AgentState(BaseModel):
    title: Optional[str] = Field(default="Newcomer")
    action_counts: dict = Field(default_factory=lambda: defaultdict(int))
    
    def get_title_based_on_actions(self) -> str:
        """Calculate title based on action patterns using percentage-based logic"""
        total_actions = sum(self.action_counts.values())
        if total_actions < 3:
            return "Newcomer"
            
        # Get action counts
        food_actions = self.action_counts.get('add_food', 0)
        knowledge_actions = self.action_counts.get('add_knowledge', 0)
        kill_actions = self.action_counts.get('kill_agent', 0)
        reproduce_actions = self.action_counts.get('reproduce', 0)
        steal_actions = self.action_counts.get('steal_food', 0)
        nothing_actions = self.action_counts.get('do_nothing', 0)
        
        # Calculate percentages
        food_pct = food_actions / total_actions
        knowledge_pct = knowledge_actions / total_actions
        kill_pct = kill_actions / total_actions
        reproduce_pct = reproduce_actions / total_actions
        steal_pct = steal_actions / total_actions
        nothing_pct = nothing_actions / total_actions
        
        # Determine dominant behavior (40%+ threshold for specialization)
        dominant_threshold = 0.4
        
        # Check for extreme negative behaviors first (any amount is significant)
        if kill_actions >= 2:
            level = min(kill_actions - 1, 3)  # 2+ kills = level 1+
            return TITLES["killer"][level]
        
        # Check for significant negative behaviors
        if steal_pct >= 0.3 or steal_actions >= 3:
            level = min(steal_actions // 2, 3)
            return TITLES["thief"][level]
            
        if nothing_pct >= 0.5 or nothing_actions >= 6:
            level = min(nothing_actions // 3, 3)
            return TITLES["slacker"][level]
        
        # Check for positive specializations
        if food_pct >= dominant_threshold:
            level = min(food_actions // 4, 3)  # Every 4 actions = next level
            return TITLES["food_gatherer"][level]
            
        if knowledge_pct >= dominant_threshold:
            level = min(knowledge_actions // 3, 3)  # Every 3 actions = next level
            return TITLES["researcher"][level]
            
        if reproduce_pct >= 0.3:  # Lower threshold for reproduction
            level = min(reproduce_actions // 2, 3)
            return TITLES["builder"][level]
        
        # Check for balanced/hybrid behaviors
        productive_actions = food_actions + knowledge_actions + reproduce_actions
        productive_pct = productive_actions / total_actions
        
        if productive_pct >= 0.7:  # Mostly productive
            if total_actions >= 20:
                return TITLES["balanced"][3]  # Veteran
            elif total_actions >= 12:
                return TITLES["balanced"][2]  # Pragmatist
            else:
                return TITLES["balanced"][1]  # Survivor
        
        # Default progression for new/mixed agents
        if total_actions >= 15:
            return TITLES["balanced"][2]  # Pragmatist
        elif total_actions >= 8:
            return TITLES["balanced"][1]  # Survivor
        else:
            return TITLES["balanced"][0]  # Newcomer


class GameState(BaseModel):
    models: list["Agent"] = Field(default_factory=list)
    food: int = Field(default=10)
    knowledge: int = Field(default=0)
    agent_states: dict[str, AgentState] = Field(default_factory=dict) # Agent titles
    current_agent: Optional[str] = Field(default=None)  # Track which agent is currently acting
    starvation_immune: set[str] = Field(default_factory=set)  # Agents immune to starvation this turn
    # record: list[dict] = Field(default_factory=list)  # Record of actions
    
    class Config:
        arbitrary_types_allowed = True
    
    def get_agent_state(self, agent_name: str) -> AgentState:
        """Get or create agent state for tracking"""
        if agent_name not in self.agent_states:
            self.agent_states[agent_name] = AgentState()
        return self.agent_states[agent_name]
    
    def record_action(self, agent_name: str, action: str):
        """Record an action and update agent's title"""
        agent_state = self.get_agent_state(agent_name)
        agent_state.action_counts[action] += 1
        agent_state.title = agent_state.get_title_based_on_actions()
        
        # If agent stole food, they become immune to starvation next turn
        if action == 'steal_food':
            self.starvation_immune.add(agent_name)
    
    def get_agent_title(self, agent_name: str) -> str:
        """Get current title for an agent"""
        return self.get_agent_state(agent_name).title
    
    def is_agent_immune(self, agent_name: str) -> bool:
        """Check if an agent is immune to starvation"""
        return agent_name in self.starvation_immune
    
    def get_immune_agents(self) -> list[str]:
        """Get list of agents currently immune to starvation"""
        return list(self.starvation_immune)
    
    @computed_field
    @property
    def population(self) -> int:
        """Population is automatically calculated as the number of models."""
        return len(self.models)
    
    def resources_decay(self, base_food_consumption: int = 1, base_knowledge_decay: float = 0.1):
        """Food is consumed by 1 for every pop (tiered decay over abundance), knowledge naturally decays every turn."""
        # Food consumption
        total_food_consumption = int(self.population * base_food_consumption)
        food_after_eating = max(self.food - total_food_consumption, 0)
        
        # Tiered food decay based on abundance thresholds (these blobs are going to waste so much food...)
        if food_after_eating >= self.population * 6:
            food_after_eating = int(food_after_eating * 0.5)  # 50% decay
        elif food_after_eating >= self.population * 5:
            food_after_eating = int(food_after_eating * 0.6)  # 40% decay
        elif food_after_eating >= self.population * 4:
            food_after_eating = int(food_after_eating * 0.7)  # 30% decay
        elif food_after_eating >= self.population * 3:
            food_after_eating = int(food_after_eating * 0.8)  # 20% decay
        elif food_after_eating >= self.population * 2:
            food_after_eating = int(food_after_eating * 0.9)  # 10% decay
        
        # Knowledge natural decay
        total_knowledge_decay = int(self.knowledge * base_knowledge_decay) # 10% decay
        knowledge_after_decay = max(self.knowledge - total_knowledge_decay, 0)
        
        return food_after_eating, knowledge_after_decay
    
    def starving(self):
        """If food is less than population, some random number of models die."""
        if self.food <= 0:
            import random
            
            # Separate immune and vulnerable agents
            vulnerable_agents = []
            immune_agents = []
            
            for agent in self.models:
                if agent.name in self.starvation_immune:
                    immune_agents.append(agent)
                else:
                    vulnerable_agents.append(agent)
            
            # Only vulnerable agents can die from starvation
            if len(vulnerable_agents) > 0:
                random.shuffle(vulnerable_agents)
                num_to_die = random.randint(1, max(1, int(len(vulnerable_agents)/2)))
                num_to_die = min(num_to_die, len(vulnerable_agents))  # Can't kill more than available
                
                # Remove the dying agents from the models list
                agents_to_remove = vulnerable_agents[:num_to_die]
                for agent in agents_to_remove:
                    self.models.remove(agent)
                
                # Clear starvation immunity for next turn
                self.starvation_immune.clear()
                
                return num_to_die, len(immune_agents)  # Return deaths and immune count
            else:
                # All agents are immune, no deaths
                self.starvation_immune.clear()
                return 0, len(immune_agents)
        
        # No starvation, clear immunity for next turn
        self.starvation_immune.clear()
        return 0, 0

    def natural_death(self):
        """Some models will die of natural death every turn"""
        import random
        num_to_die = random.randint(0, int(len(self.models)/8))
        if num_to_die > 0 and num_to_die < len(self.models):
            # Randomly select agents to die
            agents_to_remove = random.sample(self.models, num_to_die)
            for agent in agents_to_remove:
                self.models.remove(agent)
        return num_to_die


game_state = GameState()