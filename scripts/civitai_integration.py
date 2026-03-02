import requests

def fetch_civitai_models(api_key):
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    response = requests.get("https://civitai.com/api/v1/models", headers=headers)
    return response.json() if response.status_code == 200 else {"error": "API request failed"}

def get_model_download_links(model_id):
    response = requests.get(f"https://civitai.com/api/v1/models/{model_id}/download")
    return response.json() if response.status_code == 200 else {"error": "Download failed"}

# Example usage:
# models = fetch_civitai_models("YOUR_API_KEY")
# print(models)