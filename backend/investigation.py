# investigation.py - the "detective".
# It runs the Verilog simulation, reads the output lines, and reports any test that failed.

import subprocess          # lets Python run other programs (here: iverilog and vvp)
from pathlib import Path   # a safe way to build file paths

# Work out where the project folders are, based on where this file lives.
ROOT = Path(__file__).resolve().parent.parent   # the ghost-signals folder
SIM_DIR = ROOT / "hardware_sim"                 # holds alu.v and alu_tb.v
WORK_DIR = ROOT / "workdir"                     # holds generated files


def parse_line(line):
    """Turn one 'TEST|NAME|PASS|op=0|a=5|...' line into a Python dictionary."""
    parts = line.strip().split("|")             # cut the line at every | symbol
    fields = {}                                 # an empty dictionary to fill in
    for item in parts[3:]:                      # the key=value items start at position 3
        key, value = item.split("=")            # "a=5" becomes key "a", value "5"
        fields[key] = int(value)                # store the value as a whole number
    return {
        "id": parts[1].strip(),                 # the test name, with extra spaces removed
        "status": parts[2],                     # PASS or FAIL
        "fields": fields,                       # all the numbers
    }


def parse_output(text):
    """Read the whole simulator output and collect the test results."""
    tests = []
    for line in text.splitlines():              # go through the output one line at a time
        if line.startswith("TEST|"):            # only look at lines that are test results
            tests.append(parse_line(line))
    return tests


def run_simulation(design_file):
    """Compile and run the testbench. Returns (output_text, error_message).
    If everything works, error_message is None."""
    WORK_DIR.mkdir(exist_ok=True)                  # make sure workdir exists
    design_file = Path(design_file)
    if not design_file.exists():
        return None, "The design file was not found: " + design_file.name

    out_file = WORK_DIR / "run.vvp"
    compile_cmd = ["iverilog", "-o", str(out_file),
                   str(SIM_DIR / "alu_tb.v"), str(design_file)]
    try:
        compiled = subprocess.run(compile_cmd, capture_output=True, text=True, timeout=30)
        if compiled.returncode != 0:               # the Verilog had a mistake
            return None, "Compile error. Check the Verilog code:\n" + compiled.stderr
        ran = subprocess.run(["vvp", str(out_file)],
                             capture_output=True, text=True, timeout=30)
    except FileNotFoundError:                      # iverilog/vvp not installed or not on PATH
        return None, "Icarus Verilog was not found. Install it and add it to PATH."
    except subprocess.TimeoutExpired:              # the simulation ran too long
        return None, "The simulation took too long and was stopped."
    return ran.stdout, None

OP_NAMES = {0: "ADD", 1: "SUB", 2: "AND", 3: "OR"}
def build_report(tests, design_name):
    """Turn the parsed test results into one structured evidence report."""
    failures = []
    for t in tests:
        if t["status"] != "FAIL":
            continue                                   # skip tests that passed
        f = t["fields"]
        # Find which outputs did not match what was expected.
        mismatches = []
        for name in ("result", "zero", "carry"):
            if f["exp_" + name] != f["act_" + name]:
                mismatches.append({
                    "signal": name,
                    "expected": f["exp_" + name],
                    "actual": f["act_" + name],
                })
        failures.append({
            "test_id": t["id"],
            "operation": OP_NAMES.get(f["op"], "UNKNOWN"),
            "inputs": {"a": f["a"], "b": f["b"]},
            "mismatches": mismatches,
        })
    return {
        "design": design_name,
        "total": len(tests),
        "passed": len(tests) - len(failures),
        "failed": len(failures),
        "verdict": "FAIL" if failures else "PASS",
        "failures": failures,
    }

if __name__ == "__main__":
    import json
    output, error = run_simulation(SIM_DIR / "bug_cases" / "alu_bug_sub_carry.v")
    if error:
        print("ERROR:", error)
    else:
        tests = parse_output(output)
        if not tests:
            print("ERROR: the simulation printed no test results.")
        else:
            print(json.dumps(build_report(tests, "alu_bug_sub_carry.v"), indent=2))