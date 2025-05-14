class FileNotFoundError(Exception):
    detail = "File not found"

    def __init__(self, filename: str) -> None:
        self.detail = f"File {filename} not found"
