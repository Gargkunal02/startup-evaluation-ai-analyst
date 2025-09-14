from datetime import datetime
from typing import Dict

from langchain.chains.llm import LLMChain

from financial_agent.services.chat_history_manager import ChatHistoryManager
from langchain.memory import ConversationBufferMemory
from langchain.prompts import PromptTemplate
from langchain.chat_models import ChatOpenAI
from langchain.chains import ConversationChain
from langchain.schema import SystemMessage

prompt_template = """"
You are a Goal Planner chatbot for Indian users.

### Key Rules:
1. **Never give a plan or advice** without gathering the mandatory details.
2. Your first priority is to ask for the following details (if not already provided):
   - Ask how frequently do plan to go for domestic vacation and Internal vacations
   - Monthly salary and expenses.
   - Average budget or Cost of every domestic trip and international trip
   - Consider Expected annual salary increment as 10%.
   - Consider Expected annual expense increment as 6%.
   - Consider increasing SIP investments yearly by 5%.
   - If assumptions are already taken, do not confirm them with the user.
   - Consider today's date as {current_date}.
   - If the goal is not getting achieved, increase SIP investments yearly by 10%.
3. User is planning to do SIP investment to achieve this goal
4. **If any detail is missing**, politely ask for it in a conversational tone. Do not proceed with a plan until all details are collected.
5. Only after gathering all mandatory details:
   - Provide a concise and actionable goal plan.
   - Include assumptions based on the Indian market (10-year trends).
   - Clearly state whether the goal is achievable or not.
   - Present a table mentioning monthly SIP value for each year.
   - Mention the basic assumptions considered and offer the user the option to change them.
   - Ensure numbers and values are in whole numbers.
   - Conclude with whether the user will be able to achieve their goal.
   - Mention exact total savings or investments that will be accumulated based on the investment and its return.
6. Do not ask confirmation on assumption consider just proceed
### Important:
- Avoid generic advice or responses like "schedule viewings" or "negotiate with sellers."
- Stick strictly to the user's financial and goal-planning requirements.
- Respond concisely, ensuring clarity.


Answer User Query: "{user_query}"
"""


class TravelGoalAgent:
    def __init__(self, user_id: str, session_id: str, llm_temperature: float, chat_history_manager: ChatHistoryManager = None):
        self.user_id = user_id
        self.session_id = session_id
        self.llm_temperature = llm_temperature
        self.shared_memory = chat_history_manager.get_history(user_id=self.user_id, session_id=self.session_id)
        self.conversation_model = self._initialize_agent()

    def _initialize_agent(self):
        llm = ChatOpenAI(model='gpt-4o', temperature=self.llm_temperature)
        return ConversationChain(llm=llm, memory=self.shared_memory)

    def handle_query(self, query: str) -> Dict[str, str]:
        """
        Handles goals with loan related queries.

        Args:
            query (str): The user's query.

        Returns:
            dict: The response for the query.
        """
        userQueryPrompt = PromptTemplate(input_variables=["current_date", "user_query"], template=prompt_template)
        prompt_details = {
            "current_date": datetime.now().date(),
            "user_query": query
        }
        response = self.conversation_model.run(input=userQueryPrompt.format(**prompt_details))
        return response
