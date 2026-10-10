terraform {
  backend "gcs" {
    bucket = "agents-cli-test-cicd-u75kiv-terraform-state"
    prefix = "agent-project/prod"
  }
}
