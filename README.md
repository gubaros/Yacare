[![Code Review with GPT](https://github.com/gubaros/ai-cr/actions/workflows/cia.yml/badge.svg)](https://github.com/gubaros/ai-cr/actions/workflows/cia.yml)

# Code Review with GPT

This repository automates code reviews using OpenAI's GPT-3.5 Turbo model. When a pull request (PR) is created or updated, the content of the PR is sent to GPT-3.5 Turbo for a code review. The feedback is then posted as a comment on the PR.

## How It Works

- **GitHub Actions Workflow**: The workflow is triggered by a `pull_request` event. It checks out the code, sets up Python, installs dependencies, extracts the PR number, and runs the review script.

- **PR Content Fetching**: The script fetches the files changed in the PR using GitHub's API.

- **Interaction with OpenAI**: The content of the PR is sent to OpenAI's GPT-3.5 Turbo model with a prompt to review the code for quality, potential bugs, and improvements.

- **Posting Review Comments**: The feedback from GPT-3.5 Turbo is then posted as a comment on the PR using GitHub's API.

## Setup

1. **Fork the Repository**: Fork this repository to your GitHub account.

2. **Set Up GitHub Secrets**:
   - `OPENAI_API_KEY`: Your OpenAI API key.
   - `GH_TOKEN`: Your GitHub token with `repo` scope to access the repository and post comments.

3. **Configure GitHub Actions Workflow**: Ensure you have a workflow file in `.github/workflows/` that triggers on `pull_request` events and runs the review script.

## Usage

Once the setup is complete, any new pull request or updates to an existing pull request will trigger the workflow. The script will analyze the PR, send the content to OpenAI for a review, and post the feedback as a comment on the PR.

## Purpose

The purpose of this tool is to streamline the code review process by leveraging AI to provide automated feedback, ensuring code quality and identifying potential issues early in the development process.

