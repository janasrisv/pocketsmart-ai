import asyncio
from contextlib import asynccontextmanager
from dataclasses import dataclass, field
from datetime import datetime, timezone

from fastapi import FastAPI, Request
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


# ---------- Main entry point ----------
if __name__ == "__main__":
    import uvicorn

    print("Starting PocketSmart: AI Budget Planner...")
    uvicorn.run(app, host="0.0.0.0", port=8000)
