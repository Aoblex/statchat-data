import os
import json
from statchat.logging import get_logger
from typing import List, TypedDict

logger = get_logger(__name__)

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

def have_all_keys(triplet: RewrittenTriplet) -> bool:
    keys = ["prompt", "response", "triplets", "triplets_ic", "triplets_nf", "triplets_il", "rewritten_triplets", "rewritten_triplets_ic", "rewritten_triplets_nf", "rewritten_triplets_il"]
    for key in keys:
        if key not in triplet:
            return False
    return True

def export_triplets(input_path: str, output_dir: str) -> None:
    with open(input_path, "r") as f:
        rewritten_triplets: List[RewrittenTriplet] = json.load(f)
    KG_dataset_name = "statchat_KG.json"
    KC_dataset_name = "statchat_KC.json"
    KG_dataset, KC_dataset = [], []
    for i, rewritten_triplet in enumerate(rewritten_triplets, 1):
        if not have_all_keys(rewritten_triplet):
            logger.info(f"{i}th triplet have not generated yet, quitting")
            break
        KG_dataset.append({
            "prompt": rewritten_triplet["prompt"],
            "query": "",
            "response": rewritten_triplet["response"],
            "history": [],
        })
        KG_dataset.append({
            "prompt": "请根据以下的格式要求生成与给定问题相关的知识三元组\n\n            {\n              \"triplets\": [\n                {\n                  \"subject\": \"...\",\n                  \"predicate\": \"...\",\n                  \"object\": \"...\"\n                }\n              ]\n            }\n            \n以下是知识三元组的定义\n\n            主语：在一个三元组中，主语代表着陈述所涉及的主要实体或概念。它类似于信息传达中的焦点。主语通常是在给定知识领域内可以识别的一个独特实体。\n            谓语：三元组中的谓语起到连接主语与宾语的关系或属性的作用。它定义了两者之间的联系或关联的性质。谓语通常是自然语言中的动词或动词短语，但也可以是数据库中的关系术语。\n            宾语：三元组中的宾语是通过谓语与主语相连的实体或概念。它可以被视为由主语发起的关系的目标或终点。宾语可以是一个具体实体、一个值，或者是另一个抽象概念。\n            ",
            "query": f"#问题#:\n{rewritten_triplet['prompt']}\n#知识三元组#:",
            "response": json.dumps({"triplets": rewritten_triplet["triplets"]}, ensure_ascii=False, indent=4),
            "history": [],
        })
        KC_dataset.append({
            "prompt": rewritten_triplet["prompt"],
            "query": "",
            "response": [
                rewritten_triplet["rewritten_triplets"],
                rewritten_triplet["rewritten_triplets_ic"],
            ],
            "history": [],
        })
        KC_dataset.append({
            "prompt": rewritten_triplet["prompt"],
            "query": "",
            "response": [
                rewritten_triplet["rewritten_triplets"],
                rewritten_triplet["rewritten_triplets_il"],
            ],
        })
        KC_dataset.append({
            "prompt": rewritten_triplet["prompt"],
            "query": "",
            "response": [
                rewritten_triplet["rewritten_triplets"],
                rewritten_triplet["rewritten_triplets_nf"],
            ],
        })
    
    with open(os.path.join(output_dir, KG_dataset_name), "w") as f:
        json.dump(
            KG_dataset,
            f, ensure_ascii=False, indent=4)
    logger.info(f"Exported {len(KG_dataset)} triplets to {KG_dataset_name}")
    
    with open(os.path.join(output_dir, KC_dataset_name), "w") as f:
        json.dump(
            KC_dataset,
            f, ensure_ascii=False, indent=4)
    logger.info(f"Exported {len(KC_dataset)} triplets to {KC_dataset_name}")


if __name__ == "__main__":
    export_triplets(
        "datasets/know_tuning/statchat_triplets.json",
        "datasets/fine_tuning_data")