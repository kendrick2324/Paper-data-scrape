from openai import AzureOpenAI
import time
import os
import glob
import fitz
from pdfminer.high_level import extract_text
import re

#按页提取pdf文本
def extract_all_text(pdf_path):
    context = ""
    with fitz.open(pdf_path) as pdf_file:
        num_pages = pdf_file.page_count

        for page_num in range(num_pages):
            page = pdf_file[page_num]
            page_text = page.get_text()
            context += page_text
    return context

#利用gpt4提取需要的信息
def get_benchmark(para_content):
    if not para_content:
        return None
    
    prompt=f"""
        Now I will give you the content of the paper for you to analyze and answer some questions. 
        But first, I want you to know the following knowledge:
        
        1.benchmark: A benchmark is a standardized dataset or task used to evaluate or compare the performance of different models, algorithms, or techniques. It usually consists of data, evaluation metrics, and specific tasks.
        2.use LLM to generate benchmark: This technique means using a large language model (LLM) to generate benchmarks for specific tasks or targets. The benchmarks generated here consist of two main types: 1) a new benchmark generated by LLM from scratch(A new dataset is a must); 2) a existing benchmark improved by LLM, such as data augmentation, data cleaning, or other methods.
        3.use LLM as a metric/judge: This technique builds an evaluation framework with a Large Language Model (LLM) as a component. This framework often be used to evaluate the quality of content, such as written work, code, or other outputs.Note that the LLM is to act as a judge to evaluate the results of the task, not as a participant to complete the task. 
        4.ethics statement:An ethic statement is a declaration that the research follows ethical guidelines, including consent, approval, privacy protection, and conflict of interest disclosure.
        
        Now Follow these steps for each paper:
        1.Check for benchmark usage: Does the paper use the existing benchmarks to evaluate the performance of the model or effectiveness of the new algorithm? 
        2.Create a new benchmark via LLM: Does the paper use the large language model to generate a new benchmark (A new dataset generated/processed by LLM is a must)?
        3.Use the LLM to evaluate: Does the paper use the large language model as a metric or judge to build an evaluation framework?
        4.Give the ethics statement: Does the paper include an ethics statement?
        
After considering the information, you should first answer the question "whether the paper uses the benchmark" with "yes" or "no". If the paper uses the benchmark, you should answer the question "how does the paper use the benchmark" with a statement of all the benchmarks that are used and show the results in detail. Else you should answer that with "nothing".
Then, you should answer the question "whether the paper generates a new benchmark via LLM" with "yes" or "no". If the paper generates a new benchmark via LLM, you should answer the question "how does the paper generate a new benchmark via LLM" with a statement of how does the paper use the LLM to generate benchmark and the reason why they use the LLM to generate and some other information. Else you should answer that with "nothing".
After that, you should answer the question "whether the paper use LLM as a judge/metric" with "yes" or "no". If the paper uses LLM as a judge/metric, you should answer the question "how does the paper use LLM as a judge/metric" with a statement of what tasks does the paper use the LLM to evaluate, the reason why to use LLM and some other information. Else you should answer that with "nothing".
Finally, you should answer the question "whether the paper includes an ethics statement" with "yes" or "no". If the paper includes an ethics statement, you should answer the question "the content of the ethics statement" with a summary of the content of the ethics statement.Else you should answer that with "nothing".
Show your answers in JSON format like the Output format:

Input format:
{{
    the content of the paper.
}}

Output format:
{{
  "whether the paper uses the benchmark":yes/no,
  "how does the paper use the benchmark":"[analyzing the usage of the benchmark]",
  "whether the paper generates a new benchmark via LLM":yes/no,
  "how does the paper generate a new benchmark via LLM":"[how to create a new benchmark via LLM]",
  "whether the paper use LLM as a judge/metric":yes/no,
  "how does the paper use LLM as a judge/metric":"[how to use LLM as a judge/metric]",
  "whether the paper includes an ethics statement":yes/no,
  "the content of the ethics statement":"[the content of the ethics statement]"
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
pdf_path="temp" #pdf文件存放路径
pdf_files = glob.glob(os.path.join(pdf_path, "*.pdf"))
result_txt_path="result3.txt" #结果保存路径

for pdf_file in pdf_files:#遍历所有pdf
    para_content=extract_all_text(pdf_file)#先提取pdf文本
    ans=get_benchmark(para_content)#获取需要的json格式结果
    print(ans)
    with open(result_txt_path, 'a') as f:
        f.write(f"{pdf_file}: {ans}\n")#写入结果保存路径


#后面的代码是将结果写成json格式，目前还处于测试阶段，暂时不用        
# for pdf_file in pdf_files:
#     para_content = main(pdf_file)
#     ans = get_benchmark(para_content)
#     print(ans)
    
#     results[pdf_file] = ans
#     count += 1
    
#     if count % 10== 0:
#         with open(result_path, 'a') as f:
#             json.dump(results, f)
#             f.write('\n')
#         results.clear()

# # 写入剩余的结果
# if results:
#     with open(result_path, 'a') as f:
#         json.dump(results, f)
#         f.write('\n')