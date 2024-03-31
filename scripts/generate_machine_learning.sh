#!/bin/bash
python src/generate_qa.py --question_prompt_path datasets/prompts/machine_learning/question.txt \
                          --answer_prompt_path datasets/prompts/machine_learning/answer.txt \
                          --context_path datasets/context/machine_learning.json \
                          --qa_path datasets/question_answer/machine_learning.json \
                          --openai_api_key_path model_api_key.txt \
                          --temperature 0.0 \
                          --model gpt-3.5-turbo-1106 \
                          --max_context 100 \
                          --write_frequency 1 \
