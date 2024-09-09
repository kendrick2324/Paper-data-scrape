from openai import AzureOpenAI
import json
import urllib.request 
import os
import re

client = AzureOpenAI(
        api_key='c33c373d2a2b4757a185f17b90ad80a4',  # replace with your actual API key
        api_version='2023-12-01-preview',
        azure_endpoint='https://yuehuang-trustllm-3.openai.azure.com/'
    )

def get_completion(prompt):
    messages=[{"role": "user", "content": prompt}] 
    response = client.chat.completions.create(
        model='yuehuang-gpt4o',
        messages=messages,
        temperature=0,
    )
    return response.choices[0].message.content

def creat_request(i):
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

def get_content(request):
    response = urllib.request.urlopen(request)
    content = response.read()  # .decode('utf-8')#解码格式错误=========================================
    return content

def sanitize_filename(filename):
    # 移除非法字符，保证下载路径正确
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

file_path=[r"data\temp_oral_output.json",r"data\temp_poster_output.json",r"data\temp_spotlight_output.json",r"data\temp_reject_output.json",r"data\temp.json"]

with open(file_path[4], 'r',encoding='utf-8') as json_file:#读取存档论文信息的json文件
    data = json.load(json_file)
    path=r"E:\ICLR_2024\paper\temp_spotlight"#存放pdf的路径
    error_path="data\error_spotlight.txt"
    failed_list = []
    results=[]   
    for paper_id, paper_content in data.items():#取出json文件中论文标，摘要，关键词
        paper_data = json.loads(paper_content)
        for note in paper_data['notes']:
            title = note['content']['title']['value']
            abstract = note['content']['abstract']['value']
            keywords = note['content']['keywords']['value']
        file_content = {"title": title, "abstract": abstract, "keywords": keywords}
        prompt=f"""
        You will be given the title ,abstract and keywords of a paper. 
        Your task is to determine whether each paper is directly related to large language models (LLMs). 
        A paper is considered directly related to LLMs if it:
            Uses an LLM as a tool or a key part of its method.
            Explores or investigates properties or attributes of LLMs.
            Uses variations or multimodal models based on LLMs, such as MLLMs ,Flamingo or any-to-any LLMs.
        Do not count papers that only focus on foundational areas such as transformers, deep learning, reinforcement learning, efficient fine-tuning , conventional visual language models without LLM module unless there is a clear, explicit link to LLMs in the content.\
        The output for each paper should be a figure of 0 or 1, where 1 means the paper is directly related to LLMs, and 0 means it is not.Do not add any additional information or context to the response.\

Input format:
{{"title": "the paper's title", "abstract": "the paper's abstract", "keywords": "the paper's keywords"}}

Output:
0 or 1

Here is the information for the paper:{file_content}
        """
        ans=get_completion(prompt)
        if ans=='0' or ans==0:#如果不是LLM相关的文章，就不下载
            continue
        else:#如果是LLM相关的文章，就下载
            request = creat_request(paper_id)
            try:
                paper_content = get_content(request)
            except Exception as e:
                print(f"error: {e}")
                failed_list.append(paper_id)#记录下载失败的文章
                continue
            down_load(paper_content,path,title)

                   
    if len(failed_list) > 0:#如果有下载失败的文章，就把失败的文章id写入error文件
        print(f"Failed to download {len(failed_list)} papers: {failed_list}")
        if not os.path.exists(os.path.dirname(error_path)):
            os.makedirs(os.path.dirname(error_path))
        with open(error_path, 'w', encoding='utf-8') as error_file:
            for item in failed_list:
                error_file.write(f"{item}\n")
            


        
    
