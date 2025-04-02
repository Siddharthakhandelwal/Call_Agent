import requests

api_key = '0f4fbb74-f6df-4b5f-83dc-6e7f380e6cf0'
file_id = "9815ca9a-6bc4-4999-8ca5-52aeada91f19"
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
