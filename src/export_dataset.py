from statchat.data.utils import export_dataset

export_dataset(
    input_path="datasets/question_answer/statistics.json",
    output_dir="datasets/fine_tuning_data",
)

export_dataset(
    input_path="datasets/question_answer/mathematical_statistics.json",
    output_dir="datasets/fine_tuning_data",
)

export_dataset(
    input_path="datasets/question_answer/machine_learning.json",
    output_dir="datasets/fine_tuning_data",
)

export_dataset(
    input_path="datasets/question_answer/deeplearning.json",
    output_dir="datasets/fine_tuning_data",
)