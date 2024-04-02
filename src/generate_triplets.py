from statchat.model import QAModel
from statchat.model.parser import CustomParser
from statchat.prompts import CustomTemplate
from langchain.output_parsers import OutputFixingParser
from langchain_core.output_parsers import StrOutputParser
from statchat.logging import get_logger
from typing import List
import argparse
import json
import os
import re
import time

logger = get_logger(__name__)

def generate_triplets(
    input_texts: List[dict],
    knowledge_prompt,
    knowledge_parser,
    qa_model,
    write_frequency,
):
    logger.info(f"Reading generated knowledge from {args.output_path}")
    if os.path.exists(args.output_path):
        with open(args.output_path, "r") as file:
            generated_knowledge = json.load(file)
    else:
        generated_knowledge = []
    generated_inputs_set = set([k["response"] for k in generated_knowledge])
    logger.info(f"Generated knowledge loaded with length: {len(generated_knowledge)}")

    # Construct chain
    chain = knowledge_prompt | qa_model | knowledge_parser

    # Generate knowledge
    logger.info(f"Generating knowledge")
    for i, input_text in enumerate(input_texts):

        text = input_text["response"]
        if text in generated_inputs_set:
            logger.info(f"Skipping generated input:\n{text}\n")
            continue
        knowledge_info = {}

        while True:
            try:
                knowledge_info = chain.invoke({"input": text})
                illegal_escapes_pattern = re.compile(r'(?<!\\)(\\[^"\\\/bfnrtu])')
                knowledge_info = illegal_escapes_pattern.sub(
                    lambda match: '\\' + match.group(1), knowledge_info 
                )
                knowledge_info = json.loads(knowledge_info)
                break
            except json.JSONDecodeError as e:
                logger.error(f"JSON Decode Error: {e}")
                with open("json_error.txt", "w") as file:
                    file.write(knowledge_info)
                exit(0)
            except Exception as e:
                error_string = str(e)
                logger.error(f"Error Message: {error_string}")
                error_summary = error_string.split("-")[0].strip()
                error_code = error_summary.split(":")[1].strip()
                logger.error(f"Error Code: {error_code}")
                if error_code == '429':
                    rate_limit_wait = 30
                    logger.error(f"Rate limit exceeded. Waiting for {rate_limit_wait} seconds...")
                    time.sleep(rate_limit_wait)
                elif error_code == '503':
                    service_wait = 10
                    logger.error(f"Service Unavailable. Waiting for {service_wait} seconds...")
                    time.sleep(service_wait)
                logger.error(f"Retrying...")
                continue
        
        knowledge_info["prompt"] = input_text["prompt"]
        knowledge_info["response"] = input_text["response"]
        logger.info(f"Generated knowledge length: {len(knowledge_info)}")

        generated_knowledge.append(knowledge_info)
        if (len(generated_knowledge) % write_frequency == 0) or (i == len(input_texts) - 1):
            with open(args.output_path, "w") as file:
                json.dump(generated_knowledge, file, ensure_ascii=False, indent=4)
            logger.info(f"Knowledge written to {args.output_path}")

def main(args):
    # Load model 
    qa_model = QAModel(
        openai_api_key_path=args.openai_api_key_path,
        temperature=args.temperature,
        model=args.model,
    )
    logger.info(f"Model {args.model} loaded with temperature {args.temperature}")

    # Load prompt
    prompt_path = "datasets/prompts/know_tuning/extract.txt"
    knowledge_prompt = CustomTemplate.from_file(prompt_path)

    # Load parser
    triplets_parser = CustomParser.triplets_parser
    str_parser = StrOutputParser()
    logger.info(f"Triplets parser loaded")
    triplets_parser = OutputFixingParser.from_llm(
        parser=triplets_parser, llm=qa_model.model,
    )

    # Read contexts and do some preprocessing
    with open(args.input_path, "r") as file:
        input_texts = json.load(file)
    if args.random:
        import random
        random.shuffle(input_texts)
    if args.max_input:
        input_texts = input_texts[:args.max_input]
    logger.info(f"{len(input_texts)} pieces of text will be used to generate knowledge triples.")

    generate_triplets(
        input_texts=input_texts,
        knowledge_prompt=knowledge_prompt,
        knowledge_parser=str_parser,
        # knowledge_parser=triplets_parser,
        qa_model=qa_model.model,
        write_frequency=args.write_frequency,
    )

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input_path", type=str, required=True)
    parser.add_argument("--output_path", type=str, required=True)
    parser.add_argument("--openai_api_key_path", type=str, required=True)
    parser.add_argument("--temperature", type=float, default=0.01)
    parser.add_argument("--model", type=str, default="gpt-3.5-turbo-1106")
    parser.add_argument("--max_input", type=int, default=None)
    parser.add_argument("--write_frequency", type=int, default=10)
    parser.add_argument("--random", action="store_true")

    args = parser.parse_args()

    main(args)