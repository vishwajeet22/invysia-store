from google.genai.types import Part
from pathlib import Path
from google.adk.tools import ToolContext

async def get_infographic(process_name: str, tool_context: ToolContext) -> dict:
    """
    Retrieves an infographic and sends it to the user as an artifact.
    
    Args:
        process_name: The name of the process for which to retrieve the infographic. Supports 'buying_process' and 'product_tiers'.
    
    Returns:
        A confirmation message that the infographic has been generated with ID.
    """
    # Map process names to image file paths
    assets_dir = Path(__file__).parent.parent / "assets"
    
    infographic_map = {
        "buying_process": assets_dir / "buying_process.jpg",
        "product_tiers": assets_dir / "product_tiers.jpg"
    }
    
    if process_name not in infographic_map:
        raise ValueError(f"Unsupported process name for infographic: {process_name}")
    
    image_path = infographic_map[process_name]
    
    # Check if file exists locally
    if image_path.exists():
        with open(image_path, 'rb') as f:
            image_bytes = f.read()
        mime_type = "image/jpeg" 
    else:
        # Fallback: fetch a placeholder image from the web
        # In production, you should have the actual infographics stored locally
        import requests
        response = requests.get("https://fastly.picsum.photos/id/156/800/600.jpg")
        response.raise_for_status()
        image_bytes = response.content
        mime_type = "image/jpeg"
    # Create Part with inline_data
    image_part = Part.from_bytes(
        data=image_bytes,
        mime_type=mime_type
    )

    version = await tool_context.save_artifact(
        filename=process_name,
        artifact=image_part,
    )

    return {"status": "success", "filename": process_name, "version": version}

def fill_questionnaire(question: str, answer: str, tool_context: ToolContext) -> dict:
    """
    Updates the questionnaire in the session state with a new question and answer.

    Args:
        question: The question asked.
        answer: The answer provided by the user.
    
    Returns:
        A confirmation message.
    """
    session_state = tool_context.state
    questionnaire = session_state.get("user:questionnaire", [])
    questionnaire.append({"question": question, "answer": answer})
    session_state["user:questionnaire"] = questionnaire
    return {"status": "success"}
