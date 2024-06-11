[![Code Review with GPT](https://github.com/gubaros/ai-cr/actions/workflows/cia.yml/badge.svg)](https://github.com/gubaros/ai-cr/actions/workflows/cia.yml)
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)

Yacaré, yet another code automated review engine (?)

# Code Review with GPT

This repository automates code reviews using OpenAI's GPT-4o Turbo model. When a pull request (PR) is created or updated, the content of the PR is sent to GPT-4o Turbo for a code review. The feedback is then posted as a comment on the PR.

The comment (AKA "a code review comment") on the PR, provided by GPT, is the main contribution with regards to the benefits of using this software. 

## Why 

- Based on software quality reports, the code review process and the time that developers take to drive from the code, are among the biggest reasons software quality goes down

## How It Works

- **GitHub Actions Workflow**: The workflow is triggered by a `pull_request` event. It checks out the code, sets up Python, installs dependencies, extracts the PR number, and runs the review script.

- **PR Content Fetching**: The script fetches the files changed in the PR using GitHub's API.

- **Interaction with OpenAI**: The content of the PR is sent to OpenAI's GPT-4o Turbo model with a prompt to review the code for quality, potential bugs, and improvements.

- **Posting Review Comments**: The feedback from GPT-4o Turbo is then posted as a comment on the PR using GitHub's API.

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

## Considerations 

1. You might want to consider which GPT model to use and review the python script to manipulate the right model 
2. You might want to fine tune the temperature. Refer to the GPT API temperature docs for further details on this. 
3. You might want to extend the code review strategy and execute a complete checkout (instead of the PR files) so that the code review gains an optimal context, though this will definitely chew tokens from your account.
4. You might want to develop a mechanism to avoid pitfalls, false-positives, and such.
5. Reading an automatically generated code review might create and index a bias, obfuscating underlying real problems not detected by AI. Your role, as a Software Engineer, is to stand by as a Developer in the loop. 

Guido Barosio <guido@bravo47.com>
