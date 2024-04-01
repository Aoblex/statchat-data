# Statchat-data

## 数据集说明

所有的数据存放在`datasets`文件夹中。

- knowledge: 教科书的`md`文档。
- context: 将教科书分块后生成的上下文片段。
- prompts: 用于gpt问答生成的提示词。

## 使用说明

运行使用的脚本存放于`scripts`中

### generate_context.sh
将`input_dir`下的所有文档进行分块，输出到`output_dir`中，
可以传入分块的参数。
```bash
python src/generate_context.py --input_dir datasets/knowledge \
                               --output_dir datasets/context \
                               --chunk_size 1000 \
                               --chunk_overlap 500
```

### generate_statistics.sh
利用gpt，使用写好的prompt生成问答，通过设置`random`参数随机取上下文，已经生成过的上下文会自动跳过。
```bash
python src/generate_qa.py --question_prompt_path datasets/prompts/statistics/question.txt \
                          --answer_prompt_path datasets/prompts/statistics/answer.txt \
                          --context_path datasets/context/statistics.json \
                          --qa_path datasets/question_answer/statistics.json \
                          --openai_api_key_path model_api_key.txt \
                          --temperature 0.0 \
                          --model gpt-3.5-turbo-1106 \
                          --max_context 3 \
                          --write_frequency 1 \
                          --random
```

## 导出数据
将数据集导出为适用于[LLaMA_Factory](https://github.com/hiyouga/LLaMA-Factory)训练的格式
```bash
python src/export_dataset.py
```