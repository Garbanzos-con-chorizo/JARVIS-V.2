from flask import Flask, jsonify, request

from jarvis_core import JarvisCore

app = Flask(__name__)
core = JarvisCore()

@app.route('/start', methods=['POST'])
def start_listening():
    core.start()
    return jsonify({'status': 'listening'})

@app.route('/stop', methods=['POST'])
def stop_listening():
    core.stop_listening()
    return jsonify({'status': 'stopped'})

@app.route('/ask', methods=['POST'])
def ask():
    data = request.get_json() or {}
    prompt = data.get('q', '').strip()
    if not prompt:
        return jsonify({'error': 'No prompt provided'}), 400
    response = core.chatgpt.ask(prompt)
    return jsonify({'response': response})

def main() -> None:
    app.run(host='0.0.0.0', port=5000)

if __name__ == '__main__':
    main()
