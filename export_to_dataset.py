#!/data/anaconda3/envs/llama_factory/bin/python

import argparse
import json
import os
import logging

from utils import save_json

logging.basicConfig(level=logging.INFO)

logger = logging.getLogger(__name__)

def generate_dataset(data_file_name):
    dataset_directory = os.path.join("saves", data_file_name, "answers")
    qa_filenames = os.listdir(dataset_directory)
    dataset = []
    for qa_filename in qa_filenames:
        with open(os.path.join(dataset_directory, qa_filename), "r") as json_file:
            qa_list = json.load(json_file)
            for qa in qa_list:
                question = qa.get("问题","")
                answer = qa.get("回答","")
                if question and answer:
                    dataset.append(
                        {
                            "prompt": question,
                            "query": "",
                            "response": answer,
                            "history": [],
                        }
                    )
    os.makedirs("datasets", exist_ok=True)
    save_json(f"datasets/{data_file_name}_dataset.json", dataset)
    logger.info(f"Generated dataset for {data_file_name} successfully. (Total: {len(dataset)} samples)")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--data_file_name", type=str, required=True,
                        choices=["mathematical_statistics", "statistics", "deeplearning", "machine_learning"],
                        help="The name of the data file.")   
    args = parser.parse_args()
    generate_dataset(args.data_file_name)
