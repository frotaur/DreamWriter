import pynput.keyboard as kb
import datetime


 # TODO : Solve the problem of suppressing shift and CAPS. Ideally,
 # Supress everything except for shift and caps, but that seems hard!
 
class KeyCorder():
    """
        Class handling the starting of recording, recording, and stopping of recording.
    """
    def __init__(self):
        self.recording = False
        self.keystrokes = []
        self.shift_pressed = False

        self.enters_in_a_row = 0
        self.esc_in_a_row = 0
        self.kb_control = kb.Controller()


    def on_press(self, key):
        if self.recording:
            if key == kb.Key.enter:
                self.keystrokes.append('\n')
            elif key == kb.Key.shift:
                self.shift_pressed = True
            elif key == kb.Key.backspace:
                self.keystrokes.pop()
            elif key == kb.Key.space:
                self.keystrokes.append(' ')
            else:
                try:
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
                print('Exiting...')
                self.esc_in_a_row = 0
                return False # Stop the listener
        elif key == kb.Key.enter:
            self.esc_in_a_row = 0
            if(not self.recording):
                self.enters_in_a_row+=1
                if self.enters_in_a_row == 5:
                    self.recording = True
                    print('Recording...')
                    self.enters_in_a_row = 0
        else :
            self.esc_in_a_row = 0
            self.enters_in_a_row = 0
    
    def on_release(self, key):
        if key == kb.Key.shift:
            self.shift_pressed = False

    def should_suppress(self, key):
        return key not in {kb.Key.shift, kb.Key.shift_r, kb.Key.caps_lock}
    
    def start_listening(self):
        with kb.Listener(on_press=self.on_press, on_release=self.on_release, suppress=self.should_suppress) as listener:
            listener.join()

    def save_dream(self):
        print('Saving dream...')    
        with open('dream.txt', 'a') as f:
            datestamp = '\n\nDREAM, {} : \n\n\n\n'.format(datetime.datetime.now())
            f.write(datestamp+''.join(self.keystrokes))

        self.keystrokes = []