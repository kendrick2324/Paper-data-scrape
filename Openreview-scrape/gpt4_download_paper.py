from openai import AzureOpenAI
import json
import urllib.request 
import os
import re

#此程序主要用于根据文章摘要、标题、关键词判断文章是否与LLM相关，并下载相关的文章

client = AzureOpenAI(#这里是Azure的API
        api_key='c33c373d2a2b4757a185f17b90ad80a4',  # replace with your actual API key
        api_version='2023-12-01-preview',
        azure_endpoint='https://yuehuang-trustllm-3.openai.azure.com/'
    )

def get_completion(prompt):#这里是调用Azure的API
    messages=[{"role": "user", "content": prompt}] 
    response = client.chat.completions.create(
        model='yuehuang-gpt4o',
        messages=messages,
        temperature=0,
    )
    return response.choices[0].message.content

def creat_request(i):#用于创建下载pdf的request
    base_url='https://openreview.net/pdf?id='
    url=base_url+i
    headers = {
                'cookie':'_ga=GA1.1.926646815.1652076197; __cuid=6e7a75c726ae4dd39d64b75000eba48a; amp_fef1e8=eec1aab1-0a18-42ea-8ce6-0d89117b5bf6R...1ha9bookf.1ha9bp5nc.4.1.5; _ga_3TRQ40799D=GS1.1.1694678934.1.1.1694679018.0.0.0; _ga_GTB25PBMVL=GS1.1.1706703827.4.1.1706704498.0.0.0',
                'origin':'https://openreview.net',
                'referer':'https://openreview.net/',
                'user-agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
                }   
    request=urllib.request.Request(url=url,headers=headers)
    return request

def get_content(request):#用于获取pdf内容，辅助下载
    response = urllib.request.urlopen(request)
    content = response.read() 
    return content

def sanitize_filename(filename):#用于取出每个文章名中的非法字符，保持下载地址的有效性
    # 移除非法字符
    filename = re.sub(r'[\\/*?:"<>|]', "", filename)
    # 限制文件名长度
    return filename[:255]

def down_load(content, path, title):#这个存放pdf的path要提前写好
    title = sanitize_filename(title)
    # 确保路径包含文件名
    if os.path.isdir(path):
        path = path + '\\' + title + '.pdf'
    try:
        with open(path, 'wb') as fp:
            fp.write(content)
        print(f"文件 {path} 下载成功")
    except Exception as e:
        print(f"文件 {path} 下载失败: {e}")

def extract_llm_related(json_string):#用于从答案的json中提取LLM_related字段
    match = re.search(r'"LLM_related"\s*:\s*"(\w+)"', json_string)
    if match:
        return match.group(1)
    return None

#这个字典取决于你本地的标题，摘要，关键词信息的存放位置，需要修改！！！
file_path=[r"data\ver_2\temp_oral_output.json",r"data\ver_2\temp_poster_output.json",r"data\ver_2\temp_spotlight_output.json",r"data\ver_2\temp_reject_output.json",r"data\ver_2\temp.json",r"data\ver_2\temp_1.json"]

with open(file_path[2], 'r',encoding='utf-8') as json_file:
    data = json.load(json_file)
    path=r"E:\ICLR_2024\paper\temp_spotlight"#存放pdf的地址，需要修改！！！
    error_path="data\error_oral.txt"#存放下载错误paper名的地址，需要修改！！！
    #result_path=r"data\result_spotlight_2.txt" #测试大模型效果时使用，不用管
    failed_list = []
    results=[]   
    for paper_id, paper_content in data.items():#遍历每篇文章
        paper_data = json.loads(paper_content)
        for note in paper_data['notes']:#此处的title，abstract，keywords取决于你本地的json文件的结构，需要修改！！！
            title = note['content']['title']['value']
            abstract = note['content']['abstract']['value']
            keywords = note['content']['keywords']['value']
        file_content = {"title": title, "abstract": abstract, "keywords": keywords}
        prompt=f"""
        Your task is to analyze each paper's title, abstract, and keywords to determine whether the paper is directly related to large language models (LLMs). Follow these steps for each paper:

        1.Check for LLM Usage: Does the paper use an LLM as a tool or a core part of its methodology?
        2.Check for Exploration of LLM Properties: Does the paper explore or investigate any properties, characteristics, or attributes of LLMs?
        3.Check for LLM Variations or Multimodal Models: Does the paper use any variations or multimodal models based on LLMs, such as MLLMs, Flamingo, or any-to-any LLMs?
        If any of these criteria are met, mark the paper as related to LLMs.

However, do not consider the paper as LLM-related if:

It focuses solely on foundational areas like transformers, deep learning, reinforcement learning, efficient fine-tuning, or conventional visual-language models without an explicit link to LLMs.

For each paper, think step by step. After considering the information, provide a conclusion in JSON format with "yes" (LLM-related) or "no" (not LLM-related).

Input format:
{{
    "title": the paper's title,"abstract": the paper's abstract,"keywords": the paper's keywords
}}

Output format:
{{
  "reasoning": "[step-by-step reasoning]",
  "LLM_related": "yes/no"
}}

Here is the information for the paper:{file_content}
        """
        ans = get_completion(prompt)#获取大模型输出
        llm_related = extract_llm_related(ans)  # 使用正则表达式提取LLM_related字段
        if llm_related == "yes":#大模型判断论文属于LLM_related
            request = creat_request(paper_id)
            try:
                paper_content = get_content(request)
            except Exception as e:
                print(f"error: {e}")
                failed_list.append(paper_id)
                continue
            down_load(paper_content,path,title)
        
    if len(failed_list) > 0:#存在下载失败的paper
        print(f"Failed to download {len(failed_list)} papers: {failed_list}")
        if not os.path.exists(os.path.dirname(error_path)):
            os.makedirs(os.path.dirname(error_path))
        with open(error_path, 'w', encoding='utf-8') as error_file:
            for item in failed_list:
                error_file.write(f"{item}\n")
            


        
    
