import argparse
import json

def merge_json_files(file_list, output_file):
    merged_data = []

    for file_name in file_list:
        with open(file_name, 'r') as f:
            data = json.load(f)
            merged_data.extend(data)

    with open(output_file, 'w') as f:
        json.dump(merged_data, f, indent=4, ensure_ascii=False)

def main():
    parser = argparse.ArgumentParser(description='Merge JSON files.')
    parser.add_argument('files', metavar='F', type=str, nargs='+',
                        help='the JSON files to merge')
    parser.add_argument('-o', '--output', dest='output', type=str, required=True,
                        help='the output file')

    args = parser.parse_args()
    merge_json_files(args.files, args.output)

if __name__ == "__main__":
    main()