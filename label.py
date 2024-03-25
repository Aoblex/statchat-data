import argparse
import json
import os

import bisect

LABEL_LEVELS = ['0', '1', '2']

def binary_search(lst, x):
    i = bisect.bisect_left(lst, x)
    if i != len(lst) and lst[i] == x:
        return i
    else:
        return -1

def show_qa(data_item):
    print("-" * 80, '\n')
    print(f"问题：{data_item['prompt']}\n")
    print(f"回答：{data_item['response']}\n")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--file_name", help="The JSON file to label",
                        choices=["deeplearning", "machine_learning", "mathematical_statistics", "statistics"],)
    parser.add_argument("--file_dir", help="The directory of the JSON file to label",
                        choices=["datasets"])
    parser.add_argument("--output_dir", help="The directory to save the labeled JSON file",
                        choices=["labeled_datasets"])
    args = parser.parse_args()

    file_name = f"{args.file_name}_dataset.json"
    file_dir = args.file_dir
    output_dir = args.output_dir
    file_path = os.path.join(file_dir, file_name)
    output_path = os.path.join(output_dir, file_name)
    os.makedirs(output_dir, exist_ok=True)

    # Original data
    if os.path.exists(file_path):
        with open(file_path, 'r') as f:
            data = json.load(f)
    else:
        data = []   

    # Labeled data
    if os.path.exists(output_path):
        with open(output_path, 'r') as f:
            labeled_data = json.load(f)
    else:
        labeled_data = []

    # Check for updates
    labeled_data = [item for item in labeled_data if item.get("label", None) is not None] # Keep labeled data
    labeled_data.sort(key=lambda x: x['prompt'])
    labeled_prompts = [item['prompt'] for item in labeled_data]
    labeled_prompt_set = set(labeled_prompts)

    # Keep labels
    for i in range(len(data)):
        if data[i]['prompt'] in labeled_prompt_set:
            label_index = binary_search(labeled_prompts, data[i]['prompt'])
            data[i]['label'] = labeled_data[label_index]['label']

    i = 0
    while i < len(data):

        show_qa(data[i])

        print(f">>> Labeling progress: \033[36m{i-1}/{len(data)}\033[0m")

        zero_counts = len([item for item in data if item.get("label", None) == 0])
        one_counts = len([item for item in data if item.get("label", None) == 1])
        two_counts = len([item for item in data if item.get("label", None) == 2])

        print(f">>> Labeling statistics: \033[31m0: {zero_counts}, \033[33m1: {one_counts}, \033[32m2: {two_counts}\033[0m")

        if data[i].get("label", None) is not None:
            print("Already labeled, skipping.")
            i = i + 1
            continue


        while True:

            label = input(f">>> Enter label {LABEL_LEVELS}, 'u' to undo last label, 'q' to quit: ")
            if label in LABEL_LEVELS:
                data[i]['label'] = int(label)
                break
            elif label == 'u':
                if i == 0:
                    print("Cannot undo first label.")
                    continue
                i = i - 1
                if 'label' in data[i]:
                    del data[i]['label']
                print(f"Removed label for:\n{data[i]}")
            elif label == 'q':
                with open(output_path, 'w') as f:
                    json.dump(data, f, indent=4, ensure_ascii=False)
                return
            else:
                print(f"Invalid input. Please enter {LABEL_LEVELS}, u, or q.")
        i = i + 1

if __name__ == "__main__":
    main()