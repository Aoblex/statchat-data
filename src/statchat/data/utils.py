from ..logging import get_logger
import json
import os
import re

logger = get_logger(__name__)

def keep_split(split: dict) -> bool:
    return True

    if re.search(r"[0-9] *- *[0-9]", split["page_content"]) is not None:
        return False
    
    metadata = split.get("metadata", {})
    for value in metadata.values():
        if "练习题" in value:
            return False
        if re.search(r"((例题?)|(表格?)) *[0-9]+([\.-][0-9]+){1,}", value) is not None:
            return False

    return True

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

def export_qa_datasets(input_dir: str, output_dir: str) -> None:
    file_names = os.listdir(input_dir)
    output_path = os.path.join(output_dir, "statchat_qa.json")

    fine_tuning_data = []

    for file_name in file_names:
        with open(os.path.join(input_dir, file_name), "r") as f:
            data = json.load(f)
        
        for item in data:
            questions = item['questions']
            answers = item['answers']
            for question, answer in zip(questions, answers):
                fine_tuning_data.append({
                    "prompt": question,
                    "query": "",
                    "response": answer,
                    "history": [],
                })

    os.makedirs(output_dir, exist_ok=True)
    with open(output_path, "w") as f:
        json.dump(fine_tuning_data, f, indent=4, ensure_ascii=False)
    
    logger.info(f"Exported {len(fine_tuning_data)} QA pairs to {output_path}")