
# Standard library imports
# (none needed)

# Third-party imports
from flask import Flask, request, jsonify
from RestrictedPython import compile_restricted, safe_globals, safe_builtins
from RestrictedPython.Guards import guarded_iter_unpack_sequence, guarded_unpack_sequence

import numpy
import pandas

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

    try:
        # Compile code in restricted mode
        byte_code = compile_restricted(code, '<string>', 'exec')
        restricted_locals = {}

        # Prepare restricted globals
        import operator
        import matplotlib
        import matplotlib.pyplot as plt
        custom_globals ={
            "__builtins__": safe_builtins,
            "__import__": lambda name, globals=None, locals=None, fromlist=(), level=0: __import__(name),
            "getattr": lambda obj, attr: getattr(obj, attr),
            "_getiter_": iter,
            "_getitem_": operator.getitem,
            "_iter_unpack_sequence_": guarded_iter_unpack_sequence,
            "_unpack_sequence_": guarded_unpack_sequence,
            'numpy': numpy,
            'np': numpy,
            'pd': pandas,
            'pandas': pandas,
            'matplotlib': matplotlib,
            'plt': plt,
        }
        # Add 'pyplot' attribute to 'matplotlib' for 'from matplotlib import pyplot'
        setattr(matplotlib, 'pyplot', plt)
        
        # Patch safe_builtins to allow more builtins for pandas
        # WARNING: This reduces security, but is needed for pandas to work
        allowed_builtins = [
            'abs', 'all', 'any', 'bool', 'callable', 'chr', 'complex', 'dict', 'divmod', 'enumerate',
            'filter', 'float', 'format', 'frozenset', 'getattr', 'hasattr', 'hash', 'hex', 'id', 'int',
            'isinstance', 'issubclass', 'iter', 'len', 'list', 'map', 'max', 'min', 'next', 'object',
            'oct', 'ord', 'pow', 'print', 'range', 'repr', 'reversed', 'round', 'set', 'slice', 'sorted',
            'str', 'sum', 'tuple', 'type', 'zip', 'Exception', 'ValueError', 'AttributeError', 'setattr', 'property'
        ]
        for b in allowed_builtins:
            if b in __builtins__:
                custom_globals['__builtins__'][b] = __builtins__[b]

        # Allow pandas DataFrame and Series attributes
        # (This is a hack: expose all attributes, but you can restrict as needed)
        custom_globals['__builtins__']['getattr'] = getattr
        custom_globals['__builtins__']['setattr'] = setattr
        custom_globals['__builtins__']['property'] = property


        # Patch __import__ to allow numpy/np and pandas/pd imports
        import io
        def custom_import(name, globals=None, locals=None, fromlist=(), level=0):
            # Support 'import numpy', 'import numpy as np', etc.
            if name in ("numpy", "np"):
                return numpy
            if name in ("pandas", "pd"):
                return pandas
            if name == "matplotlib":
                return matplotlib
            if name == "matplotlib.pyplot":
                return plt
            # Support 'from matplotlib import pyplot'
            if name == "pyplot" and globals and globals.get("__name__", "") == "matplotlib":
                return plt
            if name == "plt":
                return plt
            if name == "io":
                return io
            if name == "StringIO" and globals and globals.get("__name__", "") == "io":
                return io.StringIO
            raise ImportError("Only numpy, pandas, matplotlib, and io imports are allowed.")

        custom_builtins = dict(custom_globals.get("__builtins__", {}))
        custom_builtins["__import__"] = custom_import
        custom_globals["__builtins__"] = custom_builtins

        # Patch sys.modules to allow 'import matplotlib.pyplot as plt'
        import sys
        sys_modules_backup = sys.modules.copy()
        sys.modules['matplotlib'] = matplotlib
        sys.modules['matplotlib.pyplot'] = plt
        try:
            exec(byte_code, custom_globals, restricted_locals)
        finally:
            # Restore sys.modules to avoid side effects
            sys.modules.clear()
            sys.modules.update(sys_modules_backup)
        output = restricted_locals.get('output', 'No output')
    except Exception as e:
        import traceback
        output = f"{e}\n{traceback.format_exc()}"
        exit_code = 1

    return jsonify({
        'output': output,
        'exitCode': exit_code
    })


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
