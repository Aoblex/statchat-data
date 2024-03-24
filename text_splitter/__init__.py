from typing import List
from langchain.text_splitter import (
    MarkdownHeaderTextSplitter,
    RecursiveCharacterTextSplitter,
)

class Splitter:

    def __init__(self):
        self.markdown_splitter = MarkdownHeaderTextSplitter(
            headers_to_split_on = [
            ("#", "Header 1"),
            ("##", "Header 2"),
            ("###", "Header 3"),
            ("####", "Header 4"),
        ])
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size = 200,
            chunk_overlap = 50,
            length_function = len,
            is_separator_regex = False,
        )
    
    def get_splits(self, file_path) -> List:
        with open(file_path, "r") as f:
            markdown_text = f.read()
        markdown_sections = self.markdown_splitter.split_text(markdown_text)
        markdown_splits = self.text_splitter.split_documents(markdown_sections)
        return markdown_splits