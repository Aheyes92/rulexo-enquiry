import os
from flask import Flask, request, jsonify
from enquiry_orchestrator import run_enquiry_pipeline

app = Flask(__name__)


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"})


@app.route("/enquiry", methods=["POST"])
def enquiry():
    data = request.get_json(force=True)
    if not data:
        return jsonify({"error": "JSON body required"}), 400

    missing = [f for f in ("lead", "source", "client_id") if f not in data]
    if missing:
        return jsonify({"error": f"Missing fields: {missing}"}), 400

    try:
        result = run_enquiry_pipeline(
            raw_data=data["lead"],
            source=data["source"],
            client_id=int(data["client_id"]),
            mode=data.get("mode", "email_only"),
        )
        return jsonify(result)
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 404
    except Exception as exc:
        return jsonify({"error": str(exc)}), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
