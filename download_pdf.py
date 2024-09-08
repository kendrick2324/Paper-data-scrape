from openai import OpenAI
import json
import urllib.request 
import os
import re 

client = OpenAI(api_key="sk-c6e21c1400f14b0c8cf23f2da12a0a69", base_url="https://api.deepseek.com")

def gen_glm_params(prompt):
    messages = [{"role": "system", "content":"You are a professional paper analyzer."},
                {"role": "user", "content":prompt}]
    return messages

def get_completion(prompt, model="deepseek-chat", temperature=0):#temperature越低内容越趋同
    messages = gen_glm_params(prompt)
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=temperature
    )
    if len(response.choices) > 0:
        return response.choices[0].message.content
    return "generate answer error"

def sanitize_filename(filename):
    # 移除非法字符
    filename = re.sub(r'[\\/*?:"<>|]', "", filename)
    # 限制文件名长度
    return filename[:255]

file_path=[r"data\oral_output.json",r"data\poster_output.json",r"data\spotlight_output.json",r"data\reject_output.json"]

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

def get_content(request):#获取pdf内容
    response = urllib.request.urlopen(request)
    content = response.read()  
    return content

def down_load(content, path, title):#下载pdf到指定位置
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

with open(file_path[3], 'r',encoding='utf-8') as json_file:
    id_dict = json.load(json_file)
    path=r"E:\ICLR_2024\paper\reject"
    error_path="data\error_spotlight.txt"
    failed_list = []
    for i in list(id_dict.keys()):
        content=id_dict[i][0]
        title=id_dict[i][0]['title']
        prompt=f"""
    Now I will give you a paper's title and abstract.You need to check if the paper mentions Large Language Modal.
    Mentions here refer to direct textual references in the text.Finally,your answer should be 0 or 1.
    The former means you don't think the article mentions the Large Language Model(LLM),while the latter means yes.
    {content}
            """
        ans=get_completion(prompt)
        if ans=='0':
            continue
        else:
            request = creat_request(i)
            try:
                paper_content = get_content(request)
            except Exception as e:
                print(f"error: {e}")
                failed_list.append(i)
                continue
            down_load(paper_content,path,title)
            print(f"Downloaded {title}")
            
    if len(failed_list) > 0:
        print(f"Failed to download {len(failed_list)} papers: {failed_list}")
        with open(error_path, 'w', encoding='utf-8') as error_file:
            for item in failed_list:
                error_file.write(f"{item}\n")