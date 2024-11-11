import json
from config import *
import os
import re

# Used to extract the LLM_related field from the answer json
def extract_llm_related(json_string):
    match = re.search(r'"LLM_related"\s*:\s*"(\w+)"', json_string)
    if match:
        return match.group(1)
    return None

def filter_llm_related(name:str, year:str):
    current_directory = os.path.dirname(os.path.abspath(__file__))
    target_directory = os.path.join(current_directory, "LLM_Related")
    if not os.path.exists(target_directory):
        os.makedirs(target_directory)
    in_path = current_directory + "\Title_and_Abstract\\"+ f"{name}{year}.json"
    out_path = os.path.join(target_directory, f"{name}{year}.json")
    llm_related_papers = {}
    
    with open(in_path, "r", encoding="utf-8") as f:
        data = json.load(f)
        for title, abstract in data.items():
            file_content = {"title": title, "abstract": abstract}
            prompt=f"""
        Your task is to analyze each paper's title and abstract to determine whether the paper is directly related to large language models (LLMs). Follow these steps for each paper:

        1.Check for LLM Usage: Does the paper use an LLM as a tool or a core part of its methodology?
        2.Check for Exploration of LLM Properties: Does the paper explore or investigate any properties, characteristics, or attributes of LLMs?
        3.Check for LLM Variations or Multimodal Models: Does the paper use any variations or multimodal models based on LLMs, such as MLLMs, Flamingo, or any-to-any LLMs?
        If any of these criteria are met, mark the paper as related to LLMs.

However, do not consider the paper as LLM-related if:

It focuses solely on foundational areas like transformers, deep learning, reinforcement learning, efficient fine-tuning, or conventional visual-language models without an explicit link to LLMs.

For each paper, think step by step. After considering the information, provide a conclusion in JSON format with "yes" (LLM-related) or "no" (not LLM-related).

Input format:
{{
    "title": the paper's title,"abstract": the paper's abstract
}}

Output format:
{{
  "reasoning": "[step-by-step reasoning]",
  "LLM_related": "yes/no"
}}

Here is the information for the paper:{file_content}
""" 
            attepmt = 0
            flag = False
            while flag == False and attepmt < 3:
                ans = get_completion(prompt)
                if ans != None:
                    flag = True  
                    llm_related = extract_llm_related(ans)
                    if llm_related == "yes":
                        llm_related_papers[title] = abstract
                        print(f"{title} is LLM_related")
                    else:
                        print(f"{title} is not LLM_related")
                else:
                    attepmt += 1
                    print(f"Attempt {attepmt+1} failed")
                
    with open(out_path, 'w', encoding='utf-8') as json_file:
        json.dump(llm_related_papers, json_file, ensure_ascii=False, indent=4)

filter_llm_related("ECCV", "2024")