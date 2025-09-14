from threading import Lock
from typing import Dict, Union

from langchain.memory import ConversationBufferMemory

from financial_agent.models import ChatHistory


class ChatHistoryManager:
    """
    Manages chat history with support for in-memory and Django ORM (SQLite3) storage.
    """

    _instance = None
    _lock = Lock()  # Ensures thread safety

    def __new__(cls, *args, **kwargs):
        # Ensure thread-safe singleton instantiation
        with cls._lock:
            if not cls._instance:
                cls._instance = super(ChatHistoryManager, cls).__new__(cls)
        return cls._instance

    def __init__(self, use_db: bool = False):
        """
        Initializes the ChatHistoryManager.

        Args:
            use_db (bool): Whether to use a database for chat history. Defaults to False (in-memory).
        """
        if not hasattr(self, "initialized"):  # Prevent re-initialization
            self.use_db = use_db
            self.memory_history = {}  # In-memory storage: {user_id: {session_id: ConversationBufferMemory}}
            self.initialized = True  # Flag to mark the instance as initialized

    # In-memory storage: {user_id: {session_id: ConversationBufferMemory}}

    def add_message(self, user_id: str, session_id: str, role: str, content: str):
        """
        Adds a message to the chat history.

        Args:
            user_id (str): The user ID.
            session_id (str): The session ID.
            role (str): The role of the message sender (e.g., 'user', 'assistant').
            content (str): The message content.
        """
        if self.use_db:
            # Save message to the database
            ChatHistory.objects.create(user_id=user_id, session_id=session_id, role=role, content=content)
        else:
            # Save message to in-memory storage
            if user_id not in self.memory_history:
                self.memory_history[user_id] = {}
            if session_id not in self.memory_history[user_id]:
                self.memory_history[user_id][session_id] = ConversationBufferMemory(
                    memory_key="history", input_key="input", return_messages=True
                )
            raise Exception("User id and session id not coming")

    def get_user_history(self, user_id: str):
        """
        Retrieves the chat history for a user.

        Args:
            user_id (str): The user ID.

        Returns:
            ConversationBufferMemory: The chat history for the user.
        """
        if self.use_db:
            # Retrieve messages from the database
            history = ChatHistory.objects.filter(user_id=user_id).order_by("created_at")
            messages = [{"role": item.role, "content": item.content} for item in history]
            return messages
        else:
            # Retrieve in-memory chat history

            if user_id not in self.memory_history:
                self.memory_history[user_id] = {}
            return self.memory_history[user_id]

    def get_history(self, user_id: str, session_id: str) -> Union[ConversationBufferMemory, Dict[str, str]]:
        """
        Retrieves the chat history for a session.

        Args:
            user_id (str): The user ID.
            session_id (str): The session ID.

        Returns:
            ConversationBufferMemory: The chat history for the session.
        """
        if self.use_db:
            # Retrieve messages from the database
            history = ChatHistory.objects.filter(user_id=user_id, session_id=session_id).order_by("created_at")
            messages = [{"role": item.role, "content": item.content} for item in history]
            return messages
        else:
            # Retrieve in-memory chat history
            b_mem = ConversationBufferMemory(memory_key="history", input_key="input", return_messages=True)
            if user_id not in self.memory_history:
                self.memory_history[user_id] = {}
                self.memory_history[user_id][session_id] = b_mem
            elif session_id not in self.memory_history[user_id]:
                self.memory_history[user_id].clear()
                self.memory_history[user_id][session_id] = b_mem
            return self.memory_history[user_id][session_id]

    def clear_history(self, user_id: str):
        """
        Clears all chat history for a given user.

        Args:
            user_id (str): The user ID.
        """
        if self.use_db:
            # Delete all messages for the user
            ChatHistory.objects.filter(user_id=user_id).delete()
        else:
            # Clear in-memory chat history for the user
            if user_id in self.memory_history:
                self.memory_history[user_id] = {}

    def clear_session_history(self, user_id: str, session_id: str):
        """
        Clears the chat history for a specific session.

        Args:
            user_id (str): The user ID.
            session_id (str): The session ID.
        """
        if self.use_db:
            # Delete messages for the specific session
            ChatHistory.objects.filter(user_id=user_id, session_id=session_id).delete()
        else:
            # Clear in-memory chat history for the session
            if user_id in self.memory_history and session_id in self.memory_history[user_id]:
                del self.memory_history[user_id][session_id]

    def start_new_session(self, user_id: str, session_id: str):
        """
        Clears previous session history for the user and starts a new session.

        Args:
            user_id (str): The user ID.
            session_id (str): The new session ID.
        """
        # Clear all history for the user before starting a new session
        self.clear_history(user_id)

        # Initialize new session in in-memory storage if using memory
        if not self.use_db:
            if user_id not in self.memory_history:
                self.memory_history[user_id] = {}
            self.memory_history[user_id][session_id] = ConversationBufferMemory(
                memory_key="history", input_key="input", return_messages=True
            )
