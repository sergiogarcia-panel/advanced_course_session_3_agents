import asyncio
from dotenv import load_dotenv

load_dotenv()

from agents import Agent, Runner, SQLiteSession, ModelSettings, RunContextWrapper
from agents.mcp import MCPServerStreamableHttp
from openai.types.shared import Reasoning

from tools.get_crypto_price import get_crypto_price
from models import UserInfo, CryptoPrice
from guardrails.input_guardrail import bitcoin_guardrail
from guardrails.output_guardrail import currency_guardrail


# session = SQLiteSession("conversation_123")

# agent = Agent(
#     name="my_agent",
# )


# result = Runner.run_sync(agent, "Write a haiku about recursion in programming.", session=session)
# print(result.final_output)
# print('='*20)

# result = Runner.run_sync(agent, "Can you repeat your last answer?", session=session)
# print(result.final_output)
# print('='*20)

###########################################################################################################

# session = SQLiteSession("conversation_456")

# agent = Agent(
#     name="my_agent",
#     instructions="Before you answer any question, ask the user for his name.",
#     model='gpt-5',
#     model_settings = ModelSettings(reasoning=Reasoning(effort="minimal"), verbosity="low")
# )

# result = Runner.run_sync(agent, "I want know what bitcoin is", session=session)
# print(result.final_output)
# print('='*20)

# result = Runner.run_sync(agent, "My name is Sergio", session=session)
# print(result.final_output)
# print('='*20)

###########################################################################################################

# session = SQLiteSession("crypto_session")

# def dynamic_instructions(ctx: RunContextWrapper[UserInfo], agent: Agent[UserInfo]) -> str:
#     return f"The user is {ctx.context.name}. Say hello to {ctx.context.name} before answering any question."

# crypto_agent = Agent[UserInfo](
#     name='crypto_agent',
#     instructions=dynamic_instructions,
#     # output_type=CryptoPrice,
#     tools=[get_crypto_price],
#     input_guardrails=[bitcoin_guardrail],
#     output_guardrails=[currency_guardrail]
# )

# result = Runner.run_sync(
#     crypto_agent,
#     "What is the current price of Bitcoin in USD?",
#     session=session,
#     context=UserInfo(name="Sergio", allowed=True)
# )
# print(result.final_output)
# print('='*20)

###########################################################################################################

# async def main():
#     async with MCPServerStreamableHttp(
#         name="Math Server",
#         params={
#             "url": "http://localhost:8000/mcp",
#             "timeout": 10,
#         },
#         cache_tools_list=True,
#         max_retry_attempts=3
#     ) as server:
#         session = SQLiteSession("mcp_session")

#         def dynamic_instructions(ctx: RunContextWrapper[UserInfo], agent: Agent[UserInfo]) -> str:
#             return f"The user is {ctx.context.name}. Say hello to {ctx.context.name} before answering any question."

#         mcp_agent = Agent[UserInfo](
#             name='mcp_agent',
#             instructions=dynamic_instructions,
#             tools=[get_crypto_price],
#             mcp_servers=[server],
#             model_settings=ModelSettings(tool_choice="required")
#         )

#         result = await Runner.run(
#             mcp_agent,
#             "Multiply 125 * 22",
#             session=session,
#             context=UserInfo(name="Sergio", allowed=True)
#         )
#         print(result.final_output)
#         print('='*20)

# asyncio.run(main())


###########################################################################################################


# Create a multi-agent system

async def main() -> None:
    async with MCPServerStreamableHttp(
        name="Streamable HTTP Python Server",
        params={
            "url": "http://localhost:8000/mcp",
            "timeout": 10,
        },
        cache_tools_list=True,
        max_retry_attempts=3,
    ) as server:
        session = SQLiteSession("multi_agent_system")

        crypto_specialist = Agent[UserInfo](
            name="Crypto Specialist",
            handoff_description="Handles crypto-related questions.",
            instructions="You are a crypto specialist. Use the MCP tools to answer crypto-related questions.",
            tools=[get_crypto_price],
            model_settings=ModelSettings(tool_choice="required")
        )

        math_specialist = Agent(
            name="Math Specialist",
            handoff_description="Handles math-related questions.",
            instructions="You are a math specialist. Use the MCP tools to answer math-related questions.",
            mcp_servers=[server],
            model_settings=ModelSettings(tool_choice="required")
        )

        master = Agent[UserInfo](
            name="Master Agent",
            instructions=(
                "You are the master agent. You have two specialist agents to help you: "
                "1) Crypto Specialist, who is an expert in cryptocurrency and can use crypto-related tools. "
                "2) Math Specialist, who is an expert in mathematics and can use math-related tools. "
                "For each question, decide which specialist agent is best suited to answer it, and delegate the question to that agent. "
                "If the question is complex, split it into multiple steps and delegate each step to the appropriate specialist agent. "
                "If the question is not related to crypto or math, answer it yourself."
            ),
            handoffs=[crypto_specialist, math_specialist],
            input_guardrails=[bitcoin_guardrail]
        )

        result = await Runner.run(
            master,
            "How many bitcoins are 100 dollars currently worth?",
            session=session,
            context=UserInfo(name="Sergio", allowed=True),
        )
        print(result.final_output)
        print('=' * 20)

asyncio.run(main())