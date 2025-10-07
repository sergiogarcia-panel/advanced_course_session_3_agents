from pydantic import BaseModel
from agents import (
    Agent,
    GuardrailFunctionOutput,
    RunContextWrapper,
    Runner,
    output_guardrail
)
from models import MessageOutput

class OutputGuardrailOutput(BaseModel):
    currency_is_usd_or_btc: bool
    reasoning: str


guardrail_agent = Agent(
    name="Output Guardrail Agent",
    instructions=(
        "Determine if all the monetary values are in USD or BTC. "
        "Set currency_is_usd_or_btc to true only if all monetary values are in USD or BTC. "
        "Provide a concise reasoning."
    ),
    output_type=OutputGuardrailOutput,
)


@output_guardrail
async def currency_guardrail(
    ctx: RunContextWrapper, agent: Agent, output: MessageOutput
) -> GuardrailFunctionOutput:
    """Output guardrail ensuring all detected monetary values are denominated in USD or BTC.

    Tripwire triggers when NOT all monetary values are USD or BTC (currency_is_usd_or_btc == False).
    """
    # Run the specialized guardrail agent on the model's raw response text
    result = await Runner.run(guardrail_agent, output.response, context=ctx.context)
    final_output = result.final_output_as(OutputGuardrailOutput)

    return GuardrailFunctionOutput(
        output_info=final_output,
        tripwire_triggered=not final_output.currency_is_usd_or_btc,
    )