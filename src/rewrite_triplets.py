from statchat.model import QAModel
from statchat.prompts import CustomTemplate
from langchain_core.output_parsers import StrOutputParser
from statchat.logging import get_logger
from typing import List, TypedDict
import argparse
import numpy as np
import json
import os
import re
import time

logger = get_logger(__name__)

class Triplet(TypedDict):
    prompt: str
    response: str
    triplets: List[dict]

class RewrittenTriplet(TypedDict):
    prompt: str
    response: str
    triplets: List[dict]
    triplets_ic: List[dict]
    triplets_nf: List[dict]
    triplets_il: List[dict]
    rewritten_triplets: str
    rewritten_triplets_ic: str
    rewritten_triplets_nf: str
    rewritten_triplets_il: str

def make_incomplete(input_triplet: RewrittenTriplet) -> RewrittenTriplet:
    logger.info(f"Making incomplete: {input_triplet['triplets']}")
    incomplete_triplet = input_triplet.copy()
    num_elements_to_extract = int(len(input_triplet["triplets"]) * 0.5)
    random_indices = np.random.choice(
        len(input_triplet["triplets"]),
        size=num_elements_to_extract,
        replace=False)
    incomplete_triplet["triplets_ic"] = [input_triplet["triplets"][i] for i in sorted(random_indices)]
    return incomplete_triplet

def make_nonfactual(
    input_triplet: RewrittenTriplet,
    nonfactual_chain,
) -> RewrittenTriplet:
    logger.info(f"Making non-factual: {input_triplet['triplets']}")
    nonfactual_triplet = input_triplet.copy()
    triplet_str = json.dumps({"triplets": input_triplet["triplets"]})
    revise_chain = nonfactual_chain
    while True:
        try:
            logger.info(f"Revising non-factual...")
            revised_triplet = revise_chain.invoke({"input": triplet_str})
            illegal_escapes_pattern = re.compile(r'(?<!\\)(\\[^"\\\/bfnrtu])')
            revised_triplet = illegal_escapes_pattern.sub(
                lambda match: '\\' + match.group(1), revised_triplet 
            )
            revised_triplet = json.loads(revised_triplet)
            logger.info(f"Revised triplets : {revised_triplet['triplets']}")
            break
        except json.JSONDecodeError as e:
            logger.error(f"JSON Decode Error: {e}")
            with open("json_error_revise.txt", "w") as file:
                file.write(revised_triplet)
            exit(0)
        except Exception as e:
            error_string = str(e)
            logger.error(f"Error Message: {error_string}")
            logger.error(f"Retrying...")
            continue
    nonfactual_triplet["triplets_nf"] = revised_triplet["triplets"]
    return nonfactual_triplet

def make_illogical(input_triplet: RewrittenTriplet) -> RewrittenTriplet:
    logger.info(f"Making illogical: {input_triplet['triplets']}")
    illogical_triplet = input_triplet.copy()
    illogical_triplet["triplets_il"] = input_triplet["triplets"]
    np.random.shuffle(illogical_triplet["triplets_il"])
    return illogical_triplet

def rewrite_triplet(
    rewrite_chain,
    triplet_str,
) -> str:
    logger.info(f"Rewriting triplet: {triplet_str[:50]}...")
    while True:
        try:
            rewritten_triplet = rewrite_chain.invoke({"input": triplet_str})
            break
        except Exception as e:
            error_string = str(e)
            logger.error(f"Error Message: {error_string}")
            logger.error(f"Retrying...")
            continue
    return rewritten_triplet

def negative_sampling(
    output_path,
    stable_temperature,
    unstable_temperature,
    max_input,
    rewrite_prompt,
    revise_prompt,
):
    logger.info(f"Reading sampled triplets from {output_path}")
    all_triplets: List[RewrittenTriplet]
    if os.path.exists(output_path):
        with open(output_path, "r") as file:
            all_triplets = json.load(file)
    else:
        all_triplets = []

    logger.info(f"{len(all_triplets)} knowledge triples will used to perform negative sampling.")
    
    # Build Model
    unstable_model = QAModel(temperature=unstable_temperature)
    stable_model = QAModel(temperature=stable_temperature)

    # Construct chain
    unstable_rewrite_chain = rewrite_prompt | unstable_model.model | StrOutputParser()
    stable_rewrite_chain = rewrite_prompt | stable_model.model | StrOutputParser()
    nonfactual_chain = revise_prompt | unstable_model.model | StrOutputParser()

    # Rewrite
    logger.info(f"Rewritting")
    for i, all_triplet in enumerate(all_triplets):

        if all_triplet.get("rewritten_triplets", None) is None:
            triplet_str = json.dumps({"triplets": all_triplet["triplets"]}, ensure_ascii=False, indent=4)
            all_triplets[i]["rewritten_triplets"] = rewrite_triplet(stable_rewrite_chain, triplet_str)
            with open(output_path, "w") as file:
                json.dump(all_triplets, file, indent=4, ensure_ascii=False)
            logger.info(f"Rewritten {i+1}th triplet")
        
        if all_triplet.get("rewritten_triplets_ic", None) is None:
            incomplete_triplet = make_incomplete(all_triplet)
            triplet_str = json.dumps({"triplets": incomplete_triplet["triplets_ic"]}, ensure_ascii=False, indent=4)
            all_triplets[i]["triplets_ic"] = incomplete_triplet["triplets_ic"]
            all_triplets[i]["rewritten_triplets_ic"] = rewrite_triplet(unstable_rewrite_chain, triplet_str)
            with open(output_path, "w") as file:
                json.dump(all_triplets, file, indent=4, ensure_ascii=False)
            logger.info(f"Rewritten {i+1}th incomplete triplet")
        
        if all_triplet.get("rewritten_triplets_nf", None) is None:
            nonfactual_triplet = make_nonfactual(all_triplet, nonfactual_chain)
            triplet_str = json.dumps({"triplets": nonfactual_triplet["triplets_nf"]}, ensure_ascii=False, indent=4)
            all_triplets[i]["triplets_nf"] = nonfactual_triplet["triplets_nf"]
            all_triplets[i]["rewritten_triplets_nf"] = rewrite_triplet(unstable_rewrite_chain, triplet_str)
            with open(output_path, "w") as file:
                json.dump(all_triplets, file, indent=4, ensure_ascii=False)       
            logger.info(f"Rewritten {i+1}th non-factual triplet")

        if all_triplet.get("rewritten_triplets_il", None) is None:
            illogical_triplet = make_illogical(all_triplet)
            triplet_str = json.dumps({"triplets": illogical_triplet["triplets_il"]}, ensure_ascii=False, indent=4)
            all_triplets[i]["triplets_il"] = illogical_triplet["triplets_il"]
            all_triplets[i]["rewritten_triplets_il"] = rewrite_triplet(unstable_rewrite_chain, triplet_str)
            with open(output_path, "w") as file:
                json.dump(all_triplets, file, indent=4, ensure_ascii=False)
            logger.info(f"Rewritten {i+1}th illogical triplet")

def main(args):
    # Load prompt
    rewrite_prompt_path = "datasets/prompts/know_tuning/rewrite.txt"
    rewrite_prompt = CustomTemplate.from_file(rewrite_prompt_path)
    revise_prompt_path = "datasets/prompts/know_tuning/revise.txt"
    revise_prompt = CustomTemplate.from_file(revise_prompt_path)

    negative_sampling(
        output_path=args.output_path,
        stable_temperature=args.stable_temperature,
        unstable_temperature=args.unstable_temperature,
        max_input=args.max_input,
        rewrite_prompt=rewrite_prompt,
        revise_prompt=revise_prompt,
    )

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output_path", type=str, required=True)
    parser.add_argument("--stable_temperature", type=float, default=0.01)
    parser.add_argument("--unstable_temperature", type=float, default=0.01)
    parser.add_argument("--max_input", type=int, default=None)

    args = parser.parse_args()

    main(args)