from statchat.data.processor import Splitter
import argparse

def main(args):
    splitter = Splitter(
        chunk_size=args.chunk_size,
        chunk_overlap=args.chunk_overlap,
    )
    num_splits = splitter.save_markdown_splits(
        input_dir=args.input_dir,
        output_dir=args.output_dir,
    )
    print(f"Saved {num_splits} splits to {args.output_dir}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input_dir", type=str, required=True)
    parser.add_argument("--output_dir", type=str, required=True)
    parser.add_argument("--chunk_size", type=int, default=1000)
    parser.add_argument("--chunk_overlap", type=int, default=500)
    args = parser.parse_args()
    main(args=args)




