import requests
import uuid
from datetime import datetime
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel

console = Console()


class FinancialAdvisorCLI:
    """
    CLI client for interacting with the Django financial advisor server.
    """

    def __init__(self):
        self.session_id = str(uuid.uuid4())  # Unique session ID for this CLI session
        self.server_url = "http://127.0.0.1:8000/agent/chat/"  # Django server endpoint

    def display_welcome_message(self):
        """
        Display a welcome message and instructions for the CLI.
        """
        console.print(Panel(
            """Welcome to Your Financial Advisor CLI!
            You can ask questions about:
            - Portfolio performance (e.g., "How is my portfolio performing?")
            - Fund analysis (e.g., "Why is Fund X underperforming?")
            - Investment recommendations (e.g., "What should I invest in?")
            - Rebalancing suggestions (e.g., "Should I rebalance my portfolio?")
            - Tax implications (e.g., "What are the tax implications of selling Fund X?")

            Type 'exit' or 'quit' to end the conversation.
            """,
            title="Financial Advisor CLI",
            border_style="blue"
        ))

    def send_query(self, query: str):
        """
        Send a query to the Django server and display the response.
        """
        try:
            # Record the start time for processing
            start_time = datetime.now()

            # Make a POST request to the Django server
            response = requests.post(self.server_url, json={
                "query": query,
                "session_id": self.session_id
            })

            # Check for errors
            if response.status_code != 200:
                console.print(f"[red]Error: {response.json().get('message')}[/red]")
                return

            # Parse the JSON response
            data = response.json()

            # Display the assistant's response
            console.print("\n[bold green]Assistant:[/bold green]")
            console.print(Markdown(data.get("response", {}).get("response", "Sorry, no response available.")))

            # Display processing time
            processing_time = (datetime.now() - start_time).total_seconds()
            console.print(f"\n[dim]Processing time: {processing_time:.2f}s[/dim]")

        except Exception as e:
            console.print(f"[red]Error: {str(e)}[/red]")

    def chat_loop(self):
        """
        Start the interactive CLI chat loop.
        """
        while True:
            try:
                # Get user input
                query = input("\nYou: ")

                # Exit condition
                if query.lower() in ['exit', 'quit']:
                    console.print("\n[yellow]Goodbye![/yellow]")
                    break

                # Send the query to the server
                self.send_query(query)

            except KeyboardInterrupt:
                console.print("\n[yellow]Exiting...[/yellow]")
                break
            except Exception as e:
                console.print(f"[red]Error: {str(e)}[/red]")


if __name__ == "__main__":
    cli = FinancialAdvisorCLI()
    cli.display_welcome_message()
    cli.chat_loop()