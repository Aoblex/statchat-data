from statchat.model import QAModel
from statchat.prompts import CustomTemplate
from statchat.model.parser import CustomParser
from statchat.logging import get_logger
from typing import List
import argparse
import json
import os
import time

logger = get_logger(__name__)

def generate_question_and_answer(
    contexts: List[str],
    question_prompt,
    answer_prompt,
    question_parser,
    answer_parser,
    qa_model,
    qa_path,
    write_frequency,
):
    # Read generated questions
    logger.info(f"Reading generated qa_pairs from {qa_path}")
    if os.path.exists(qa_path):
        with open(qa_path, "r") as file:
            generated_qa_pairs = json.load(file)
    else:
        generated_qa_pairs = []
    generated_contexts_set = set([q["context"]["page_content"] for q in generated_qa_pairs])
    logger.info(f"Generated question answer pairs loaded with length: {len(generated_qa_pairs)}")

    # Construct chain
    question_chain = question_prompt | qa_model | question_parser
    answer_chain = answer_prompt | qa_model | answer_parser 

    # Generate questions
    logger.info(f"Generating questions")
    for i, context in enumerate(contexts):

        # Skip if context already generated
        page_content = context["page_content"]
        if page_content in generated_contexts_set:
            logger.info(f"Skipping generated context:\n{page_content}\n")
            continue
        qa_info = {}

        # Generate question
        while True:
            try:
                qa_info["questions"] = question_chain.invoke({"context": page_content})["questions"]
                break
            except Exception as e:
                error_string = str(e)
                error_summary = error_string.split("-")[0].strip()
                error_code = error_summary.split(":")[1].strip()
                logger.error(f"Error Code: {error_code}")
                if error_code == '429':
                    logger.error(f"Rate limit exceeded. Waiting for 30 seconds...")
                    time.sleep(30)
                logger.error(f"Retrying...")
                continue
        
        qa_info["question_prompt"] = question_prompt.template
        qa_info["answer_prompt"] = answer_prompt.template
        qa_info["context"] = context
        logger.info(f"Generated question length: {len(qa_info['questions'])}")

        # Generate answers
        answers = []
        len_answers = len(qa_info["questions"])
        for j, question in enumerate(qa_info["questions"], 1):
            logger.info(f"[{j}/{len_answers}] Generating answer for question: {question}")

            while True:
                try:
                    answer = answer_chain.invoke({"context": page_content, "question": question})
                    break
                except Exception as e:
                    error_string = str(e)
                    error_summary = error_string.split("-")[0].strip()
                    error_code = error_summary.split(":")[1].strip()
                    logger.error(f"Error Code: {error_code}")
                    if error_code == '429':
                        logger.error(f"Rate limit exceeded. Waiting for 30 seconds...")
                        time.sleep(30)
                    logger.error(f"Retrying...")
                    continue

            answers.append(answer)
            logger.info(f"[{j}/{len_answers}] Answer: {answer}")
        qa_info["answers"] = answers
        logger.info(f"Generated answer length: {len(qa_info['answers'])}")

        # Write to file
        generated_qa_pairs.append(qa_info)
        if (len(generated_qa_pairs) % write_frequency == 0) or (i == len(contexts) - 1):
            with open(qa_path, "w") as file:
                json.dump(generated_qa_pairs, file, ensure_ascii=False, indent=4)
            logger.info(f"Question and answers written to {qa_path}")

def main(args):
    # Load model 
    qa_model = QAModel(
        openai_api_key_path=args.openai_api_key_path,
        temperature=args.temperature,
        model=args.model,
    )
    logger.info(f"Model {args.model} loaded with temperature {args.temperature}")

    # Load prompt
    question_prompt = CustomTemplate.from_file(args.question_prompt_path)
    logger.info(f"Question prompt loaded from {args.question_prompt_path}")
    answer_prompt = CustomTemplate.from_file(args.answer_prompt_path)
    logger.info(f"Answer prompt loaded from {args.answer_prompt_path}")

    # Load parser
    custom_parser = CustomParser()
    question_parser = custom_parser.question_parser
    answer_parser = custom_parser.answer_parser
    logger.info(f"OutputParser loaded")

    # Read contexts and do some preprocessing
    with open(args.context_path, "r") as file:
        contexts = json.load(file)
    if args.random:
        import random
        random.shuffle(contexts)
    if args.max_context:
        contexts = contexts[:args.max_context]
    logger.info(f"{len(contexts)} contexts will be used to generate questions and answers")

    generate_question_and_answer(
        contexts=contexts,
        question_prompt=question_prompt,
        answer_prompt=answer_prompt,
        question_parser=question_parser,
        answer_parser=answer_parser,
        qa_model=qa_model.model,
        qa_path=args.qa_path,
        write_frequency=args.write_frequency,
    )

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--question_prompt_path", type=str, required=True)
    parser.add_argument("--answer_prompt_path", type=str, required=True)
    parser.add_argument("--context_path", type=str, required=True)
    parser.add_argument("--qa_path", type=str, required=True)
    parser.add_argument("--openai_api_key_path", type=str, required=True)
    parser.add_argument("--temperature", type=float, default=0.01)
    parser.add_argument("--model", type=str, default="gpt-3.5-turbo-1106")
    parser.add_argument("--max_context", type=int, default=None)
    parser.add_argument("--write_frequency", type=int, default=10)
    parser.add_argument("--random", action="store_true")

    args = parser.parse_args()

    main(args)