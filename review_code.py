import os
import requests
import openai

# Configuración de la API de OpenAI
openai.api_key = os.getenv("OPENAI_KEY")

# Obtiene la URL del repositorio y el PR ID
repo_url = os.getenv("GITHUB_REPOSITORY")
pr_number = os.getenv("GITHUB_REF").split('/')[-1]

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

# Preparar los archivos para el envío al endpoint
files_content = {}
for file in pr_files:
    file_path = file.get("filename")
    if file_path:
        try:
            with open(file_path, 'r') as f:
                files_content[file_path] = f.read()
        except FileNotFoundError:
            print(f"File not found: {file_path}")
        except IOError as e:
            print(f"Error reading file {file_path}: {e}")

# Enviar el contenido al endpoint del servicio
endpoint = "http://tu_servicio_endpoint/api/compare"
data = {
    "pr_content": files_content,
    "branch": "main"  # Puedes cambiar esto según sea necesario
}

try:
    response = requests.post(endpoint, json=data)
    response.raise_for_status()
    review_comments = response.json()
    print(review_comments)
except requests.exceptions.RequestException as e:
    print(f"Error sending data to the endpoint: {e}")
    exit(1)

