# Coding agent guide

This project was scaffolded by agents-cli. The agent code lives in `app/`, and `agents-cli info` prints the project's language and deployment target.

- Resuming? Read `.agents-cli-spec.md` first: it is the approved spec.
- Before each stage, call the Skill tool with the matching agents-cli skill: `google-agents-cli-workflow` to plan a new capability (memory, OAuth, triggers, sub-agents); `google-agents-cli-scaffold` to create, scaffold or upgrade the project; `google-agents-cli-eval` to evaluate it; `google-agents-cli-deploy` to deploy, add a deployment target or CI/CD, or provision infrastructure; `google-agents-cli-observability` to observe it; `google-agents-cli-publish` to publish it. For ADK API code, call the Skill tool with `google-agents-cli-adk-code`. No Skill tool: read that skill's `SKILL.md` instead.
- `app/agent.py` exports `root_agent` and `app = App(root_agent=root_agent, name="app")`: `run`, eval and `scaffold enhance` need both names.
- Tools you write go in their own module beside the agent file (`tools.py`) and return bad input, missing data and no match as results the model can explain, not exceptions.
- Change only what was asked. Keep config values, comments, formatting, `.env` entries and the files the template generated: they wire serving, sessions and A2A.
- Keep the model the code names unless the user asks to change it. On a model 404, set `GOOGLE_CLOUD_LOCATION` in `.env` (try `global`) and keep the model name.
- Smoke-test each change with `agents-cli run "<prompt>"`. Check behavior with `agents-cli eval run`, not with unit tests that assert on model output.
- The eval dataset and config are already in `tests/eval/`. Start with 1-2 cases and expect 5-10 or more fix-and-rerun iterations.
- Before any deploy: rerun `agents-cli eval run`, paste every case's score, ask "Ready to deploy to dev?" and wait for an explicit yes. Judge by the scores: the exit code only gates on configured thresholds and errored cases.
- Ask before creating or pushing to a git repository, and before deleting a deployment or cloud data.
- Before any `--apply` or `terraform apply`, show the user the plan summary and wait for an explicit yes: `infra single-project --apply` and `infra cicd --apply` run `terraform apply -auto-approve`.
- API keys and secrets go in Secret Manager. Infrastructure goes in Terraform.
- A Terraform 409 or "already exists" means `terraform import`, not a new resource.
- `agents-cli <command> --help` is authoritative, and its last line names the source file that implements the command.
- Run Python with `uv run`, after `agents-cli install`. Run `uv run pytest tests/unit tests/integration` before deploying.
