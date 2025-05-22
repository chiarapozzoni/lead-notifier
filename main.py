from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

SLACK_BOT_TOKEN = os.environ["SLACK_BOT_TOKEN"]
SLACK_CHANNEL = os.environ.get("SLACK_CHANNEL", "#leads")

def get_slack_user_id(email):
    r = requests.get(
        "https://slack.com/api/users.lookupByEmail",
        headers={"Authorization": f"Bearer " + SLACK_BOT_TOKEN},
        params={"email": email}
    )
    data = r.json()
    return data["user"]["id"] if data.get("ok") else None

@app.route("/notify", methods=["POST"])
def notify():
    data = request.json
    email = data.get("owner_email")
    name = data.get("lead_name")
    url = data.get("lead_url")

    slack_id = get_slack_user_id(email)
    if not slack_id:
        return jsonify({"error": "Slack user not found"}), 404

    msg = f"👋 <@{slack_id}> sei ora il proprietario del lead *{name}*\n🔗 {url}"
    r = requests.post(
        "https://slack.com/api/chat.postMessage",
        headers={"Authorization": f"Bearer " + SLACK_BOT_TOKEN},
        json={"channel": SLACK_CHANNEL, "text": msg}
    )
    return jsonify(r.json())

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
