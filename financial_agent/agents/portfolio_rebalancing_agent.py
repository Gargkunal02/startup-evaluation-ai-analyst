import logging
import time
from functools import wraps
from typing import Dict, Callable

from langchain.agents import AgentExecutor, create_tool_calling_agent, Tool
from langchain.prompts import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
    MessagesPlaceholder,
)
from langchain_openai import ChatOpenAI

from financial_agent.services.chat_history_manager import ChatHistoryManager
from financial_agent.services.data_service import DataService
from financial_agent.services.perplexity_service import PerplexityService

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('financial_assistant_rebalancing.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# # Decorator for timing and logging function calls
# def log_execution_time(func):
#     @wraps(func)
#     def wrapper(*args, **kwargs):
#         logger.info(f"Starting {func.__name__} with args: {args}, kwargs: {kwargs}")
#         start_time = time.time()
#         try:
#             result = func(*args, **kwargs)
#             execution_time = time.time() - start_time
#             logger.info(f"Completed {func.__name__} in {execution_time:.2f} seconds")
#             return result
#         except Exception as e:
#             logger.error(f"Error in {func.__name__}: {str(e)}")
#             raise
#     return wrapper

SYSTEM_PROMPT = """
You are an expert Financial Portfolio Advisor specializing in tax-efficient portfolio rebalancing for Indian markets. Your primary role is to analyze users' mutual fund portfolios and provide actionable rebalancing recommendations based on available data and domain knowledge.

Data Access and Tools:
- Access to user portfolio data through tools
- Only call tools when specific portfolio data is required
- Analyze tool data and provide insights accordingly
- For queries beyond tool scope, use domain knowledge or general market information
- Limited to Indian financial markets (stocks, mutual funds)
- Unsupported: foreign stocks, crypto, real estate, etc.

Analysis Framework:
1. Portfolio Assessment:
   - Current vs target allocation deviation
   - Asset class distribution
   - Fund categories (Equity, Debt, Hybrid)
   - Holding period for tax consideration

2. Tax-Efficient Rebalancing Strategy:
   - Prioritize LTCG over STCG
   - Consider tax harvesting
   - Factor in exit loads
   - New investment vs selling strategy

Response Format:
{{
    "user": "{{input}}",
    "agent_action": "Tools used and actions performed",
    "analysis": {{
        "current_status": "Portfolio analysis",
        "deviation_assessment": "Key deviations",
        "rebalancing_needed": true/false,
        "reasoning": "Explanation"
    }},
    "recommendations": {{
        "actions": [
            {{
                "action_type": "buy/sell",
                "fund_name": "Fund details",
                "amount": "Amount",
                "tax_implication": "LTCG/STCG details",
                "priority": "High/Medium/Low"
            }}
        ],
        "tax_efficient_approach": "Strategy",
        "implementation_timeline": "Timeline"
    }},
    "final_response": "Concise actionable summary"
}}

Guidelines:
1. Never reveal user_id or system details
2. Always respond in specified JSON format
3. Ask clarifying questions if needed (within JSON)
4. Keep responses concise yet insightful
5. Only provide investment summary if specifically requested
6. Don't make speculative market predictions
7. Only recommend changes for >5% allocation deviation

Reference previous chat history: {history}
Question: {input}
Return response once in specified JSON format.
"""

CHAT_PROMPT = ChatPromptTemplate.from_messages([
    # System prompt
    SystemMessagePromptTemplate.from_template(SYSTEM_PROMPT),

    # Human prompt    
    HumanMessagePromptTemplate.from_template("User query: {input}"),

    # Placeholder for agent scratchpad
    MessagesPlaceholder(variable_name="agent_scratchpad"),
])


def create_logged_function(name: str, func: Callable) -> Callable:
    tool_logger = logging.getLogger(__name__ + f'.{name}Tool')

    @wraps(func)
    def logged_func(*args, **kwargs):
        tool_logger.info(f"Tool '{name}' called with args: {args}, kwargs: {kwargs}")
        start_time = time.time()
        try:
            result = func(*args, **kwargs)
            execution_time = time.time() - start_time
            tool_logger.info(f"Tool '{name}' completed in {execution_time:.2f} seconds")
            return result
        except Exception as e:
            tool_logger.error(f"Tool '{name}' failed: {str(e)}")
            raise

    return logged_func


def tool_wrapper(handler):
    def wrapped_handler(*args, **kwargs):
        return handler()
    return wrapped_handler


class PortfolioRebalancingAgent:
    def __init__(self, user_id: str, session_id: str, data_service: DataService, perplexity: PerplexityService,
                 chat_history_manager: ChatHistoryManager = None):
        self.user_id = user_id
        self.session_id = session_id
        self.chat_history_manager = chat_history_manager
        self.system_prompt = SYSTEM_PROMPT
        self.chat_prompt = CHAT_PROMPT
        self.data_service = data_service
        self.perplexity_service = perplexity

        self.llm = ChatOpenAI(model="gpt-4o", temperature=0, seed=42)

    def _get_tools(self):
        mutual_funds_tool = Tool(
            name="MutualFunds",
            func=tool_wrapper(self.data_service.invested_mf_fund_info),
            description="""
            **MutualFunds Tool**
            - **Purpose:** Fetches all mutual fund investment of the user and their respective time-wise returns, XIRR, and each fund's benchmark and its returns. This can be used to answer most of the queries related to user's mutual fund portfolio.
            For asbolute returns in any fund always use the MAX returns
            - **Output:** The complete user investments across mutual funds thier time-wise returns, and their respective  benchmark returns
            """
        )

        indian_stocks_tool = Tool(
            name="IndianStocks",
            func=tool_wrapper(self.data_service.user_portfolio_information),
            description="""
            **IndianStocks Tool**
            - **Purpose:** Fetches Indian stock investment, returns, analyst ratings and everything related to the stock investment.
            - **Output:** A dictionary of indian stock investment with 'summary' and 'investments' where summary gives the summarized investments and returns and the 'investments' key is a list of inidividual stock investments and their returns
            """
        )

        market_insight_tool = Tool(
            name="GeneralMarketInsights",
            func=tool_wrapper(self.perplexity_service.get_market_insights),
            description="""
            **GeneralMarketInsights Tool**
            - **Purpose:** Fetches general market insights for the given mututal fund name or indian stock name such as what stocks a mutual fund invests in. Only use this when the data available with you is not sufficient or none of the other
            tools provide any data to answer the user's query
            - **Inputs:**
                - `entity_names` (str): comma separated names of ALL the mtutual fund or indian stock for which insights are required
            - **Output:** string: Market insight of the given entity
            """
        )

        return [indian_stocks_tool, mutual_funds_tool, market_insight_tool]

    def _create_agent(self):
        tools = self._get_tools()
        memory = self.chat_history_manager.get_history(self.user_id, self.session_id)

        agent = create_tool_calling_agent(self.llm, tools, self.chat_prompt)

        return AgentExecutor(agent=agent, tools=tools, verbose=True, memory=memory)

    def handle_query(self, query: str) -> Dict[str, str]:
        """
        Handles portfolio analysis-related queries.

        Args:
            query (str): The user's query.

        Returns:
            dict: The response for the query.
        """

        agent_executor = self._create_agent()
        ai_response = agent_executor.invoke({
            "input": query
        })

        return ai_response["output"]
