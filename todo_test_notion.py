import requests
import json
from datetime import datetime

NOTION_TOKEN = "your_integration_token_here"
DATABASE_ID = "your_database_id_here"

headers = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28"
}

def add_dream_to_notion(dream_text):
    url = "https://api.notion.com/v1/pages"
    
    data = {
        "parent": { "database_id": DATABASE_ID },
        "properties": {
            "Title": {
                "title": [
                    {
                        "text": {
                            "content": f"Dream on {datetime.now().strftime('%Y-%m-%d')}"
                        }
                    }
                ]
            },
            "Date": {
                "date": {
                    "start": datetime.now().strftime("%Y-%m-%d")
                }
            }
        },
        "children": [
            {
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [
                        {
                            "type": "text",
                            "text": {
                                "content": dream_text
                            }
                        }
                    ]
                }
            }
        ]
    }
    
    response = requests.post(url, headers=headers, data=json.dumps(data))
    
    if response.status_code == 200:
        print("Successfully added dream to Notion!")
    else:
        print(f"Failed to add dream. Status code: {response.status_code}")
        print(response.text)

# Usage
# add_dream_to_notion("I dreamt I was flying over a city made of candy...")