from typing import Generator

def stream_file(file_path: str) -> Generator[str, None, None]:
    """
    Reads a file (by path) and streams it line by line.
    """
    with open(file_path, "r", encoding="utf-8") as f:
        for line in f:
            yield line.strip()
