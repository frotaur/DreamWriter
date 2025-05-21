# Just test keyboard capture
from keycorder import KeyCorder
import sys

try:
    bro = KeyCorder('mykeys.env')
    bro.start_listening()
except Exception as e:
    print(f"Error: {e}", file=sys.stderr)
    bro.log(f"TERMINATED WITH ERROR: {e}")
    sys.exit(1)
 
