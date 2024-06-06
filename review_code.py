import os
import requests
import json
import hashlib
from openai import OpenAI, OpenAIError

def calculate_file_hash(content):
    return hashlib.md5(content.encode()).hexdigest()

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

# Leer el archivo de estado de revisiones anteriores
reviewed_files = {}
state_file_path = "reviewed_files.json"

if os.path.exists(state_file_path):
    with open(state_file_path, "r") as f:
        reviewed_files = json.load(f)

# Preparar el contenido del PR para enviarlo a OpenAI
files_content = ""
new_files = False
for file in pr_files:
    file_path = file.get("filename")
    patch = file.get("patch")
    if file_path and patch:
        file_hash = calculate_file_hash(patch)
        if file_path not in reviewed_files or reviewed_files[file_path] != file_hash:
            files_content += f"File: {file_path}\n{patch}\n\n"
            reviewed_files[file_path] = file_hash
            new_files = True

if not new_files:
    print("No new files to review.")
    exit(0)

# Interactuar con OpenAI para hacer la revisión del código
prompt = f"Please review the following pull request:\n\n{files_content}\n\n Please review the following source file for each of the following aspects. Only provide output if its worthy: 1. **Bugs**: Identify any potential bugs or errors in the code.  2. **Computational Complexity**: Analyze the computational complexity of the code and suggest any possible optimizations.  3. **Clean Coding Practices**: Evaluate the code for clean coding practices, including readability, maintainability, and adherence to coding standards.  4. **Coding Standards**: Check for compliance with the relevant coding standards and best practices.  5. **Security**: Identify any potential security vulnerabilities in the code.  6. **Documentation**: Assess the quality and completeness of the code documentation, including comments and inline documentation.  7. **Testing**: Evaluate the adequacy of testing, including the presence and quality of unit tests, integration tests, and other relevant testing practices.  8. **Performance**: Identify any potential performance issues and suggest improvements.  9. **Scalability**: Assess the scalability of the code and recommend any necessary changes to handle increased load or data size.  10. **Code Structure**: Evaluate the overall structure and organization of the code, including the use of design patterns and modularity."
 #Provide feedback on the code quality, potential bugs, and improvements. For each file, review methods and provide a detailed note on the algorithm complexity presented, if found"

try:
    chat_completion = client.chat.completions.create(
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt},
        ],
        model="gpt-3.5-turbo",
        max_tokens=2000,  # Reducir el número de tokens
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
    "body": f"**Code Review by GPT:**\n\n{review_comments}"
}

try:
    comment_response = requests.post(comment_url, headers=comment_headers, json=comment_data)
    comment_response.raise_for_status()
    print(f"Successfully posted review comment to PR #{pr_number}")
except requests.exceptions.RequestException as e:
    print(f"Error posting comment to PR: {e}")
    exit(1)

# Guardar el estado actualizado de archivos revisados
with open(state_file_path, "w") as f:
    json.dump(reviewed_files, f)

