import asyncio
import random
import re
import os
import time
from typing import List, Any
from PIL import Image
from google import genai
from google.genai import types
from google.adk.tools.tool_context import ToolContext
from google.adk.tools import AgentTool
from .sub_agents import prompt_generator
import logging

logger = logging.getLogger(__name__)

client = genai.Client(
    api_key=os.environ["GOOGLE_API_KEY"],
    http_options=types.HttpOptions(timeout=60000)
)

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
    logger.info(f"Generating prompts for theme: {theme}")
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
            # Strip markdown code blocks (e.g., ```python ... ```)
            clean_output = re.sub(r"^```[a-zA-Z]*\s*", "", raw_output.strip())
            clean_output = re.sub(r"\s*```$", "", clean_output)
            
            # Try to parse Python-list-like text:
            parsed = ast.literal_eval(clean_output)
            if isinstance(parsed, list):
                prompts = [str(p) for p in parsed]
            else:
                prompts = [raw_output]
        except Exception as e:
            # Fallback: single big string
            logger.warning(f"Failed to parse prompt output as list: {e}. Using raw output.")
            prompts = [raw_output]
    else:
        # Very defensive fallback:
        prompts = [str(raw_output)]

    # 4. Store in persistent user state
    tool_context.state["user:prompts"] = prompts  # "user:" prefix = per-user persistence

    # 5. Also return them to the caller
    return prompts
async def generate_calendar(
    aspect_ratio: str,
    resolution: str,
    tool_context: ToolContext,
) -> str:
    """
    Generates a calendar and delivers it to the user.

    Args:
        aspect_ratio (str): The aspect ratio of the calendar images (e.g., "9:16").
        resolution (str): The resolution of the calendar images (e.g., "1K").
        tool_context (ToolContext): The tool context to access state.

    Returns:
        str: A message indicating the result of the generation.
    """
    prompts = tool_context.state.get("user:prompts", [])
    
    if not prompts or len(prompts) != 12:
        logger.error(f"Invalid number of prompts found: {len(prompts) if prompts else 0}")
        return "Error: Could not find exactly 12 prompts in user state. Please generate prompts first."

    logger.info(f"Starting calendar generation with {len(prompts)} prompts")

    # Generate output folder name with random 3-digit number
    output_folder = f"output_{random.randint(100, 999)}"
    # Create the output folder if it doesn't exist
    os.makedirs(output_folder, exist_ok=True)

    # Save prompts to a file in the output folder
    with open(f"{output_folder}/prompts.txt", "w") as f:
        for prompt in prompts:
            f.write(prompt + "\n")

    # Map aspect ratio to template folder name
    # Assuming aspect_ratio format like "9:16" maps to "9_16"
    template_folder_name = aspect_ratio.replace(":", "_")
    template_base_path = f"daedalus/templates/{template_folder_name}"

    tasks = []
    for i, prompt in enumerate(prompts, start=1):
        template_path = f"{template_base_path}/{i}-2026.png"
        output_path = f"{output_folder}/{i}-2026.png"
        
        try:
            template_image = Image.open(template_path)
        except FileNotFoundError:
             logger.error(f"Template file not found: {template_path}")
             return f"Error: Template file not found at {template_path}. Please check aspect ratio and template files."

        prompt_contents = [prompt, template_image]
        
        # Create async task
        task = asyncio.create_task(
            generate_images_gemini_3_pro(
                prompt_contents=prompt_contents,
                aspect_ratio=aspect_ratio,
                resolution=resolution,
                output_path=output_path
            )
        )
        tasks.append(task)

    # Wait for all tasks to complete
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    # Check for exceptions in results
    failures = []
    for i, result in enumerate(results, start=1):
        if isinstance(result, Exception):
            failures.append(f"Image {i}: {str(result)}")
    
    if failures:
        logger.error(f"Calendar generation completed with errors: {failures}")
        return f"Calendar generation completed with some errors:\n" + "\n".join(failures) + f"\nOutput folder: {output_folder}"

    logger.info(f"Calendar generation completed successfully in {output_folder}")
    return f"Calendar generated successfully in folder: {output_folder}"


async def generate_images_gemini_3_pro(prompt_contents: list[str], aspect_ratio: str, resolution: str, output_path: str):
    """
    Generates images using the Gemini 3 Pro model.

    Args:
        prompt_contents: A list of strings representing the prompt for image generation.
        aspect_ratio: The desired aspect ratio of the generated image (e.g., "16:9").
        resolution: The desired resolution of the generated image (e.g., "1K").
        output_path: The file path where the generated image should be saved.
    """

    # Retry logic with exponential backoff
    max_retries = 3
    retry_delay = 1  # Initial delay in seconds
    
    success = False
    for attempt in range(max_retries):
        try:
            response = await client.aio.models.generate_content(
                model="gemini-3-pro-image-preview",
                contents=prompt_contents,
                config=types.GenerateContentConfig(
                    response_modalities=['IMAGE'],
                    image_config=types.ImageConfig(
                        aspect_ratio=aspect_ratio,
                        image_size=resolution
                    ),
                )
            )
            success = True
            break  # Success, exit retry loop
        except Exception as e:
            if attempt < max_retries - 1:
                print(f"API call failed (attempt {attempt + 1}/{max_retries}): {e}")
                logger.warning(f"API call failed (attempt {attempt + 1}/{max_retries}): {e}")
                print(f"Retrying in {retry_delay} seconds...")
                await asyncio.sleep(retry_delay)
                retry_delay *= 2  # Exponential backoff
            else:
                print(f"API call failed after {max_retries} attempts: {e}")
                logger.error(f"API call failed after {max_retries} attempts: {e}")

    if success:
        for part in response.parts:
            if part.text is not None:
                print(part.text)
            elif image:= part.as_image():
                # Ensure directory exists
                os.makedirs(os.path.dirname(output_path), exist_ok=True)
                image.save(output_path)