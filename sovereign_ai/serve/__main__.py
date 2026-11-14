import argparse


def main() -> None:
    parser = argparse.ArgumentParser(description="Local ask HTTP UI (127.0.0.1)")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8787)
    args = parser.parse_args()
    try:
        import uvicorn
    except ImportError as e:
        raise SystemExit(
            "Missing serve dependencies. On Deploy: pip install -e '.[serve]'"
        ) from e
    uvicorn.run(
        "sovereign_ai.serve.app:app",
        host=args.host,
        port=args.port,
        reload=False,
    )


if __name__ == "__main__":
    main()