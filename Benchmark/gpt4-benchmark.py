from openai import AzureOpenAI
import time
import fitz  # PyMuPDF
import os
import glob
from pdfminer.high_level import extract_text
import re

# 定义关键词列表
words_list = [
    "benchmark", "evaluation", "performance", "comparison", "dataset", 
    "improvement","metric", "experiment", "evaluate", "result","state-of-the-art","compare","judge",
    "experimental results", "sota", "baseline"
]

# 提取整个 PDF 的文本内容
def extract_text_from_pdf(pdf_path):
    text = extract_text(pdf_path)
    return text

# 按段落拆分文本内容
def split_text_to_paragraphs(text):
    # 使用两个换行符分割段落
    paragraphs = re.split(r'\n\s*\n', text)
    return paragraphs

# 删除所有长度小于20的段落
def remove_short_paragraphs(paragraphs):
    filtered_paragraphs = []
    for paragraph in paragraphs:
        # 去除开头结尾的空白符，然后按空格分割单词列表
        words = paragraph.strip().split()
        # 只保留不等于1的段落
        if len(words) >20:
            filtered_paragraphs.append(paragraph.strip())
    return filtered_paragraphs

# 筛选含有关键词的段落
def filter_paragraphs_by_keywords(paragraphs, keywords):
    keyword_paragraphs = {}
    i=1
    for paragraph in paragraphs:
        # 如果段落中包含任何一个关键词，则保留该段落
        if any(keyword.lower() in paragraph.lower() for keyword in keywords):
            keyword_paragraphs[i] = paragraph
            i+=1
    return keyword_paragraphs

# 主函数
def main(pdf_path):
    # 提取 PDF 中的所有文本
    text = extract_text_from_pdf(pdf_path)
    # 将文本按段落拆分
    paragraphs = split_text_to_paragraphs(text)
    # 移除所有单个单词的段落
    paragraphs = remove_short_paragraphs(paragraphs)
    # 筛选出包含关键词的段落
    keyword_paragraphs = filter_paragraphs_by_keywords(paragraphs, words_list)
    # 将段落列表转换为一个字符串，每个段落之间用两个换行符分隔
    return keyword_paragraphs

def get_benchmark(para_content):
    if not para_content:
        return None

    prompt=prompt=f"""
        Now I will give you some paragraphs of the paper for you to analyze and answer some questions. 
        
        But first,I want you to know the following knowledge:
        
        1.benchmark:A benchmark is a standard set of tests, including specific datasets , used to evaluate and compare the performance of different machine learning models or algorithms.
        2.use llm to generate benchmark:This technique means using a large language model (LLM) to generate benchmarks for specific tasks or targets.The benchmarks generated must consist of specific datasets.These datasets must be processed by LLM or generated from scratch by LLM ,not person.
        3.use llm as a metric/judge:This technique means employing LLM to evaluate the quality or effectiveness of content, such as written work, code, or other outputs.It is often used in essay grading, code review, or creative writing critiques.
        
        Now Follow these steps for each paper:
        1.Check for benchmark usage: Does the paper use the existing benchmarks to evaluate the performance of the model or effectiveness of the new algorithm? 
        2.Create a new benchmark via LLM: Does the paper use the large language model to generate a new benchmark ?
        3.Use the LLM to evaluate: Does the paper use the large language model as a metric or judge to evaluate the quality or effectiveness of content?

After considering the information, you should first answer the question "whether the paper uses the benchmark" with "yes" or "no". If the paper uses the benchmark, you should answer the question "how does the paper use the benchmark" with a summary of what benchmarks are used and show the results. Else you should answer that with "nothing".
Then, you should answer the question "whether the paper generates a new benchmark via LLM" with "yes" or "no". If the paper generates a new benchmark via LLM, you should answer the question "how does the paper generate a new benchmark via LLM" with a summary of how does paper use the LLM to generate benchmark and why they use the LLM to generate.Else you should answer that with "nothing".
Finally, you should answer the question "whether the paper use LLM as a judge/metric" with "yes" or "no". If the paper uses LLM a judge/metric, you should answer the question "how does the paper use LLM as a judge/metric" with a summary of what tasks does the paper use the LLM to evaluate and the reason why to use LLM.Else you should answer that with "nothing".
Show your answers in JSON format like the Output format:

Input format:
{{
    "Paragraph 1": the content of paragraph 1,"Paragraph 2": the content of paragraph 2,"Paragraph 3": the content of paragraph 3..."Paragraph n": the content of paragraph n
}}

Output format:
{{
  "whether the paper uses the benchmark":yes/no,
  "how does the paper use the benchmark":"[analyzing the usage of the benchmark]",
  "whether the paper generates a new benchmark via LLM":yes/no,
  "how does the paper generate a new benchmark via LLM":"[how to create a new benchmark via LLM]",
  "whether the paper use LLM as a judge/metric":yes/no,
  "how does the paper use LLM as a judge/metric":"[how to use LLM as a judge/metric]"
}}

Here is the information for the paper:{para_content}
        """    
    

    client = AzureOpenAI(
        api_key='c33c373d2a2b4757a185f17b90ad80a4',  # replace with your actual API key
        api_version='2023-12-01-preview',
        azure_endpoint='https://yuehuang-trustllm-3.openai.azure.com/'
    )
    
    content = [{"role": "user", "content": prompt}]
    
    success = False
    attempt = 0
    while not success and attempt < 3:
        try:
            chat_completion = client.chat.completions.create(
                model='yuehuang-gpt4o',
                messages=content
            )

            success = True
            output = chat_completion.choices[0].message.content.strip()
        except Exception as e:
            print(e)
            attempt += 1
            time.sleep(10)

    return output
#"ICLR2024/paper/oral"
pdf_path="temp"
pdf_files = glob.glob(os.path.join(pdf_path, "*.pdf"))
result_txt_path="result.txt"

for pdf_file in pdf_files:
    para_content=main(pdf_file)
    ans=get_benchmark(para_content)
    print(ans)
    with open(result_txt_path, 'a') as f:
        f.write(f"{pdf_file}: {ans}\n")
        
# for pdf_file in pdf_files:
#     para_content = main(pdf_file)
#     ans = get_benchmark(para_content)
#     print(ans)
    
#     results[pdf_file] = ans
#     count += 1
    
#     if count % 1 == 0:
#         with open(result_path, 'a') as f:
#             json.dump(results, f)
#             f.write('\n')
#         results.clear()

# # 写入剩余的结果
# if results:
#     with open(result_path, 'a') as f:
#         json.dump(results, f)
#         f.write('\n')