import json
import os
import sys

from dotenv import load_dotenv
from flask import Flask, request

load_dotenv()

CUSTOM_DIR = os.path.join('prototypes', os.environ.get('CUSTOM_DIR', 'demo'))

# Base directory
BASE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), CUSTOM_DIR)
sys.path.append(BASE_DIR)

# Load JSON config file
with open(os.path.join(BASE_DIR, 'config.json')) as f:
    config = json.load(f)

# Import the "custom" module from CUSTOM_DIR (e.g. "prototypes/demo/custom") and make it accessible as 'custom'
import importlib
custom = __import__(CUSTOM_DIR.replace('/', '.') + '.custom', fromlist=['Workflow'])
importlib.reload(custom)

app = Flask(__name__)

print("Serving " + os.path.basename(CUSTOM_DIR) + " prototype on http://localhost:5000")
print("Available tasks: " + ', '.join(config['steps'].keys()))

@app.route('/', methods=['POST'])
def main():
    step = request.form['step']

    # Error out, if step is not a key in config['steps']
    if step not in config['steps']:
        return {
            'error': f'Invalid step: {step}'
        }, 400

    options = {}
    for key in config['options']:
        # Take the corresponding value from the form, use default value from config if not set.
        options[key] = request.form.get(key, config['options'][key])

        # Convert 'true' and 'false' to bool
        if options[key] == 'true':
            options[key] = True
        elif options[key] == 'false':
            options[key] = False

    # Get the parameters for the step function
    defined_params = config['steps'][step]['input']

    # Get the parameter values from the form
    params = {}
    for key in defined_params:
        # Take the corresponding value from the form, use None if not set
        params[key] = request.form.get(key, None)

    # Call the function with the parameters
    return custom.Workflow().call(step, **params, options=options)


if __name__ == '__main__':
    app.run(host='localhost', port=5000, debug=True)
