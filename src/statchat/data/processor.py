from ..logging import get_logger
from typing import List
from .utils import (
    get_text_file,
    remove_links,
) 
import json
import os

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

    def save_markdown_splits(self, input_dir: str, output_dir: str) -> int:
        filenames = os.listdir(input_dir)
        total_splits = 0
        for filename in filenames:
            file_path = os.path.join(input_dir, filename)
            markdown_text = get_text_file(file_path)
            markdown_text = remove_links(markdown_text)
            markdown_sections = self.markdown_splitter.split_text(markdown_text)
            markdown_splits = [split.dict()
                               for split in self.text_splitter.split_documents(markdown_sections)]
            total_splits += len(markdown_splits)
            # Save these splits into one json file
            os.makedirs(output_dir, exist_ok=True)
            output_path = os.path.join(output_dir, filename.replace(".md", ".json"))
            with open(output_path, "w") as file:
                json.dump(markdown_splits, file, indent=4, ensure_ascii=False)
            
            logger.info(f"Saved {len(markdown_splits)} splits to {output_path}")
        return total_splits

