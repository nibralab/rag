import json
import os
import sys

from dotenv import load_dotenv
from flask import Flask, request
import datetime
from humanfriendly.text import random_string

app = Flask(__name__)

load_dotenv()


@app.route('/stop', methods=['GET'])
def stop():
    print("Stopping server...")
    sys.exit(0)


@app.route('/status/<task_id>', methods=['GET'])
def get_status(task_id: str):
    """
    Get the status of a task
    """

    # If there is no file for this task_id, return HTTP 404
    if not os.path.exists(os.path.join('db', task_id + '.json')):
        return {
            'error': f'No such task: {task_id}'
        }, 404

    # Load the file
    with open(os.path.join('db/tasks', task_id + '.json')) as f:
        data = json.load(f)

        # If the task is not finished, return HTTP 202
        if not data['done']:
            return data, 202

        # If the task is finished, remove the file and return HTTP 200
        os.remove(os.path.join('db/tasks', task_id + '.json'))
        return data, 200


@app.route('/<client>', methods=['POST'])
def serve_client(client: str):
    config, custom = prepare_configuration_for_client(client)

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

    # Generate a unique filesafe task_id
    task_id = random_string(8)

    # Call the function with the parameters
    options['task_id'] = task_id

    # Create the task file
    with open(os.path.join('db/tasks', task_id + '.json'), 'w') as f:
        json.dump({
            'done': False,
            'task_id': task_id,
            "started": datetime.datetime.now().isoformat()
        }, f)

    custom.Workflow().call(step, **params, options=options)

    # Return HTTP 202 Accepted status code
    return {
        "message": "Generation process started",
        "task_id": task_id,
    }, 202


def prepare_configuration_for_client(client):
    CUSTOM_DIR = os.path.join('prototypes', client)
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
    return config, custom


if __name__ == '__main__':
    # Get debug options from command line
    debug = False
    if len(sys.argv) > 1 and sys.argv[1] == '--debug':
        debug = True

    app.run(host='localhost', port=5000, debug=debug)
