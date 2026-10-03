import os
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

# (item name, platform, percent of budget, why it fits)
SPLITS = {
    "home": [
        ("Sofa covers and cushions", "Amazon", 35, "Gives the living room a fresh look at low cost."),
        ("Lamps and lighting", "IKEA", 25, "Warm light changes the whole mood of the room."),
        ("Curtains and rug", "Flipkart", 25, "Adds colour and makes the room feel complete."),
        ("Wall art and plants", "Amazon", 15, "Small items that finish the makeover."),
    ],
    "party": [
        ("Food and cake", "Swiggy or Zomato", 40, "Food is the main part of any party."),
        ("Decoration and balloons", "Amazon", 25, "Makes the place look festive."),
        ("Venue or hall booking", "OYO", 20, "Gives enough space for all guests."),
        ("Return gifts and games", "Flipkart", 15, "Keeps the guests happy and busy."),
    ],
    "jewelry": [
        ("Main piece (necklace or earrings)", "Myntra", 50, "The main piece decides the full look."),
        ("Matching small pieces", "Flipkart", 25, "Bangles or studs to match the main piece."),
        ("Gift box and packaging", "Amazon", 10, "Makes it ready to gift."),
        ("Keep aside", "Savings", 15, "Extra money for offers or small changes."),
    ],
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

    suggestions = []
    lines = [f"Plan for {PLANNERS[planner]} with budget Rs {round(budget)}."]
    if needs:
        lines.append(f"Your needs: {needs}")
    if occasion:
        lines.append(f"Occasion: {occasion}")
    lines.append("")

    for number, (name, platform, percent, why) in enumerate(SPLITS[planner], 1):
        amount = round(budget * percent / 100)
        suggestions.append({"name": name, "estimated_budget": amount})
        lines.append(f"{number}. {name} - about Rs {amount}")
        lines.append(f"   Buy from: {platform}")
        lines.append(f"   Why: {why}")

    lines.append("")
    lines.append("These are estimates, not live prices or confirmed products.")

    return jsonify({
        "mode": "demo",
        "planner": planner,
        "budget": budget,
        "suggestions": suggestions,
        "recommendation": "\n".join(lines),
    })


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
