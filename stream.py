from typing import Generator

def stream_file(file_path: str) -> Generator[str, None, None]:
    """
    Reads a file and streams it line by line.

    Args:
        file_paths (str): The filename of the file that needs ot be streamed.

    Yields:
        str: A single line from the file at a time.
    """
    with open(file_path, "r", encoding="utf-8") as f:
        for line in f:
            yield line.strip()
