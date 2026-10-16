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

import datetime
from zoneinfo import ZoneInfo
import json
import os

from google.adk.agents import Agent
from google.adk.apps import App
from google.adk.models import Gemini
from google.adk.agents.callback_context import CallbackContext
from google.genai import types
from google import genai
from app.tools import lookup_product_info, check_known_issues, escalate_to_human



MODEL = "gemini-3.5-flash"


async def evaluate_and_draft_eval(context: CallbackContext) -> None:
    if not context.response or not context.response.text:
        return
    
    # Simple self-eval check
    client = genai.Client(vertexai=True, location='global')
    eval_prompt = f"Evaluate this customer support response for clarity, accuracy, and tone. If it is weak or unhelpful, reply with 'WEAK'. Otherwise reply 'OK'. Response: {context.response.text}"
    eval_res = client.models.generate_content(
        model="gemini-3.5-flash",
        contents=eval_prompt
    )
    if eval_res.text and "WEAK" in eval_res.text:
        # Draft new eval case
        prompt_text = context.prompt.parts[0].text if context.prompt and context.prompt.parts else "Unknown prompt"
        case = {
            "eval_case_id": f"auto_weak_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}",
            "prompt": {
                "role": "user",
                "parts": [{"text": prompt_text}]
            }
        }
        dataset_path = "tests/eval/datasets/auto_generated_eval.json"
        os.makedirs(os.path.dirname(dataset_path), exist_ok=True)
        if os.path.exists(dataset_path):
            with open(dataset_path, "r") as f:
                data = json.load(f)
        else:
            data = {"eval_cases": []}
        
        data["eval_cases"].append(case)
        with open(dataset_path, "w") as f:
            json.dump(data, f, indent=2)


root_agent = Agent(
    name="agent_project",
    model=Gemini(
        model=MODEL,
        retry_options=types.HttpRetryOptions(attempts=3),
    ),
    instruction="""You are a customer support agent.
You answer product questions, troubleshoot common issues, and escalate complex cases.
You politely refuse out-of-scope questions unrelated to the product.
You have tools to lookup product info, check known issues, and escalate to a human.
""",
    tools=[lookup_product_info, check_known_issues, escalate_to_human],
    after_agent_callback=evaluate_and_draft_eval,
)

app = App(
    root_agent=root_agent,
    name="app",
)
