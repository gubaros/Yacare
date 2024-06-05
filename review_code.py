import os
import requests
import openai

# Configuración de la API de OpenAI
openai.api_key = os.getenv("OPENAI_API_KEY")

# Obtiene la URL del repositorio y el PR ID
repo_url = os.getenv("GITHUB_REPOSITORY")
pr_id = os.getenv("GITHUB_REF").split('/')[-1]

# Extrae el contenido del PR usando la API de GitHub
response = requests.get(f"https://api.github.com/repos/{repo_url}/pulls/{pr_id}/files")
pr_files = response.json()

# Preparar los archivos para el envío al endpoint
files_content = {}
for file in pr_files:
    file_path = file["filename"]
    with open(file_path, 'r') as f:
        files_content[file_path] = f.read()

# Enviar el contenido al endpoint del servicio
endpoint = "http://tu_servicio_endpoint/api/compare"
data = {
    "pr_content": files_content,
    "branch": "main"  # Puedes cambiar esto según sea necesario
}
response = requests.post(endpoint, json=data)

# Manejo de la respuesta
print(response.json())

