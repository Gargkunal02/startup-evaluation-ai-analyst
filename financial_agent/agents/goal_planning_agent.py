from typing import Dict

from financial_agent.agents.goals.goals_categorization_agent import GoalCategorizationAgent
from financial_agent.services.chat_history_manager import ChatHistoryManager


class GoalPlanningAgent:
    def __init__(self, user_id: str, session_id: str = None, llm_temperature: float = 0.0,
                 chat_history_manager: ChatHistoryManager = None):
        self.session_id = session_id
        self.chat_history_manager = chat_history_manager or ChatHistoryManager()
        self.categorization_agent = GoalCategorizationAgent(
            user_id=user_id,
            session_id=self.session_id,
            chat_history_manager=self.chat_history_manager,
        )

    def handle_query(self, query: str) -> Dict[str, str]:
        """
        Handles goal planning related queries.

        Args:
            query (str): The user's query.

        Returns:
            dict: The response for the query.
        """

        classification = self.categorization_agent.classify_text(query)

        # Handle unsupported queries
        if classification.get("not_supported"):
            return {
                "status": "error",
                "message": "The query does not match any supported category.",
                "classification": classification
            }

        # Route to the appropriate agent
        top_match = classification["top_match"]

        if top_match not in self.categorization_agent.goal_types:
            return {
                "status": "error",
                "message": f"No agent available for the category: {top_match}"
            }

        if top_match in ["Home", "Car", "Education"]:
            agent = self.categorization_agent.agents["goal_with_loans"]
        elif top_match in ["Education"]:
            agent = self.categorization_agent.agents["education_goal"]
        elif top_match in ["Travel"]:
            agent = self.categorization_agent.agents["travel_goal"]
        else:
            return "This category not supported"
        response = agent.handle_query(query)

        return response
