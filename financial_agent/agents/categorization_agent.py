import json
import uuid
from typing import Union, Dict

from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain_community.chat_models import ChatOpenAI

from financial_agent.agents.goal_planning_agent import GoalPlanningAgent
from financial_agent.agents.portfolio_analysis_agent import PortfolioAnalysisAgent
from financial_agent.agents.portfolio_rebalancing_agent import PortfolioRebalancingAgent
from financial_agent.services.chat_history_manager import ChatHistoryManager
from financial_agent.services.data_service import DataService
from financial_agent.services.perplexity_service import PerplexityService


class CategorizationAgent:
    """
    A production-level class for categorizing user queries into predefined categories
    using an LLM with a structured prompt and routing messages to child agents.
    """

    def __init__(self, user_id: str, session_id: str = None, llm_temperature: float = 0.0,
                 chat_history_manager: ChatHistoryManager = None):
        """
        Initializes the CategorizationAgent.

        Args:
            user_id (str): The unique ID of the user.
            session_id (str, optional): A unique session ID. If not provided, a new UUID will be generated.
            llm_temperature (float, optional): The temperature parameter for the LLM. Default is 0.0 for deterministic output.
            chat_history_manager (ChatHistoryManager): A ChatHistoryManager instance to manage chat history.
        """
        self.user_id = user_id
        self.session_id = session_id or str(uuid.uuid4())
        self.categories = [
            "Portfolio Analysis",
            "Portfolio Re-balancing",
            "Goal Planning",
        ]
        self.llm_temperature = llm_temperature
        self.chat_history_manager = chat_history_manager or ChatHistoryManager()
        self.llm_chain, self.categories_str = self._initialize_llm_chain()

        data_service = DataService(self.user_id)
        perplexity_service = PerplexityService()

        # Initialize specialized agents
        self.agents = {
            "Portfolio Analysis": PortfolioAnalysisAgent(user_id, self.session_id, data_service, perplexity_service,
                                                         chat_history_manager=self.chat_history_manager),
            "Portfolio Re-balancing": PortfolioRebalancingAgent(user_id, self.session_id, data_service,
                                                                perplexity_service,
                                                                chat_history_manager=self.chat_history_manager),
            "Goal Planning": GoalPlanningAgent(user_id, self.session_id,
                                               chat_history_manager=self.chat_history_manager),
        }

    def _initialize_llm_chain(self) -> tuple:
        """
        Initializes the LLM chain with a structured prompt.

        Returns:
            tuple: An instance of LLMChain and a string of comma-separated categories.
        """
        prompt_template = """
        You are a financial AI assistant. Your task is to classify the provided text into one of the following categories:
        {categories}

        Text: {input}

        Chat History:
        {history}

        Respond ONLY with valid JSON in the format below:
        {{
          "top_match": "{{category}}",
          "confidence_score": {{confidence_score}}, // A number between 0 and 1
          "not_supported": {{true/false}},
          "context_change": {{true/false}}
        }}

        If none fit, respond with:
        {{
          "top_match": "",
          "confidence_score": 0.0,
          "not_supported": true,
          "context_change": true // or false if the context has changed
        }}

        Ensure the JSON is valid and contains no extra information.
        """
        shared_memory = self.chat_history_manager.get_history(self.user_id, self.session_id)
        prompt = PromptTemplate(template=prompt_template, input_variables=["input", "categories", "history"])
        llm = ChatOpenAI(model='gpt-4o', temperature=self.llm_temperature)
        return LLMChain(llm=llm, prompt=prompt, memory=shared_memory), ", ".join(self.categories)

    @staticmethod
    def extract_and_parse_json(raw_response: str) -> dict:
        """
        Extracts and parses JSON from a string, whether it's a proper JSON string
        or a JSON string wrapped with formatting like ```json ... ```.

        Args:
            raw_response (str): The input string containing JSON.

        Returns:
            dict: Parsed JSON as a Python dictionary.
        """
        try:
            # Check and remove surrounding formatting if present
            if raw_response.startswith('```json'):
                raw_response = raw_response.lstrip('```json').rstrip('```').strip()
            elif raw_response.startswith('```'):
                raw_response = raw_response.split('\n', 1)[1].rsplit('```', 1)[0].strip()

            # Parse JSON
            return json.loads(raw_response)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON string: {raw_response}") from e

    def classify_text(self, text: str) -> Dict[str, Union[str, float, bool]]:
        """
        Classifies the input text into one or more predefined categories.

        Args:
            text (str): The text to classify.

        Returns:
            dict: A dictionary containing the classification results.
        """
        try:
            # Run classification
            # shared_memory = self.chat_history_manager.get_history(self.user_id, self.session_id)
            # shared_memory.chat_memory.add_message(HumanMessage(content=text))
            response = self.llm_chain.run({"input": text, "categories": self.categories_str})
            print("Classification Response", response)
            response = self.extract_and_parse_json(response)

            if response.get("top_match"):
                shared_memory = self.chat_history_manager.get_user_history(self.user_id)
                shared_memory["last_matched"] = response.get("top_match", "")
            else:
                shared_memory = self.chat_history_manager.get_user_history(self.user_id)
                response["top_match"] = shared_memory.get("last_matched", "")
                response["not_supported"] = False

            # Extract classification results
            return {
                "top_match": response.get("top_match", ""),
                "confidence_score": response.get("confidence_score", 0.0),
                "not_supported": response.get("not_supported", True),
                "context_change": response.get("context_change", False)
            }
        except Exception as e:

            shared_memory = self.chat_history_manager.get_user_history(self.user_id)
            if shared_memory.get("last_matched"):
                return {
                    "top_match": shared_memory.get("last_matched", ""),
                    "confidence_score": 0.0,
                    "not_supported": True,
                    "context_change": False
                }
            # Add robust logging or error handling in production
            return {
                "error": str(e),
                "top_match": "",
                "confidence_score": 0.0,
                "not_supported": True,
                "context_change": False
            }

    def route_to_agent(self, text: str) -> Dict[str, Union[str, dict]]:
        """
        Routes the query to the appropriate agent based on classification.

        Args:
            text (str): The user's query.

        Returns:
            dict: The response from the specialized agent.
        """
        # Classify the text
        classification = self.classify_text(text)

        # Handle unsupported queries
        if classification.get("not_supported"):
            return {
                "status": "error",
                "message": "The query does not match any supported category.",
                "classification": classification
            }

        # Route to the appropriate agent
        top_match = classification.get("top_match")
        confidence_score = classification.get("confidence_score")
        if top_match in self.agents:
            agent = self.agents[top_match]
            agent_response = agent.handle_query(text)  # Call the appropriate agent's handle_query method
            return {
                "status": "success",
                "category": top_match,
                "confidence_score": confidence_score,
                "message": agent_response
            }

        # No matching agent found
        return {
            "status": "error",
            "message": f"No agent available for the category: {top_match}",
            "classification": classification
        }

    def get_session_details(self) -> Dict[str, str]:
        """
        Retrieves session-related details for the agent.

        Returns:
            dict: A dictionary containing the user ID and session ID.
        """
        return {
            "user_id": self.user_id,
            "session_id": self.session_id
        }
