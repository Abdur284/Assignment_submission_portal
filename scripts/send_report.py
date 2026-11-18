
import json
import os
import sys
import urllib.request
import urllib.error
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path

XML_FILE = Path("test-results.xml")

REPORT_URL = os.environ.get("REPORT_URL")
REPORT_TOKEN = os.environ.get("REPORT_TOKEN")

if not REPORT_URL or not REPORT_TOKEN:
    print("ERROR: REPORT_URL or REPORT_TOKEN is missing.")
    sys.exit(1)

if not XML_FILE.exists():
    print("ERROR: Pytest XML report was not generated.")
    sys.exit(1)

root = ET.parse(XML_FILE).getroot()

test_cases = root.findall(".//testcase")

tests = []

for case in test_cases:
    failure = case.find("failure")
    error = case.find("error")
    skipped = case.find("skipped")

    problem = failure if failure is not None else error

    if problem is not None:
        result = "FAILED"
        failure_message = (
            (problem.get("message") or "")
            + "\n"
            + (problem.text or "")
        ).strip()
    elif skipped is not None:
        result = "SKIPPED"
        failure_message = skipped.get("message") or ""
    else:
        result = "PASSED"
        failure_message = ""

    tests.append({
        "name": case.get("classname", "") + "::" + case.get("name", ""),
        "result": result,
        "failure_message": failure_message
    })

# Include collection errors if pytest could not collect tests.
if not tests:
    for suite in root.iter("testsuite"):
        errors = int(suite.get("errors", "0"))
        if errors:
            tests.append({
                "name": "pytest-collection",
                "result": "FAILED",
                "failure_message": "Pytest encountered an error before test execution."
            })
            break

total = len(tests)
passed = sum(t["result"] == "PASSED" for t in tests)
failed = sum(t["result"] == "FAILED" for t in tests)
skipped_count = sum(t["result"] == "SKIPPED" for t in tests)

report = {
    "repository": os.environ.get("GITHUB_REPOSITORY", ""),
    "branch": os.environ.get("GITHUB_REF_NAME", ""),
    "commit_sha": os.environ.get("GITHUB_SHA", ""),
    "pipeline_run_id": os.environ.get("GITHUB_RUN_ID", ""),
    "timestamp": datetime.now(timezone.utc).isoformat(),
    "tests": tests,
    "summary": {
        "total": total,
        "passed": passed,
        "failed": failed,
        "skipped": skipped_count,
        "status": "FAILED" if failed else "PASSED"
    }
}

payload = json.dumps(report).encode("utf-8")

request = urllib.request.Request(
    REPORT_URL,
    data=payload,
    headers={
        "Content-Type": "application/json",
        "X-Report-Token": REPORT_TOKEN
    },
    method="POST"
)

try:
    with urllib.request.urlopen(request, timeout=30) as response:
        print("Report receiver response:", response.status)
        print(response.read().decode("utf-8"))
except urllib.error.HTTPError as error:
    print("HTTP error:", error.code, error.read().decode("utf-8"))
    sys.exit(1)
except urllib.error.URLError as error:
    print("Could not connect to report receiver:", error)
    sys.exit(1)

print("Test report sent successfully.")
print(json.dumps(report, indent=4))
