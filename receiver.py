
from flask import Flask, request, jsonify
from pathlib import Path
import json
import os
import secrets

app = Flask(__name__)

# Save the report in the same folder as receiver.py
REPORT_FILE = Path(__file__).resolve().parent / "test-report.json"

# Secret token used to authenticate GitHub Actions
REPORT_TOKEN = os.environ.get("REPORT_TOKEN")


@app.route("/health", methods=["GET"])
def health():
    return jsonify({
        "status": "Receiver is running"
    }), 200


@app.route("/report", methods=["POST"])
def receive_report():

    # Check whether the secret is configured
    if not REPORT_TOKEN:
        return jsonify({
            "error": "REPORT_TOKEN is not configured"
        }), 500

    # Authenticate the incoming request
    received_token = request.headers.get("X-Report-Token", "")

    if not secrets.compare_digest(received_token, REPORT_TOKEN):
        return jsonify({
            "error": "Unauthorized"
        }), 401

    # Read JSON report
    report = request.get_json(silent=True)

    if not isinstance(report, dict):
        return jsonify({
            "error": "A valid JSON report is required"
        }), 400

    # Save report to file
    try:
        with REPORT_FILE.open("w", encoding="utf-8") as file:
            json.dump(report, file, indent=4)

        return jsonify({
            "status": "success",
            "message": "Test report received and saved",
            "file": str(REPORT_FILE)
        }), 200

    except OSError as error:
        return jsonify({
            "error": "Could not save report",
            "details": str(error)
        }), 500


if __name__ == "__main__":
    app.run(
        host="127.0.0.1",
        port=5001,
        debug=False
    )
