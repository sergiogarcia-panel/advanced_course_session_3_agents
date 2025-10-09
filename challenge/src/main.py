import asyncio
from dotenv import load_dotenv
from agents import Agent, Runner, SQLiteSession, ModelSettings
from agents.mcp import MCPServerStreamableHttp

from tools.semantic_search import semantic_search
from guardrails.input_guardrail import music_guardrail

load_dotenv()

questions = {
    "history": "When was America discovered?",
    "math": "Give me the definition of prime numbers",
    "art": "Which is the most famous painting of Francisco Goya",
    "science": "What planets are in our solar system?",
    "literature": "Which is the most famous novel of Miguel de Cervantes?",
    "music": "What is the most popular song of The Beatles?"
}


async def main():
    async with MCPServerStreamableHttp(
        name="Streamable HTTP Python Server",
        params={
            "url": "http://localhost:8080/mcp",
            "timeout": 10,
        },
        cache_tools_list=True,
        max_retry_attempts=3,
    ) as server:
        session = SQLiteSession("session_123")

        domains = ["history", "math", "art", "science", "literature"]
        specialists = {}
        for domain in domains:
            specialists[domain] = Agent(
                name=f"{domain.capitalize()} Tutor",
                handoff_description=f"Specialist agent for {domain} questions",
                model_settings=ModelSettings(tool_choice="required"),
                instructions=f"""
                You are a {domain} Tutor specialist. Before answering any {domain} question, you MUST first search the {domain} knowledge base using the semantic_search tool to find relevant information.

                Your process should be:
                1. Use semantic_search to find relevant {domain} documents for the user's query
                2. If you find relevant information, use it to provide a comprehensive answer
                3. Provide clear explanations with step-by-step reasoning and examples
                4. Always cite the source documents you used in your response

                Never provide your own knowledge. Only use information retrieved from the semantic_search tool. EVEN IF IT IS INCORRECT or incomplete.
                """,
                # tools=[semantic_search],
                mcp_servers=[server]
            )

        triage_agent = Agent(
            name="Triage Agent",
            instructions="""
            You determine which agent to use based on the user's homework question.
            ALWAYS DELEGATE TO A SPECIALIST, DO NOT ANSWER YOURSELF.
            Never include your own knowledge, only the information retrieved from the specialists, EVEN IF IT IS INCORRECT or incomplete.
            """,
            handoffs=list(specialists.values()),
            input_guardrails=[music_guardrail],
        )

        for category, question in questions.items():
            print(f"Testing {category} question...")
            result = await Runner.run(triage_agent, question, session=session)
            print(result.final_output)
            print("\n" + "="*50 + "\n")

if __name__ == "__main__":
    asyncio.run(main())
