from ..logging import get_logger
import json
import os
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

def export_dataset(input_path: str, output_dir: str) -> None:
    file_name = os.path.basename(input_path)
    output_path = os.path.join(output_dir, f"{file_name.split('.')[0]}_dataset.json")

    if not os.path.exists(input_path):
        logger.error(f"File not found: {input_path}")
        return

    with open(input_path, "r") as f:
        data = json.load(f)
    
    fine_tuning_data = []
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