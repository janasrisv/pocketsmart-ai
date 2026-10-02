# PocketSmart AI: Your Smart Budget & Recommendation Assistant

PocketSmart AI is an AI-powered budget planning web app that gives smart,
personalized recommendations for everyday lifestyle needs. It uses
**Gemini 1.5 Flash Pro** to process user inputs (budget, preferences, and
even images) and suggests the best options within your budget.

## Features
- **Home Interior Planner**: furniture, lighting and decor suggestions
  based on room details, quantity and budget
- **Party Planner**: venue, food, decor and entertainment plans based on
  event type, budget and guest count
- **Jewelry Planner**: jewelry matched to your budget, occasion and
  outfit (image upload supported)
- Recommendations inspired by platforms like Amazon, Flipkart, IKEA,
  Swiggy, Zomato and OYO
- Fallback recommendations when AI results are insufficient

## Tech Stack
- **Backend:** Python (Flask)
- **AI:** Google Gemini 1.5 Flash Pro API
- **Frontend:** HTML, CSS, JavaScript (Jinja2 templates)

## Project Structure
- `1-Brainstorming-and-Ideation`
- `2-Requirement-Analysis`
- `3-Project-Design-Phase`
- `Backend`
- `app.py`: main application
- `index.html`: landing page

## How to Run
1. Clone the repo
   git clone https://github.com/janasrisv/pocketsmart-ai.git
2. Install dependencies
   pip install -r requirements.txt
3. Add your Gemini API key in a `.env` file
   GEMINI_API_KEY=your_key_here
4. Run the app
   python app.py

## Team
- janasrisv
- lochinimeena650-cyber
