python src/generate_triplets.py --input_path datasets/fine_tuning_data/knowledge_dataset.json \
                                --output_path datasets/know_tuning/statchat_triplets.json \
                                --openai_api_key_path model_api_key.txt \
                                --temperature 0.0 \
                                --model gpt-3.5-turbo \
                                --write_frequency 1 \