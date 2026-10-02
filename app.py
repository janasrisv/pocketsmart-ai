import os
import requests
from flask import Flask, jsonify, request

app = Flask(__name__)


@app.after_request
def allow_github_pages(response):
    response.headers["Access-Control-Allow-Origin"] = (
        "https://janasrisv.github.io"
    )
    response.headers["Access-Control-Allow-Headers"] = "Content-Type"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
    return response


PLANNERS = {
    "home": "home decor and interior planning",
    "party": "party and event planning",
    "jewelry": "jewelry shopping for a special occasion",
}


@app.get("/")
def home():
    return "PocketSmart AI backend is running."


@app.get("/health")
def health():
    return jsonify({"status": "ok"})


def make_recommendation(planner):
    data = request.get_json(silent=True) or {}

    try:
        budget = float(data.get("budget", 0))
    except (TypeError, ValueError):
        return jsonify({"error": "Enter a valid budget."}), 400

    if budget <= 0:
        return jsonify({"error": "Budget must be greater than zero."}), 400

    needs = str(data.get("needs", "")).strip()[:500]
    occasion = str(data.get("occasion", "")).strip()[:200]

    api_key = os.getenv("GEMINI_API_KEY")
    model = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

    if not api_key:
        return jsonify({
            "mode": "demo",
            "message": "Add a Gemini API key to enable AI recommendations.",
            "planner": planner,
            "budget": budget,
            "suggestions": [
                {"name": "Essentials", "estimated_budget": round(budget * 0.5)},
                {"name": "Useful extras", "estimated_budget": round(budget * 0.3)},
                {"name": "Keep aside", "estimated_budget": round(budget * 0.2)},
            ],
        })

    prompt = f"""
Create 3 practical suggestions for {PLANNERS[planner]}.
User budget: {budget}
Needs: {needs}
Currency: Indian Rupees (₹). Use ₹ for all amounts.
Occasion: {occasion}
Return a short, clear answer. Split the budget across the suggestions.
These are estimates, not live prices or confirmed products.
"""

    url = (
        "https://generativelanguage.googleapis.com/v1beta/models/"
        f"{model}:generateContent"
    )

    try:
        response = requests.post(
            url,
            headers={"x-goog-api-key": api_key},
            json={"contents": [{"parts": [{"text": prompt}]}]},
            timeout=30,
        )
        response.raise_for_status()

        result = response.json()
        answer = result["candidates"][0]["content"]["parts"][0]["text"]

        return jsonify({
            "mode": "gemini",
            "planner": planner,
            "budget": budget,
            "recommendation": answer,
        })

    except (requests.RequestException, KeyError, IndexError, ValueError):
        return jsonify({
            "error": "Gemini request failed. Check the API key and model settings."
        }), 502


@app.post("/generate-home")
def generate_home():
    return make_recommendation("home")


@app.post("/generate-party")
def generate_party():
    return make_recommendation("party")


@app.post("/generate-jewelry")
def generate_jewelry():
    return make_recommendation("jewelry")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)))
