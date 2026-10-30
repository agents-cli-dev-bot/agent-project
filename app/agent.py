from google.adk.agents import Agent, SequentialAgent
from google.adk.apps import App
from google.adk.models import Gemini
from google.genai import types
from app.tools import lookup_product_info, check_known_issues, escalate_to_human, draft_eval_case

MODEL = "gemini-3.5-flash"

support_agent = Agent(
    name="support_agent",
    model=Gemini(
        model=MODEL,
        retry_options=types.HttpRetryOptions(attempts=3),
    ),
    instruction=(
        "You are a customer support agent. Your role is to answer product questions, "
        "troubleshoot common issues, and escalate complex cases.\n"
        "You politely refuse to answer any out-of-scope questions unrelated to the products.\n"
        "Priority levels for escalation are: low, medium, high, critical.\n"
        "Use your tools when necessary."
    ),
    tools=[lookup_product_info, check_known_issues, escalate_to_human],
    output_key="support_response"
)

evaluator_agent = Agent(
    name="evaluator_agent",
    model=Gemini(
        model=MODEL,
        retry_options=types.HttpRetryOptions(attempts=3),
    ),
    instruction=(
        "You evaluate the response of the support agent.\n"
        "Review the support_response in state: {support_response}.\n"
        "Identify if the response is weak (e.g. incorrect tone, unhelpful, missed escalation). "
        "If it is weak, use the draft_eval_case tool to draft a new eval case. "
        "Then, provide the final response to the user by either repeating the support_response if it is good, "
        "or providing an improved response."
    ),
    tools=[draft_eval_case]
)

root_agent = SequentialAgent(
    name="agent_project",
    sub_agents=[support_agent, evaluator_agent],
)

app = App(
    root_agent=root_agent,
    name="app",
)
