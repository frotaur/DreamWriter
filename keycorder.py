import pynput.keyboard as kb
import datetime
from util import dream_to_json, load_keys
import requests,json
from claude_dream import ClaudeDreamCorrection
from pathlib import Path
 # TODO : Solve the problem of suppressing shift and CAPS. Ideally,
 # Supress everything except for shift and caps, but that seems hard!
 
cur_dir = Path(__file__).parent
class KeyCorder():
    """
        Class handling the starting of recording, recording, and stopping of recording.
        Also uploads the recorded dream to Notion.
    """
    def __init__(self, keys_file='keys.env', log_folder=None):
        self.recording = False
        self.keystrokes = []
        self.shift_pressed = False

        self.enters_in_a_row = 0
        self.esc_in_a_row = 0
        
        notion, database, claude = load_keys(keys_file)
        self.DATABASE_KEY = database

        self.claudector = ClaudeDreamCorrection(api_key=claude)

        self.notion_headers = {
        "Authorization": f"Bearer {notion}",
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28" }

        self.notion_url = "https://api.notion.com/v1/pages"
        self.claude_url = ""

        if(log_folder is None):
            self.log_folder = Path(__file__).parent / 'logs'
        else:
            self.log_folder = Path(log_folder)
        self.log_folder.mkdir(parents=True, exist_ok=True)
        self.log_file = self.log_folder / f"dream_{datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.txt"
        with open(self.log_file, 'w') as f:
            f.write("Dream session started at " + datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S') + "\n")


    def log(self,text):
        """
            Logs the given text to the log file, and prints it to the console.
        """
        with open(self.log_file, 'a') as f:
            f.write(text + "\n")
        print(text)

    def on_press(self, key):
        if self.recording:
            if key == kb.Key.enter:
                self.keystrokes.append('\n')
            elif key == kb.Key.shift:
                self.shift_pressed = True
            elif key == kb.Key.backspace:
                if(len(self.keystrokes) > 0):
                    self.keystrokes.pop()
            elif key == kb.Key.space:
                self.keystrokes.append(' ')
            else:
                try:
                    if(key.char is not None):
                        if self.shift_pressed:
                            self.keystrokes.append(key.char.upper())
                        else:
                            self.keystrokes.append(key.char)
                except AttributeError:
                    pass # Key is not a character
            
        if key == kb.Key.esc:
            self.esc_in_a_row += 1
            self.enters_in_a_row = 0
            if self.esc_in_a_row == 5:
                # Save the dream
                if(self.recording):
                    self.recording = False
                    self.save_dream()
            elif self.esc_in_a_row == 10:
                self.log('Exiting...')
                self.esc_in_a_row = 0
                return False # Stop the listener
    
        elif key == kb.Key.enter:
            self.esc_in_a_row = 0
            if(not self.recording):
                self.enters_in_a_row+=1
                if self.enters_in_a_row == 5:
                    self.recording = True
                    self.log('Recording...')
                    self.enters_in_a_row = 0
        else :
            self.esc_in_a_row = 0
            self.enters_in_a_row = 0
    
    def on_release(self, key):
        if key == kb.Key.shift:
            self.shift_pressed = False
    
    def start_listening(self):
        with kb.Listener(on_press=self.on_press, on_release=self.on_release, suppress=True) as listener:
            listener.join()

    def save_dream(self):
        self.log('Saving dream...')
        self.log('--------- DREAM RAW TEXT ---------')
        self.log(''.join(self.keystrokes))
        self.log('----------------------------------')    
        
        dream_text = ''.join(self.keystrokes)
        if(dream_text==''):
            self.log('No text submitted, skipping')
            return
        
        claude_response = self.claudector.correct_and_title(dream_text,self)
        claude_text = claude_response['dream_text']
        dream_title = claude_response['dream_title']
        emoji = claude_response['dream_emoji']

        data = dream_to_json(dream_title=dream_title, dream_claude=claude_text, dream_original=dream_text, emoji=emoji,database_id=self.DATABASE_KEY)
        response = requests.post(self.notion_url, headers=self.notion_headers, data=json.dumps(data))
    
        if response.status_code == 200:
            self.log("Successfully added dream to Notion!")
        else:
            self.log(f"Failed to add dream. Status code: {response.status_code}")
            self.log(response.text)

        self.keystrokes = []
