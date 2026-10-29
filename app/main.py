from __future__ import annotations
import argparse
import uvicorn
from app.runtime import get_runtime


def main():
    parser=argparse.ArgumentParser(description="RDRS defensive ransomware-like behavior detector")
    parser.add_argument("--host", default=None)
    parser.add_argument("--port", type=int, default=None)
    parser.add_argument("--no-api", action="store_true", help="Start monitors without starting FastAPI")
    args=parser.parse_args()
    rt=get_runtime(); rt.start()
    if args.no_api:
        import time
        try:
            while True: time.sleep(1)
        except KeyboardInterrupt: rt.stop()
        return
    uvicorn.run("app.api.main:app", host=args.host or rt.settings.host, port=args.port or rt.settings.port, reload=False)

if __name__ == "__main__": main()
