import requests
from kivy.app import App
from kivy.lang import Builder
from kivy.properties import StringProperty
from kivy.uix.boxlayout import BoxLayout

SERVER_URL = 'http://localhost:5000'

KV = '''
<RootWidget>:
    orientation: 'vertical'
    padding: 10
    spacing: 10

    TextInput:
        id: command
        hint_text: 'Enter command'
        size_hint_y: None
        height: '40dp'
    Button:
        text: 'Send'
        size_hint_y: None
        height: '40dp'
        on_press: root.send_command(command.text)
    Label:
        text: root.response
        size_hint_y: None
        height: self.texture_size[1]
    Button:
        text: 'Start Listening'
        size_hint_y: None
        height: '40dp'
        on_press: root.start_jarvis()
    Button:
        text: 'Stop Listening'
        size_hint_y: None
        height: '40dp'
        on_press: root.stop_jarvis()
'''

class RootWidget(BoxLayout):
    response = StringProperty('')

    def send_command(self, text: str) -> None:
        if not text:
            return
        try:
            resp = requests.post(f'{SERVER_URL}/ask', json={'q': text}, timeout=5)
            if resp.ok:
                self.response = resp.json().get('response', '')
            else:
                self.response = f'Error: {resp.status_code}'
        except Exception as exc:
            self.response = f'Error: {exc}'

    def start_jarvis(self) -> None:
        try:
            requests.post(f'{SERVER_URL}/start', timeout=5)
        except Exception as exc:
            self.response = f'Error: {exc}'

    def stop_jarvis(self) -> None:
        try:
            requests.post(f'{SERVER_URL}/stop', timeout=5)
        except Exception as exc:
            self.response = f'Error: {exc}'

class JarvisMobileApp(App):
    def build(self):
        Builder.load_string(KV)
        return RootWidget()

if __name__ == '__main__':
    JarvisMobileApp().run()
