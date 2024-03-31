import json
import logging
import re
import markdown

logger = logging.getLogger(__name__)

def save_json(file_path, py_obj):
    with open(file_path, "w") as json_file:
        json.dump(py_obj, json_file, ensure_ascii=False, indent=4)
    logger.info(f"Response saved to {file_path}")

escape_dict = {
    "\t": "\\t",
    "\r": "\\r",
    "\x07": "\\a",  # ASCII 07
    "\x08": "\\b",  # ASCII 08
    "\x0b": "\\v",  # ASCII 11
    "\x0c": "\\f",  # ASCII 12
    "\\\\":"\\",
}

def unescape_string(s: str):
    for k, v in escape_dict.items():
        s = s.replace(k, v)
    return s

def is_valid_markdown(text: str):
    try:
        markdown.markdown(text)
        return True
    except:
        return False

def is_good_text(text):

    # Not null
    if not text:
        return False

    # Can be parsed to markdown
    if not is_valid_markdown(text):
        return False    

    # No bad patterns
    bad_patterns_raw_text = [

        r"[0-9]+\.[0-9]+",
        r"(给定的)|(这个)|(上述)",
        r"/(https?:\/\/)?(([0-9a-z.]+\.[a-z]+)|(([0-9]{1,3}\.){3}[0-9]{1,3}))(:[0-9]+)?(\/[0-9a-z%/.\-_]*)?(\?[0-9a-z=&%_\-]*)?(\#[0-9a-z=&%_\-]*)?/ig",
        r"(\\boldsymbol\{){3,}",
    ]
    bad_patterns = [re.compile(pattern) for pattern in bad_patterns_raw_text]
    return all(not pattern.search(text) for pattern in bad_patterns)

def remove_markdown_url(text):
    return re.sub(r"\[.*?\]\(.*?\)", "", text)