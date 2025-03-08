import requests

api_key = '5ce77c0e-2947-47d2-abd9-a1a11656e38d'
file_id = "71355bfe-8bdd-40d6-af19-8c34f5daced7"
url = 'https://api.vapi.ai/knowledge-base'
headers = {
    'Authorization': f'Bearer {api_key}',
    'Content-Type': 'application/json'
}
data = {
    'name': 'poc doctor',
    'provider': 'trieve',
    'searchPlan': {
        'searchType': 'semantic',
        'topK': 3,
        'removeStopWords': True,
        'scoreThreshold': 0.7
    },
    'createPlan': {
        'type': 'create',
        'chunkPlans': [
            {
                'fileIds': [file_id],
                'targetSplitsPerChunk': 50,
                'splitDelimiters': ['.!?\n'],
                'rebalanceChunks': True
            }
        ]
    }
}

response = requests.post(url, headers=headers, json=data)

if response.status_code == 201:
    kb_id = response.json().get('id')
    print(f'Knowledge Base created successfully. KB ID: {kb_id}')
else:
    print(f'Failed to create Knowledge Base. Status code: {response.status_code}')
    print(response.text)
