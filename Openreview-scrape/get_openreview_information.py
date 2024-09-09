import json
import requests
import urllib.request
import urllib.parse
from tqdm import tqdm
import time
import random
import os

def creat_request(i,key):#依据id创建request
    base_url='https://api2.openreview.net/notes?forum='
    if key=='oral':
        url=base_url+i+'&content.venue=ICLR%202024%20oral'
    elif key=='spotlight':
        url=base_url+i+'&content.venue=ICLR%202024%20spotlight'
    elif key=='poster':
        url=base_url+i+'&content.venue=ICLR%202024%20poster'
    elif key=='decisionPending':
        url=base_url+i+'&content.venue=Submitted%20to%20ICLR%202024'
    headers = {
                'origin':'https://openreview.net',
                'referer':'https://openreview.net/',
                'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }    
    request=urllib.request.Request(url=url,headers=headers)
    return request

def get_content(request, retries=3, delay=1):#获取information
    for attempt in range(retries):
        try:
            response = urllib.request.urlopen(request)
            content = response.read().decode('utf-8')
            return content
        except Exception as e:
            print(f"Request failed: {e}. Retrying in {delay} seconds...")
            time.sleep(delay)
            delay *= 2  # Exponential backoff
    raise Exception("Failed to fetch content after multiple retries")

# def filter_content(i, data):#过滤数据，只保留title和abstract  
#     filtered_notes = []
#     for note in data.get('notes', []):
#         content = note.get('content', {})
#         title = content.get('title', {}).get('value', '')
#         abstract = content.get('abstract', {}).get('value', '')
#         filtered_notes.append({
#             'title': title,
#             'abstract': abstract
#         })
#     return {i: filtered_notes}

def process_ids(ids, key, json_path, batch_size=10):
    final_content = {}
    count = 0
    for the_id in tqdm(ids):
        request = creat_request(the_id, key)
        try:
            content = get_content(request)
            file_content = {the_id: content}
            final_content.update(file_content)
            count += 1
            time.sleep(random.uniform(1, 3))  # Random delay between requests
            
            if count % batch_size == 0:
                # 读取现有的 JSON 文件内容
                if os.path.exists(json_path):
                    with open(json_path, 'r', encoding='utf-8') as json_file:
                        try:
                            existing_content = json.load(json_file)
                        except json.JSONDecodeError:
                            existing_content = {}
                    existing_content.update(final_content)
                else:
                    existing_content = final_content
                
                # 写入更新后的内容
                with open(json_path, 'w', encoding='utf-8') as json_file:
                    json.dump(existing_content, json_file, ensure_ascii=False, indent=4)
                
                print(f"Processed and wrote {count} IDs to {json_path}")
                final_content = {}  # 清空 final_content 以便处理下一批次
        except Exception as e:
            print(f"Failed to process ID {the_id}: {e}")
    
    # 写入最后一批不满 batch_size 的 final_content
    if final_content:
        if os.path.exists(json_path):
            with open(json_path, 'r', encoding='utf-8') as json_file:
                existing_content = json.load(json_file)
            existing_content.update(final_content)
        else:
            existing_content = final_content
        
        with open(json_path, 'w', encoding='utf-8') as json_file:
            json.dump(existing_content, json_file, ensure_ascii=False, indent=4)
        
        print(f"Processed and wrote remaining {count % batch_size} IDs to {json_path}")

key="oral"
input_path = r"data\oral.json"
output_path = r"data\oral_output.json"

with open(input_path, 'r', encoding='utf-8') as input_file:
    data = json.load(input_file)
    ids = data.get(key, [])

process_ids(ids, key, output_path)





