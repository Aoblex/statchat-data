from ..logging import get_logger
from typing import List
from .utils import (
    get_text_file,
    remove_links,
    keep_split,
) 
import json
import os
import re

logger = get_logger(__name__)

from langchain.text_splitter import (
    MarkdownHeaderTextSplitter,
    RecursiveCharacterTextSplitter,
)

class Splitter:

    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 500):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

        self.markdown_splitter = MarkdownHeaderTextSplitter(
            headers_to_split_on = [
            ("#", "Header 1"),
            ("##", "Header 2"),
            ("###", "Header 3"),
            ("####", "Header 4"),
        ])

        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size = self.chunk_size,
            chunk_overlap = self.chunk_overlap,
            length_function = len,
            is_separator_regex = False,
        )

    def save_splits(self, input_dir: str, output_dir: str) -> int:
        filenames = os.listdir(input_dir)
        total_splits = 0
        for filename in filenames:
            name, ext = os.path.splitext(filename)
            file_path = os.path.join(input_dir, filename)
            text = get_text_file(file_path)

            if ext == ".md":
                text = remove_links(text)
                sections = self.markdown_splitter.split_text(text)
                splits = [split.dict()
                          for split in self.text_splitter.split_documents(sections)]
            else:
                splits = [{"page_content": split}
                          for split in self.text_splitter.split_text(text)]

            # Filter useless splits
            splits = [split for split in splits if keep_split(split) is True]

            total_splits += len(splits)

            # Save these splits into one json file
            os.makedirs(output_dir, exist_ok=True)
            output_path = os.path.join(output_dir, name + ".json")
            with open(output_path, "w") as file:
                json.dump(splits, file, indent=4, ensure_ascii=False)
            
            logger.info(f"Saved {len(splits)} splits to {output_path}")
        return total_splits