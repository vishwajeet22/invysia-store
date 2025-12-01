from typing import List, Any
from google.adk.tools.tool_context import ToolContext
from google.adk.tools import AgentTool
from daedalus.src.sub_agents import prompt_generator

def get_payment_link() -> dict:
    """
    Generates a payment link for the user to complete their purchase.
    
    Returns:
        dict: A mock payment link URL.
    """
    return {"status": "success", "payment_link": "https://invysia.store/payment/mock-link-12345"}


async def generate_prompts(
    theme: str,
    tool_context: ToolContext,
) -> List[str]:
    """
    Generates prompts for the user to complete their purchase.

    Args:
        theme (str): The theme for the prompts.
    
    Returns:
        List[str]: A list of prompts.
    """

    # 1. Wrap the agent as a tool
    agent_tool = AgentTool(agent=prompt_generator)

    # 2. Call the agent as a tool
    raw_output: Any = await agent_tool.run_async(
        args={"request": theme},
        tool_context=tool_context,
    )

    # 3. Normalize the output into a Python list of strings
    import ast
    prompts: List[str]

    if isinstance(raw_output, list):
        prompts = [str(p) for p in raw_output]
    elif isinstance(raw_output, str):
        try:
            # Try to parse Python-list-like text:
            parsed = ast.literal_eval(raw_output)
            if isinstance(parsed, list):
                prompts = [str(p) for p in parsed]
            else:
                prompts = [raw_output]
        except Exception:
            # Fallback: single big string
            prompts = [raw_output]
    else:
        # Very defensive fallback:
        prompts = [str(raw_output)]

    # 4. Store in persistent user state
    tool_context.state["user:prompts"] = prompts  # "user:" prefix = per-user persistence

    # 5. Also return them to the caller
    return prompts


async def generate_calendar():
    """
    Generates a calendar and delivers it to the user.
    """
    pass