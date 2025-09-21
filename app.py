
# Standard library imports
# (none needed)

# Third-party imports
from flask import Flask, request, jsonify


# Flask app initialization
app = Flask(__name__)


@app.route('/run', methods=['POST'])
def run_code():
    """
    Endpoint to execute restricted Python code with access to numpy (as numpy/np) and pandas (as pd).
    Returns output and exit code as JSON.
    """
    data = request.get_json()
    code = data.get('code', '')
    output = None
    exit_code = 0

    import tempfile
    import subprocess
    import os
    try:
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as tmp_file:
            tmp_file.write(code)
            tmp_file_path = tmp_file.name
        # Run the code using pypy3
        result = subprocess.run([
            'pypy', '-u', tmp_file_path
        ], capture_output=True, text=True)
        output = result.stdout.strip()
        exit_code = result.returncode
    except Exception as e:
        import traceback
        output = f"{e}\n{traceback.format_exc()}"
        exit_code = 1
    finally:
        try:
            os.remove(tmp_file_path)
        except Exception:
            pass

    return jsonify({
        'output': output,
        'exitCode': exit_code
    })


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
