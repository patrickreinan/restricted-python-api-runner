from flask import Flask, request, jsonify
from RestrictedPython import compile_restricted, safe_globals

app = Flask(__name__)

@app.route('/run', methods=['POST'])
def run_code():
    data = request.get_json()
    code = data.get('code', '')
    output = None
    exit_code = 0
    try:
        byte_code = compile_restricted(code, '<string>', 'exec')
        restricted_locals = {}
        exec(byte_code, safe_globals, restricted_locals)
        output = restricted_locals.get('output', 'No output')
    except Exception as e:
        output = str(e)
        exit_code = 1
    return jsonify({
        'output': output,
        'exitCode': exit_code
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
