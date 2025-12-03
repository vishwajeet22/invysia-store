from google.adk.agents.llm_agent import Agent
from google.adk.models.google_llm import Gemini
from google.genai.types import HttpRetryOptions

import logging
logger = logging.getLogger(__name__)

from .src.agent_persona import DAEDALUS_PERSONA
from .src.agent_tools import get_payment_link, generate_prompts, generate_calendar

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
    tools=[get_payment_link, generate_prompts, generate_calendar],
)

logger.info("Daedalus agent initialized")
