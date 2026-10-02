# Project name used for resource naming
project_name = "agent-project"

# Your Production Google Cloud project id
prod_project_id = "agents-cli-test-cicd-u75kiv"

# Your Staging / Test Google Cloud project id
staging_project_id = "agents-cli-test-cicd-u75kiv"

# Your Google Cloud project ID that will be used to host the Cloud Build pipelines.
cicd_runner_project_id = "agents-cli-test-cicd-u75kiv"
# Name of the host connection you created in Cloud Build
host_connection_name = "git-agent-project"
github_pat_secret_id = "github-pat"

repository_owner = "agents-cli-dev-bot"

# Name of the repository you added to Cloud Build
repository_name = "agent-project"

# The Google Cloud region you will use to deploy the infrastructure
region = "us-east1"
