from ..logging import get_logger
import re

logger = get_logger(__name__)

def get_text_file(file_path: str) -> str:
    logger.info(f"Reading text from {file_path}")
    with open(file_path, "r") as f:
        text = f.read()
    return text

def remove_links(text: str) -> str:
    """Remove links in markdown like [link](url) and other urls"""
    text = re.sub(r"\[.*?\]\(.*?\)", "", text)
    text = re.sub(r"https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&//=]*)", "", text)
    return text