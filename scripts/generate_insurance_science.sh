#!/bin/bash
subject="insurance-science"
python src/generate_qa.py --question_prompt_path datasets/prompts/$subject/question.txt \
                          --answer_prompt_path datasets/prompts/$subject/answer.txt \
                          --context_path datasets/context/$subject.json \
                          --qa_path datasets/question_answer/$subject.json \
                          --openai_api_key_path model_api_key_finance.txt \
                          --temperature 0.0 \
                          --model gpt-3.5-turbo-1106 \
                          --write_frequency 1 \