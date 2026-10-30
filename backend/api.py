# api.py - the web API. A web page talks to the detective and ghost through this.

import sys
from pathlib import Path
from fastapi.staticfiles import StaticFiles
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

# Let this file find investigation.py and ghost.py in the same folder.
sys.path.insert(0, str(Path(__file__).resolve().parent))

import ghost
import investigation as inv

ROOT = Path(__file__).resolve().parent.parent
SIM = ROOT / "hardware_sim"

# The page may only pick from this fixed list. No free-form file paths.
CASES = {
    "good_alu": (SIM / "alu.v", "alu.v"),
    "sub_carry_bug": (SIM / "bug_cases" / "alu_bug_sub_carry.v", "alu_bug_sub_carry.v"),
}

app = FastAPI(title="Ghost Signals")

# Allow a web page on another address to call this API (tighten later).
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])


@app.get("/health")
def health():
    return {"status": "alive"}


@app.get("/cases")
def list_cases():
    return {"cases": list(CASES.keys())}


@app.post("/investigate/{case_id}")
def investigate(case_id: str):
    if case_id not in CASES:
        raise HTTPException(status_code=404, detail="Unknown case: " + case_id)

    path, label = CASES[case_id]

    output, error = inv.run_simulation(path)
    if error:
        raise HTTPException(status_code=500, detail=error)

    report = inv.build_report(inv.parse_output(output), label)
    explanation, ghost_error = ghost.ask_ghost(report)

    return {
        "report": report,
        "ghost": explanation,
        "ghost_error": ghost_error,
    }

# Serve the web page from the frontend folder (must stay last).
app.mount("/", StaticFiles(directory=ROOT / "frontend", html=True), name="frontend")