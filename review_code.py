import os
import requests
import json
from openai import OpenAI

def get_full_repository_context():
    context = ""
    for root, dirs, files in os.walk("."):
        if ".git" in dirs:
            dirs.remove(".git")  # Excluir el directorio .git
        for file in files:
            file_path = os.path.join(root, file)
            try:
                with open(file_path, 'r') as f:
                    content = f.read()
                    # Limitar el contenido para evitar exceder los límites de tokens
                    if len(content) > 1000:
                        content = content[:500] + "... [content truncated] ..." + content[-500:]
                    context += f"File: {file_path}\n{content}\n\n"
            except Exception as e:
                print(f"Could not read file {file_path}: {str(e)}")
    return context

def get_pr_files(repo_url, pr_number, headers):
    url = f"https://api.github.com/repos/{repo_url}/pulls/{pr_number}/files"
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()

def main():
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    repo_url = os.getenv("GITHUB_REPOSITORY")
    pr_number = os.getenv("PR_NUMBER")
    gh_token = os.getenv("GH_TOKEN")

    headers = {
        "Accept": "application/vnd.github.v3+json",
        "Authorization": f"Bearer {gh_token}"
    }

    pr_files = get_pr_files(repo_url, pr_number, headers)
    
    full_context = get_full_repository_context()
    
    pr_changes = "\n".join([f"File: {file['filename']}\n{file.get('patch', 'No patch available')}" for file in pr_files])

    prompt = f"""
    Full Repository context:
    {full_context}

    Pull request changes:
    {pr_changes}

    Please review the following pull request in the context of the entire repository.
    Focus on:
    0. Cohesion between the style used in the PR and the already existing in the repo. 
    1. Code quality and best practices
    2. Potential bugs or errors
    3. Performance and efficiency
    4. Consistency with the existing codebase
    5. Security considerations
    6. Suggestions for improvements

    Provide a concise but thorough review, considering the full context of the repository.
    """

    try:
        chat_completion = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are an expert code reviewer with knowledge of multiple programming languages and full context of the repository."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=4000,
            temperature=0.7
        )
        review = chat_completion.choices[0].message.content.strip()

        comment_url = f"https://api.github.com/repos/{repo_url}/issues/{pr_number}/comments"
        comment_data = {"body": f"**AI Code Review (with full repository context):**\n\n{review}"}
        comment_response = requests.post(comment_url, headers=headers, json=comment_data)
        comment_response.raise_for_status()
        print("Successfully posted review comment")
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    main()
