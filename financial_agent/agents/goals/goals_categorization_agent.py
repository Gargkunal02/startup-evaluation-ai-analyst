import json
import uuid
from typing import Union, Dict, List

from langchain.chains import LLMChain
from langchain_core.prompts import PromptTemplate

from langchain_openai import OpenAI

from financial_agent.agents.goals.education_goal_agent import EducationGoalAgent
from financial_agent.agents.goals.goal_with_loan_agent import GoalWithLoanAgent
from financial_agent.agents.goals.travel_goal_agent import TravelGoalAgent
from financial_agent.services.chat_history_manager import ChatHistoryManager


class GoalCategorizationAgent:
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
        self.goal_types = [
            "Home",
            "Car",
            "Education",
            "Travel",
            "Retirement",
            "Emergency Fund"
        ]
        self.llm_temperature = llm_temperature
        self.chat_history_manager = chat_history_manager
        self.llm_chain, self.categories_str = self._initialize_llm_chain()

        self.agents = {
            "goal_with_loans": GoalWithLoanAgent(user_id, self.session_id, self.llm_temperature, chat_history_manager),
            "education_goal": EducationGoalAgent(user_id, self.session_id, self.llm_temperature,
                                                 chat_history_manager),
            "travel_goal": TravelGoalAgent(user_id, self.session_id, self.llm_temperature,
                                           chat_history_manager)
        }

    def _initialize_llm_chain(self) -> tuple:
        """
        Initializes the LLM chain with a structured prompt.

        Returns:
            tuple: An instance of LLMChain and a string of comma-separated categories.
        """
        prompt_template = """You are an intelligent system designed to route user queries to the appropriate 
        goal-planning agent. Your primary task is to accurately classify the provided text into one of the 
        following predefined categories: 
        
        {categories}
        
        Text: {input}
        
        Chat History:
        {history}
        
        When classifying the current input, take into account any relevant previous chat history. Assign a higher 
        weight to the chat history if it provides useful context that strongly suggests a particular category. 
        However, ensure that recent inputs have priority if they contradict past mentions. 
        
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
        llm = OpenAI(temperature=self.llm_temperature)
        return LLMChain(llm=llm, prompt=prompt, memory=shared_memory), ", ".join(self.goal_types)

    def classify_text(self, text: str) -> Dict[str, Union[List[Dict[str, Union[str, float]]], bool]]:
        """
        Classifies the input text into one or more predefined categories.

        Args:
            text (str): The text to classify.

        Returns:
            dict: A dictionary containing the classification results.
        """
        try:
            response = self.llm_chain.run({"input": text, "categories": self.categories_str})
            response = json.loads(response)

            # Extract classification results
            return {
                "top_match": response.get("top_match", ""),
                "confidence_score": response.get("confidence_score", 0.0),
                "not_supported": response.get("not_supported", True),
                "context_change": response.get("context_change", False)
            }
        except Exception as e:
            # Add robust logging or error handling in production
            return {"error": str(e), "top_matches": [], "not_supported": True, "context_change": False}

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
