from pydantic import BaseModel
from agents import (
    Agent,
    GuardrailFunctionOutput,
    RunContextWrapper,
    Runner,
    input_guardrail,
)


class InputGuardrailOutput(BaseModel):
    is_about_music: bool
    reasoning: str


guardrail_agent = Agent(
    name="Input Guardrail Agent",
    instructions=(
        "Determine if the user input is about music. "
        "Set is_about_music to true only if the main intent concerns music. "
        "Provide a concise reasoning."
    ),
    output_type=InputGuardrailOutput,
)


@input_guardrail
async def music_guardrail(
    ctx: RunContextWrapper, agent: Agent, user_input: str
) -> GuardrailFunctionOutput:
    """Input guardrail that blocks queries not related to music.

    Returns a GuardrailFunctionOutput whose tripwire is triggered when the
    input is about music.
    """
    result = await Runner.run(guardrail_agent, user_input, context=ctx.context)
    final_output = result.final_output_as(InputGuardrailOutput)
    return GuardrailFunctionOutput(
        output_info=final_output,
        tripwire_triggered=final_output.is_about_music,
    )