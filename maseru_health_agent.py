import asyncio

from google.adk.agents import LlmAgent
from google.adk.models.lite_llm import LiteLlm
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

# -----------------------------
# Model
# -----------------------------

AGENT_MODEL = LiteLlm(model="gpt-4o-mini")

APP_NAME = "maseru_health_support"

# -----------------------------
# Agents
# -----------------------------

greeting_agent = LlmAgent(
    name="GreetingAgent",
    description="Introduces the health support system and sets expectations.",
    instruction=(
        "Greet the user warmly. Explain that you are a Health Support Assistant "
        "based in Maseru, Lesotho. Make it clear that you provide support and guidance, "
        "not medical diagnosis or treatment. Ask how the user is feeling today."
    ),
    model=AGENT_MODEL
)

conversation_agent = LlmAgent(
    name="ConversationAgent",
    description="Gathers information about emotional and physical wellbeing.",
    instruction=(
        "Ask gentle, supportive questions to understand the user's situation. "
        "Focus on emotional state, stress, sleep, duration of symptoms, and severity. "
        "Do not diagnose. Do not give medical advice."
    ),
    model=AGENT_MODEL
)

suggestion_agent = LlmAgent(
    name="SuggestionAgent",
    description="Provides general wellbeing suggestions based on user input.",
    instruction=(
        "Offer safe, non-clinical suggestions related to stress management, rest, "
        "hydration, and emotional wellbeing. Avoid medications or diagnoses. "
        "Encourage professional care if symptoms persist."
    ),
    model=AGENT_MODEL
)

root_agent = LlmAgent(
    name="HealthSupportCoordinator",
    description="Coordinates health support agents and escalates when needed.",
    instruction=(
        "If the user greets or starts the conversation, delegate to GreetingAgent.\n"
        "If the user describes symptoms, stress, or emotional distress, delegate to ConversationAgent.\n"
        "If enough information has been gathered, delegate to SuggestionAgent.\n"
        "If the user expresses severe distress, hopelessness, self-harm thoughts, "
        "or alarming physical symptoms, immediately escalate by advising the user "
        "to visit the nearest clinic or Queen Mamohato Memorial Hospital in Maseru.\n"
        "In escalation cases, do not delegate further—respond directly and clearly."
    ),
    model=AGENT_MODEL,
    sub_agents=[greeting_agent, conversation_agent, suggestion_agent]
)

# -----------------------------
# Runtime Wrapper (IMPORTANT)
# -----------------------------

class MaseruHealthSupportSystem:
    """
    This class is what Streamlit (or any UI) talks to.
    """

    def __init__(self, user_id: str):
        self.user_id = user_id
        self.session_id = f"session_{user_id}"

        self.session_service = InMemorySessionService()
        self.runner = Runner(
            agent=root_agent,
            app_name=APP_NAME,
            session_service=self.session_service
        )

        asyncio.run(
            self.session_service.create_session(
                app_name=APP_NAME,
                user_id=self.user_id,
                session_id=self.session_id
            )
        )

    async def _chat_async(self, message: str) -> str:
        content = types.Content(
            role="user",
            parts=[types.Part(text=message)]
        )

        async for event in self.runner.run_async(
            user_id=self.user_id,
            session_id=self.session_id,
            new_message=content
        ):
            if event.is_final_response():
                return event.content.parts[0].text

        return "I'm here with you. Could you tell me more?"

    def chat(self, message: str) -> str:
        return asyncio.run(self._chat_async(message))


