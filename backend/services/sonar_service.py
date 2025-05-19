import requests
from dotenv import load_dotenv
import os

load_dotenv()
SONAR_API_KEY = os.getenv('SONAR_API_KEY')

def sonar_research(topic):
    headers = {'Authorization': f'Bearer {SONAR_API_KEY}'}
    response = requests.get(f'https://api.perplexity.ai/research?query={topic}', headers=headers)
    return response.json()['results']

def sonar_reasoning(content, platform):
    headers = {'Authorization': f'Bearer {SONAR_API_KEY}'}
    data = {"content": content, "platform": platform}
    response = requests.post('https://api.perplexity.ai/reason', json=data, headers=headers)
    return response.json()