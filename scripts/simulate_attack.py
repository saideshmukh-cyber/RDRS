"""Safe RDRS detector trigger. Operates only in data/sandbox."""
from pathlib import Path
import os

ROOT=Path(__file__).resolve().parents[1]
SANDBOX=(ROOT/"data"/"sandbox").resolve()
SANDBOX.mkdir(parents=True, exist_ok=True)

# Guardrail: refuse to operate outside the project sandbox.
if "data" not in SANDBOX.parts or SANDBOX.name != "sandbox":
    raise RuntimeError("Refusing to run outside data/sandbox")

for old in SANDBOX.glob("*.txt"):
    old.unlink(missing_ok=True)
for old in SANDBOX.glob("*.locked"):
    old.unlink(missing_ok=True)

files=[]
for i in range(30):
    p=SANDBOX/f"demo_{i:03d}.txt"
    p.write_text("This is harmless disposable test content.\n"*10, encoding="utf-8")
    files.append(p)

for p in files:
    p.write_bytes(os.urandom(20000))
    p.rename(p.with_suffix(".locked"))

print(f"Created a safe simulated burst in {SANDBOX}")
print("No real files outside the sandbox were touched.")
