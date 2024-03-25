# Statchat-data

## 问答生成

选择`data`文件夹中的`markdown`格式文本以生成问答数据。

- prompt_topic: 任意字符串，用于替换提示词中的主题。
- data_file_name: `data`文件夹中的文件名，无后缀名。

```bash
./main.py --prompt_topic 深度学习 \
          --data_file_name deeplearning \
```

## 数据集合并

运行 `generate_dataset.sh` 将生成的问答存储为训练的标准格式。

### generate_dataset.sh
```bash
./export_to_dataset.py --data_file_name statistics
./export_to_dataset.py --data_file_name mathematical_statistics
./export_to_dataset.py --data_file_name deeplearning
./export_to_dataset.py --data_file_name machine_learning 
```

## 数据筛选

运行 `label.sh` 给 `datasets` 文件夹中的数据打标签。

### 运行说明
首先读取`file_dir`中的数据用于打标签，然后读取`output_dir`中的对应文件更新已经记录过的标签。

- file_dir: 待标签文件的目录
- output_dir: 标签的输出目录
- file_name: 待标签文件的文件名，无后缀名，默认为`json`文件。

标记后的数据会存放在`output_dir`目录中，文件名为`file_name`。

### 操作说明
显示一组问答后有若干输入选项：
- label: 输入`0,1,2`标记数据，数据质量依次递增，`0`表示数据质量差，`2`表示数据质量好。
    - 对于一些含有 `根据例题/表格/公式1.1.1...`等的强烈依赖于上下文的数据可以归类为`0`
    - 对于类似于`对于某电商6月份各天的销售额数据，如何计算销售额的偏度和峰度？`的不明确引用的数据；或者拿不定主意，不确定好坏的数据，可以归类为`1`
    - 对于你认为质量相对较好的适用于训练的数据，可以归类为`2`
- undo: 输入`u`撤回上一个标签。
- quit: 输入`q`退出，将本次标记的标签写入文件。

### 分工

|姓名|科目|运行文件|
|---|---|---|
wcr|统计学|label_tasks/label_wcr.sh|
ljw|数理统计|label_tasks/label_ljw.sh|
zyc|机器学习|label_tasks/label_zyc.sh|
lky|深度学习|label_tasks/label_lky.sh|

### 注意事项

开始打标签之前，先使用 `git pull` 更新数据。每次标记完成后记得 `git add` 和 `git commit`，提交的注释最好用英文写。提交完成后记得 `git push`

### 使用示例
一定要切换到`statchat-data`所在目录
```bash
  [llama_factory] root@vgpu >> /data/wangchenrui/statchat-data 
  Monday 25 March 12:56:24 [main]
  $ ./label_tasks/label_wcr.sh 
-------------------------------------------------------------
问题：在这个年龄段的人群中，哪个年龄段的人数最多？

回答：在这个年龄段的人群中，40岁至50岁的人数最多，为100人。

Enter label ['0', '1', '2'], 'u' to undo last label, 'q' to quit:   
```