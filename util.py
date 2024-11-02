from datetime import datetime


def _get_children(text, block_type='paragraph'):
    """
        Given a text and block_type, returns the dictionary to format in a notion request.
    """

    return {
        "object": "block",
        "type": block_type,
        block_type: {
            "rich_text": [
                {
                    "type": "text",
                    "text": {
                        "content": text
                    }
                }
            ]
        }
    }

def dream_to_json(dream_title, dream_claude, dream_original, emoji, database_id):
    """
        Given a dream title, a dream text and a database ID, returns a JSON object to be sent to Notion.
        
        Args:
        dream_title (str): The title of the dream.
        dream_claude (str): The dream text corrected by Claude.
        dream_original (str): The original dream text.
        database_id (str): The ID of the database to send the dream to.
    """
    return {
        "parent": { "database_id": database_id },
        "icon": {
        "emoji": emoji
        },
        "properties": {
            "Name": {
                "title": [
                    {
                        "text": {
                            "content": dream_title
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
            _get_children('Claude-Treated : ', 'heading_2'),
            _get_children(dream_claude),
            _get_children('Original : ', 'heading_2'),
            _get_children(dream_original)
        ]
    }

    
def load_keys(key_file):
        """
            Load needed API keys from the keys.env file.

            Returns:
            3-uple : (NOTION_TOKEN, DATABASE_ID, CLAUDE)
        """
        with open(key_file, 'r') as f:
            keys = f.readlines()
            for key in keys:
                key = key.strip()
                if key.startswith('NOTION'):
                    NOTION_TOKEN = key.split('=')[1]
                    if NOTION_TOKEN == 'notion-key':
                        print('Please set your Notion key in the keys.env file.')
                        exit(1)
                elif key.startswith('DATABASE'):
                    DATABASE_ID = key.split('=')[1]
                    if DATABASE_ID == 'database-id':
                        print('Please set your Notion database ID in the keys.env file.')
                        exit(1)
                elif key.startswith('CLAUDE'):
                    CLAUDE = key.split('=')[1]
                    if CLAUDE == 'claude-key':
                        print('Please set your Claude key in the keys.env file.')
                        exit(1)

        print('Notion token:', NOTION_TOKEN)
        print('Database ID:', DATABASE_ID)
        print('Claude token:', CLAUDE)

        return NOTION_TOKEN, DATABASE_ID, CLAUDE