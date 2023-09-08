import subprocess

from flask import Flask

app = Flask(__name__)


@app.route('/trigger-training', methods=['POST'])
def trigger_training():
    try:
        # Execute the train.py script using subprocess
        subprocess.run(["python", "train.py"], check=True)
        return {"message": "Training triggered successfully"}
    except subprocess.CalledProcessError as e:
        return {"message": f"Error triggering training: {e}"}, 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)
