import argparse
import json
import os
import bisect

LABEL_LEVELS = ['0', '1']

def binary_search(lst, x):
    i = bisect.bisect_left(lst, x)
    if i != len(lst) and lst[i] == x:
        return i
    else:
        return -1

def show_qa(data_item):
    print("-" * 80, '\n')
    print(f"问题：\033[33m{data_item['prompt']}\033[0m\n")
    print(f"回答：{data_item['response']}\n")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--file_name", help="The JSON file to label")
    parser.add_argument("--input_dir", help="The directory of the JSON file to label")
    parser.add_argument("--output_dir", help="The directory to save the labeled JSON file")
    args = parser.parse_args()

    file_name = args.file_name
    input_dir = args.input_dir
    output_dir = args.output_dir
    file_path = os.path.join(input_dir, file_name)
    output_path = os.path.join(output_dir, file_name)
    os.makedirs(output_dir, exist_ok=True)

    # Original data
    if os.path.exists(file_path):
        with open(file_path, 'r') as f:
            data = json.load(f)
    else:
        print(f"File {file_path} does not exist.")
        exit(0)

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

        print(f">>> Labeling progress: \033[36m{i + 1}/{len(data)}\033[0m")

        zero_counts = len([item for item in data if item.get("label", None) == 0])
        one_counts = len([item for item in data if item.get("label", None) == 1])

        print(f">>> Labeling statistics: \033[31m0: {zero_counts}, \033[32m1: {one_counts}\033[0m")

        if data[i].get("label", None) is not None:
            print("Already labeled, skipping.")
            i = i + 1
            continue


        while True:

            label = input(f">>> Enter label {LABEL_LEVELS}(default 1), 'u' to undo last label, 'q' to quit: ")
            if label == '': label = '1'
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
        print(f"Label \033[1;31m{data[i]['label']}\033[0m added to:\n\033[33m{data[i]['prompt']}\033[0m")

        i = i + 1

if __name__ == "__main__":
    main()