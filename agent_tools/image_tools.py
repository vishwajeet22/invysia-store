import asyncio
import os
from google import genai
from google.genai import types
import time

async def generate_images_gemini_3_pro(prompt_contents: list[str], aspect_ratio: str, resolution: str, output_path: str):
    """
    Generates images using the Gemini 3 Pro model.

    Args:
        prompt_contents: A list of strings representing the prompt for image generation.
        aspect_ratio: The desired aspect ratio of the generated image (e.g., "16:9").
        resolution: The desired resolution of the generated image (e.g., "1K").
        output_path: The file path where the generated image should be saved.
    """
    print(f"Calling API for prompt {prompt_contents[0]}")

    client = genai.Client(
        api_key=os.environ["GOOGLE_API_KEY"],
        http_options=types.HttpOptions(timeout=60000)
    )

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
                print(f"Retrying in {retry_delay} seconds...")
                await asyncio.sleep(retry_delay)
                retry_delay *= 2  # Exponential backoff
            else:
                print(f"API call failed after {max_retries} attempts: {e}")

    if success:
        for part in response.parts:
            if part.text is not None:
                print(part.text)
            elif image:= part.as_image():
                # Ensure directory exists
                os.makedirs(os.path.dirname(output_path), exist_ok=True)
                image.save(output_path)
                print(f"Successfully edited image")