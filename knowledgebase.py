import requests

api_key = '1b60bee6-8c3c-4715-a7cb-f30c17a67fe4'
file_id = "51e5093f-81c6-4434-b8b8-6a4c1076e250"
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
