import argparse
import json
import os
import logging
import re

from utils import (
    save_json,
    is_good_text,
    unescape_string,
)

logging.basicConfig(level=logging.INFO)

logger = logging.getLogger(__name__)


def generate_dataset(output_dir, data_file_name, do_preprocess):
    dataset_directory = os.path.join("saves", data_file_name, "answers")
    qa_filenames = os.listdir(dataset_directory)
    dataset = []
    for qa_filename in qa_filenames:
        with open(os.path.join(dataset_directory, qa_filename), "r") as json_file:
            qa_list = json.load(json_file)
            for qa in qa_list:
                question = unescape_string(qa.get("问题",""))
                answer = unescape_string(qa.get("回答",""))

                if do_preprocess and ((not is_good_text(question)) \
                                  or (not is_good_text(answer))):
                    continue
                dataset.append(
                    {
                        "prompt": question,
                        "query": "",
                        "response": answer,
                        "history": [],
                    }
                )

    os.makedirs(output_dir, exist_ok=True)
    save_json(f"{output_dir}/{data_file_name}_dataset.json", dataset)
    logger.info(f"Generated dataset for {data_file_name} successfully. (Total: {len(dataset)} samples)")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--data_file_name", type=str, required=True,
                        choices=["mathematical_statistics", "statistics", "deeplearning", "machine_learning"],
                        help="The name of the data file.")   
    parser.add_argument("--output_dir", type=str, default="datasets",
                        help="The output directory for the generated dataset.")
    parser.add_argument("--do_preprocess", action="store_true",
                        help="Whether to preprocess the data before generating the dataset.")
    args = parser.parse_args()
    generate_dataset(args.output_dir, args.data_file_name, args.do_preprocess)
