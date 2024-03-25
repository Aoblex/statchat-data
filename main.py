import os
import json
import logging
import argparse

from prompt_templates import (
    QuestionTemplate,
    AnswerTemplate,
)
from text_splitter import Splitter
from models import QAModel
from utils import (
    save_json,
)



def main(prompt_topic, data_file_name, max_splits, start_split):
    
    logging.basicConfig(
        level=logging.INFO,
        format=f"%(asctime)s - {prompt_topic} - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    splitter = Splitter()
    splits = splitter.get_splits(f"data/{data_file_name}.md")
    logging.info(f"{len(splits)} splits found in data/{data_file_name}.md")

    question_template = QuestionTemplate(prompt_topic)
    answer_template = AnswerTemplate(prompt_topic)
    qa_model = QAModel()
    
    question_chain = question_template.prompt_template | qa_model.model | question_template.output_parser

    question_directory = os.path.join("saves", data_file_name, "questions")
    answer_directory = os.path.join("saves", data_file_name, "answers")

    os.makedirs(question_directory, exist_ok=True)
    os.makedirs(answer_directory, exist_ok=True)

    if max_splits is None:
        max_splits = len(splits)
    if start_split is None:
        start_split = 1

    logging.info(f"Generating questions and answers for splits {start_split} to {start_split+max_splits}...")

    for i, split in enumerate(splits[start_split-1:start_split-1+max_splits], start_split):
        content = split.page_content
        answer_chain = answer_template.get_prompt_with_context(context=content) | qa_model.model | answer_template.output_parser

        # Generate questions
        question_path = os.path.join(question_directory, f"split_{i}.json")
        if os.path.exists(question_path):
            logging.info(f"Skipping {question_path} as it already exists.")
            with open(question_path, "r") as f:
                question_response = json.load(f)
        else:
            while True:
                try:
                    question_response = question_chain.invoke(input=content)
                    question_response["上下文"] = content
                    break
                except:
                    logging.error(f"Error in question_chain.invoke for {question_path}. Retrying...")
                    continue
            save_json(question_path, question_response)

        # Generate answers
        answer_path = os.path.join(answer_directory, f"split_{i}.json")
        if os.path.exists(answer_path):
            logging.info(f"Skipping {answer_path} as it already exists.")
        else:
            questions = question_response.get("问题列表",[])
            content = question_response.get("上下文","")
            answers = []
            for question in questions:
                while True:
                    try:
                        answer_response = answer_chain.invoke(input=question)
                        answer_response["问题"] = question
                        answer_response["上下文"] = content
                        answers.append(answer_response)
                        break
                    except:
                        logging.error(f"Error in answer_chain.invoke for {answer_path}. Retrying...")
                        continue
            save_json(answer_path, answers)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()    
    parser.add_argument("--prompt_topic", type=str, required=True,
                        choices=["数理统计", "统计学", "深度学习", "机器学习"],
                        help="The topic of the prompt.")
    parser.add_argument("--data_file_name", type=str, required=True,
                        choices=["mathematical_statistics", "statistics", "deeplearning", "machine_learning"],
                        help="The name of the data file.")    
    parser.add_argument("--max_splits", type=int, required=False,
                        help="The maximum number of splits to process.")
    parser.add_argument("--start_split", type=int, required=False,
                        help="The starting split number.")
    args = parser.parse_args()
    main(args.prompt_topic, args.data_file_name, args.max_splits, args.start_split)
