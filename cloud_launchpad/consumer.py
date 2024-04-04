import subprocess
import json
from channels.generic.websocket import WebsocketConsumer

class VSCodeTerminalConsumer(WebsocketConsumer):
    def connect(self):
        self.accept()

        process = subprocess.Popen(
            ['python', '/home/dell/launchpad_backend/launchpad/scripts/launchpad_python.py'],  # Modify with your script path
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True
        )

        for stdout_line in iter(process.stdout.readline, ""):
            self.send(text_data=json.dumps({'output': stdout_line}))

    def disconnect(self, close_code):
        pass