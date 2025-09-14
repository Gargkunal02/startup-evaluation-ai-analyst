from django.http import JsonResponse
from rest_framework.decorators import api_view

from financial_agent.agents.categorization_agent import CategorizationAgent
from financial_agent.decorator import user_login_required
from financial_agent.services.chat_history_manager import ChatHistoryManager
from financial_agent.services.response_service import ResponseService
from financial_agent.utils import parse_user_details


@user_login_required
@api_view(['GET', 'POST'])
def chat_bot(request):
    """
    Handles chat requests by classifying the user's query and routing it to the appropriate agent.

    Expected JSON Input:
    {
        "user_id": "user_123",
        "session_id": "session_456",
        "query": "How can I rebalance my portfolio?"
    }

    Returns:
        JSON Response with the agent's response.
    """

    if request.method == "GET":
        user_details = parse_user_details(request.user_config)
        data = ResponseService(user_details).base_page()
        return JsonResponse(
            data=data,
            status=200
        )

    try:
        # Parse the input JSON

        data = request.data
        if not data:
            return JsonResponse(
                {"status": "error", "message": "Invalid JSON data."},
                status=400
            )
        print(f"chat_bot: {data}")
        user_details = parse_user_details(request.user_config)
        user_id = user_details.user_id
        session_id = data.get('session_id')
        query = data.get('query')

        # Validate input
        if not user_id or not session_id or not query:
            return JsonResponse(
                {"status": "error", "message": "user_id, session_id, and query are required."},
                status=400
            )

        # Initialize ChatHistoryManager and CategorizationAgent
        chat_history_manager = ChatHistoryManager(use_db=False)  # Set to True to use the database
        categorization_agent = CategorizationAgent(
            user_id=str(user_id),
            session_id=session_id,
            chat_history_manager=chat_history_manager
        )

        # Route the query through the categorization agent
        response = categorization_agent.route_to_agent(query)

        response_message = response.get('message')

        data = ResponseService(user_details=parse_user_details(request.user_config)).query_response(response_message)

        # Return the response to the client
        return JsonResponse(data, status=200)

    except Exception as e:
        # Handle unexpected errors
        return JsonResponse({"status": "error", "message": str(e)}, status=500)
