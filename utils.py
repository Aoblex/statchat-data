import json
import logging

logger = logging.getLogger(__name__)

def save_json(file_path, py_obj):
    with open(file_path, "w") as json_file:
        json.dump(py_obj, json_file, ensure_ascii=False, indent=4)
    logger.info(f"Response saved to {file_path}")

# escape_dict = {
#     "\\": "\\\\",
#     "\t": "\\t",
#     "\b": "\\b",
#     "\n": "\\n",
#     "\r": "\\r",
#     "\f": "\\f",
#     "\'": "\\'",
#     "\"": "\\\"",
#     "\0": "\\0",
#     "\a": "\\a",
#     "\v": "\\v",
#     "\x07": "\\x07",  # ASCII 07
#     "\x08": "\\x08",  # ASCII 08
#     "\x09": "\\x09",  # ASCII 09
#     "\x0a": "\\x0a",  # ASCII 10
#     "\x0b": "\\x0b",  # ASCII 11
#     "\x0c": "\\x0c",  # ASCII 12
#     "\x0d": "\\x0d",  # ASCII 13
#     "\x1a": "\\x1a",  # ASCII 26
#     "\x1b": "\\x1b",  # ASCII 27
# }

# def unescape_string(s):
#     for k, v in escape_dict.items():
#         s = s.replace(v, k)
#     return s