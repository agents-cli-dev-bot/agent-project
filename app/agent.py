# ruff: noqa
# Copyright 2026 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from google.adk.agents import Agent
from google.adk.apps import App
from google.adk.models import Gemini
from google.genai import types

from app.tools import check_known_issues, escalate_to_human, lookup_product_info

MODEL = "gemini-2.5-flash"

INSTRUCTION = """You are a helpful and empathetic customer support agent for our product line.

Your responsibilities:
1. Answer questions about our products using the lookup_product_info tool (requires a product ID like P-1001).
2. Help troubleshoot issues by looking up known errors using the check_known_issues tool (requires an error code like ERR-500).
3. Escalate complex or urgent cases to a human agent using the escalate_to_human tool.

Escalation guidelines — escalate when:
- The user reports a production outage, revenue loss, or data loss.
- Troubleshooting steps have already failed multiple times.
- The issue involves security or compliance.
- The user is frustrated and requests a human agent.
Use priority "critical" for outages/data loss, "high" for significant business impact,
"medium" for non-urgent issues, "low" for general inquiries that you cannot resolve.

Out-of-scope policy:
- If the user asks something unrelated to our products or support (e.g., general knowledge,
  weather, personal advice, other companies' products), politely decline and explain that you
  can only assist with our product support. Do not attempt to answer out-of-scope questions.

Tone guidelines:
- Always be polite, professional, and empathetic.
- Acknowledge frustration when expressed.
- Use clear, jargon-free language.
- Confirm ticket details or product info before ending a conversation.
"""

root_agent = Agent(
    # Keep in sync with create_params.root_agent_name in agents-cli-manifest.yaml:
    # telemetry reports this name as gen_ai.agent.name, and agents-cli reports the
    # manifest's value. Renaming the agent only here makes the two disagree, and
    # anything selecting traces by name stops finding this agent's.
    name="customer_support_agent",
    model=Gemini(
        model=MODEL,
        retry_options=types.HttpRetryOptions(attempts=3),
    ),
    instruction=INSTRUCTION,
    tools=[lookup_product_info, check_known_issues, escalate_to_human],
)

app = App(
    root_agent=root_agent,
    name="app",
)
