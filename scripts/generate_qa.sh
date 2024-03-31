#!/bin/bash
python src/generate_qa.py --question_prompt_path datasets/prompts/statistics/question.txt \
                          --answer_prompt_path datasets/prompts/statistics/answer.txt \
                          --context_path datasets/context/statistics.json \
                          --qa_path datasets/question_answer/statistics.json \
                          --openai_api_key_path model_api_key.txt \
                          --temperature 0.0 \
                          --model gpt-3.5-turbo-1106 \
                          --max_context 1 \
                          --write_frequency 1 \
                          --random