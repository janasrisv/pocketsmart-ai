import asyncio
from contextlib import asynccontextmanager
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

from fastapi import FastAPI, File, Form, Request, UploadFile
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates


# ---------- Session storage ----------
@dataclass
class Session:
    username: str
    last_activity: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )


active_sessions: dict[str, Session] = {}


# ---------- Startup: background cleanup task ----------
async def cleanup_expired_sessions():
    """Background task to clean up expired sessions"""
    while True:
        current_time = datetime.now(timezone.utc)

        # Check for sessions inactive for more than 30 minutes
        expired_sessions = [
            username
            for username, session in active_sessions.items()
            if (current_time - session.last_activity).total_seconds() > 1800
        ]

        # Remove expired sessions
        for username in expired_sessions:
            print(f"Removing expired session for {username}")
            active_sessions.pop(username, None)

        # Wait for 5 minutes before checking again
        await asyncio.sleep(300)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("PocketSmart startup: loading services...")
    task = asyncio.create_task(cleanup_expired_sessions())
    yield
    # Shutdown
    task.cancel()
    print("PocketSmart shutting down...")


# ---------- App setup ----------
app = FastAPI(lifespan=lifespan)
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


@app.get("/")
def home(request: Request):
    return templates.TemplateResponse(request, "index.html")
def render(request: Request, name: str, **ctx):
    return templates.TemplateResponse(request, name, ctx)


@app.get("/go")
def go(category: str = "home", budget: str = ""):
    return RedirectResponse(f"/{category}-planner?budget={budget}")


@app.get("/login")
def login_page(request: Request):
    return render(request, "login.html")


@app.post("/login")
def login_post(username: str = Form(...), password: str = Form(...)):
    return RedirectResponse("/dashboard", status_code=303)


@app.get("/register")
def register_page(request: Request):
    return render(request, "register.html")


@app.post("/register")
def register_post(username: str = Form(...), email: str = Form(...),
                  password: str = Form(...), confirm: str = Form(...)):
    return RedirectResponse("/login", status_code=303)


@app.get("/dashboard")
def dashboard(request: Request):
    return render(request, "dashboard.html")


@app.get("/history")
def history(request: Request):
    return render(request, "history.html")


# ---------- Home planner ----------
@app.get("/home-planner")
def home_planner_page(request: Request, budget: str = ""):
    return render(request, "home_planner.html", budget=budget)


@app.post("/home-planner")
def home_planner_post(request: Request, budget: float = Form(...),
                      lights: int = Form(0), fans: int = Form(0),
                      furniture: int = Form(0), tables: int = Form(0),
                      rooms: list[str] = Form(default=[]), notes: str = Form("")):
    costs = [("LED Bulbs", lights * 150), ("Ceiling Fans", fans * 2500),
             ("Furniture", furniture * 4000), ("Dining Tables", tables * 6000)]
    total = sum(c for _, c in costs)
    if total > budget and total:
        factor = budget / total
        costs = [(n, int(c * factor)) for n, c in costs] 
    where = ", ".join(rooms) or "your home"
    products = [{"name": n, "desc": f"Suggested for {where}", "price": f"₹{c}"}
                for n, c in costs if c]
    result = {"title": "Your Home Budget Plan", "budget": f"₹{budget:.0f}",
              "remaining": f"₹{budget - sum(c for _, c in costs):.0f}",
              "products": products, "image": None}
    return render(request, "home_planner.html", budget=int(budget), result=result)


# ---------- Party planner ----------
@app.get("/party-planner")
def party_planner_page(request: Request, budget: str = ""):
    return render(request, "party_planner.html", budget=budget)


@app.post("/party-planner")
def party_planner_post(request: Request, budget: float = Form(...),
                       guests: int = Form(...), party_type: str = Form(...),
                       venue: str = Form(...), needs: list[str] = Form(default=[]),
                       notes: str = Form("")):
    chosen = ["Venue"] + needs
    share = budget / len(chosen)
    products = [{"name": n, "desc": f"{party_type} at {venue} for {guests} guests",
                 "price": f"₹{share:.0f}"} for n in chosen]
    result = {"title": "Your Party Budget Plan", "budget": f"₹{budget:.0f}",
              "remaining": "₹0", "products": products, "image": None}
    return render(request, "party_planner.html", budget=int(budget), result=result)


# ---------- Jewelry planner ----------
@app.get("/jewelry-planner")
def jewelry_planner_page(request: Request, budget: str = ""):
    return render(request, "jewelry_planner.html", budget=budget)


@app.post("/jewelry-planner")
async def jewelry_planner_post(request: Request, budget: float = Form(...),
                               occasion: str = Form(...), style: str = Form(""),
                               outfit: UploadFile = File(None)):
    filename = None
    if outfit and outfit.filename:
        folder = Path("static/uploads")
        folder.mkdir(parents=True, exist_ok=True)
        filename = f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{Path(outfit.filename).name}"
        (folder / filename).write_bytes(await outfit.read())
    parts = [("Bracelet", 0.15), ("Ring", 0.20), ("Watch", 0.40)]
    products = [{"name": n, "desc": f"For {occasion}. {style}".strip(),
                 "price": f"₹{budget * p:.0f}"} for n, p in parts]
    result = {"title": "Your Jewelry Recommendations", "budget": f"₹{budget:.0f}",
              "remaining": f"₹{budget * 0.25:.0f}", "products": products,
              "image": filename}
    return render(request, "jewelry_planner.html", budget=int(budget), result=result)

# ---------- Main entry point ----------
if __name__ == "__main__":
    import uvicorn

    print("Starting PocketSmart: AI Budget Planner...")
    uvicorn.run(app, host="0.0.0.0", port=8000)