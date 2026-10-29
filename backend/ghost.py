# ghost.py - the AI ghost.
# Takes the detective's evidence report and asks an AI model to explain
# the bug in plain language. The model only sees the evidence, nothing else.

import json
import os
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI, APIConnectionError, APIStatusError

# Read the secrets from the .env file in the project root.
ROOT = Path(__file__).resolve().parent.parent
load_dotenv(ROOT / ".env")

SYSTEM_PROMPT = (
    "You are a friendly ghost haunting a digital circuit (an ALU). "
    "You receive an evidence report from a detective who ran a simulation. "
    "Explain the bug in plain language for a beginner. "
    "Use ONLY the evidence given. Do not invent facts. "
    "Structure your answer as: 1) What went wrong, 2) Why it matters, "
    "3) Where in the design to look. Keep it under 150 words."
)


def build_messages(report):
    """Turn the report into the chat messages we send to the AI."""
    evidence = json.dumps(report, indent=2)
    return [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": "Evidence report:\n" + evidence},
    ]


def ask_ghost(report):
    """Returns (explanation, error). Exactly one of them is None."""
    # A passing design has nothing to explain, so skip the AI call.
    if report.get("verdict") == "PASS":
        return "No haunting here. Every test passed.", None

    base_url = os.getenv("AI_BASE_URL")
    api_key = os.getenv("AI_API_KEY")
    model = os.getenv("AI_MODEL")

    if not (base_url and api_key and model):
        return None, "AI settings are missing. Fill AI_BASE_URL, AI_API_KEY and AI_MODEL in .env"

    try:
        client = OpenAI(base_url=base_url, api_key=api_key, timeout=60)
        response = client.chat.completions.create(
            model=model,
            messages=build_messages(report),
            max_tokens=1500,
            temperature=0.2,
        )
    except APIStatusError as e:
        code = e.status_code
        if code == 401:
            return None, "The AI service rejected the token (401). Check AI_API_KEY in .env"
        if code == 402:
            return None, "Out of free credits (402). Wait for the monthly reset or add billing."
        if code in (400, 404):
            return None, f"The AI service does not accept the model '{model}' ({code}). Check AI_MODEL."
        if code == 429:
            return None, "Too many requests (429). Wait a minute and try again."
        return None, f"The AI service returned an error ({code})."
    except APIConnectionError:
        return None, "Could not reach the AI service. Check your internet connection."

    text = response.choices[0].message.content
    if not text:
        return None, "The AI returned an empty answer. Try again."
    return text.strip(), None


if __name__ == "__main__":
    # Quick demo: investigate the buggy ALU, then ask the ghost to explain.
    import investigation as inv

    buggy = ROOT / "hardware_sim" / "bug_cases" / "alu_bug_sub_carry.v"
    output, error = inv.run_simulation(buggy)
    if error:
        print("Detective error:", error)
    else:
        report = inv.build_report(inv.parse_output(output), "alu_bug_sub_carry.v")
        explanation, error = ask_ghost(report)
        print(error if error else explanation)