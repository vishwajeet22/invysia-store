from google.adk.agents.llm_agent import Agent
from google.adk.models.google_llm import Gemini
from google.genai.types import HttpRetryOptions

from daedalus.src.agent_persona import DAEDALUS_PERSONA

retry_config=HttpRetryOptions(
    attempts=5,  # Maximum retry attempts
    exp_base=7,  # Delay multiplier
    initial_delay=1, # Initial delay before first retry (in seconds)
    http_status_codes=[429, 500, 503, 504] # Retry on these HTTP errors
)

root_agent = Agent(
    model=Gemini(
        model="gemini-2.5-flash",
        retry_options=retry_config
    ),
    name='daedalus',
    description='Daedalus, a experienced designer at Invysia',
    instruction=DAEDALUS_PERSONA,
    tools=[],
)
