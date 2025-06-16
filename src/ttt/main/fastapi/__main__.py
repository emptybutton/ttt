from ttt.main.common.uvicorn import run_dev


def main() -> None:
    run_dev("ttt.main.fastapi.asgi:app")


if __name__ == "__main__":
    main()
