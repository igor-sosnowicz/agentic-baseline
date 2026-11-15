from pathlib import Path


SUPPORTED_EXTENSIONS = {".txt", ".md", ".markdown"}


def read_text_file(path: Path) -> str:
    """
    Read the contents of a TXT or Markdown file.

    Args:
        path: Path to the document.

    Returns:
        Document contents.

    Raises:
        ValueError: If the file format is unsupported.
        FileNotFoundError: If the file does not exist.
    """
    if path.suffix.lower() not in SUPPORTED_EXTENSIONS:
        raise ValueError(f"Unsupported document format: {path.suffix}")

    if not path.is_file():
        raise FileNotFoundError(f"Document not found: {path}")

    return path.read_text(encoding="utf-8")