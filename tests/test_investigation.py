# test_investigation.py - automatic checks for the detective.
# pytest runs every function whose name starts with "test_".

import sys
from pathlib import Path

# Let the tests find investigation.py inside the backend folder.
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "backend"))

import investigation as inv

GOOD = ROOT / "hardware_sim" / "alu.v"
BUGGY = ROOT / "hardware_sim" / "bug_cases" / "alu_bug_sub_carry.v"


def test_parse_line_reads_fields():
    # A made-up line in the same format the testbench prints.
    line = "TEST|ADD_BASIC|PASS|op=0|a=5|b=3|exp_result=8|act_result=8|exp_zero=0|act_zero=0|exp_carry=0|act_carry=0"
    t = inv.parse_line(line)
    assert t["id"] == "ADD_BASIC"
    assert t["status"] == "PASS"
    assert t["fields"]["a"] == 5


def test_good_alu_passes_all():
    output, error = inv.run_simulation(GOOD)
    assert error is None
    report = inv.build_report(inv.parse_output(output), "alu.v")
    assert report["verdict"] == "PASS"
    assert report["total"] == 8
    assert report["failed"] == 0


def test_buggy_alu_is_caught():
    output, error = inv.run_simulation(BUGGY)
    assert error is None
    report = inv.build_report(inv.parse_output(output), "alu_bug_sub_carry.v")
    assert report["verdict"] == "FAIL"
    assert report["failed"] == 1
    failure = report["failures"][0]
    assert failure["test_id"] == "SUB_EQUAL"
    assert failure["mismatches"] == [{"signal": "carry", "expected": 0, "actual": 1}]


def test_missing_file_gives_error():
    output, error = inv.run_simulation(ROOT / "nope.v")
    assert output is None
    assert "not found" in error