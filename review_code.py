import os
import requests
from openai import OpenAI, OpenAIError

# Configuración de la API de OpenAI
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Obtiene la URL del repositorio y el PR ID
repo_url = os.getenv("GITHUB_REPOSITORY")
pr_number = os.getenv("PR_NUMBER")

# Verificar que PR_NUMBER se ha obtenido correctamente
print(f"PR Number: {pr_number}")

# Extrae el contenido del PR usando la API de GitHub
headers = {
    "Accept": "application/vnd.github.v3+json",
    "Authorization": f"Bearer {os.getenv('GH_TOKEN')}"
}

# La URL debe tener el formato correcto, asegurándose de usar el número del PR
url = f"https://api.github.com/repos/{repo_url}/pulls/{pr_number}/files"
print(f"Fetching PR files from URL: {url}")

try:
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    pr_files = response.json()
except requests.exceptions.RequestException as e:
    print(f"Error fetching PR files: {e}")
    exit(1)

# Preparar el contenido del PR para enviarlo a OpenAI
files_content = ""
for file in pr_files:
    file_path = file.get("filename")
    patch = file.get("patch")
    if file_path and patch:
        files_content += f"File: {file_path}\n{patch}\n\n"

# Interactuar con OpenAI para hacer la revisión del código
prompt = f"Please review the following pull request:\n\n{files_content}\n\nProvide feedback on the code quality, potential bugs, and improvements."

try:
    chat_completion = client.chat.completions.create(
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt},
        ],
        model="gpt-4o",
        max_tokens=300,  # Reducir el número de tokens
        temperature=0.7,  # Ajustar la temperatura para una respuesta más eficiente
    )
    review_comments = chat_completion.choices[0].message.content.strip()
    print(f"Code Review Comments:\n{review_comments}")
except OpenAIError as e:
    print(f"Error interacting with OpenAI: {e}")
    exit(1)

# Crear un comentario en el PR usando la API de GitHub
comment_url = f"https://api.github.com/repos/{repo_url}/issues/{pr_number}/comments"
comment_headers = {
    "Authorization": f"Bearer {os.getenv('GH_TOKEN')}",
    "Accept": "application/vnd.github.v3+json"
}
comment_data = {
    "body": f"**Code Review by GPT-3.5 Turbo:**\n\n{review_comments}"
}

try:
    comment_response = requests.post(comment_url, headers=comment_headers, json=comment_data)
    comment_response.raise_for_status()
    print(f"Successfully posted review comment to PR #{pr_number}")
except requests.exceptions.RequestException as e:
    print(f"Error posting comment to PR: {e}")
    exit(1)

