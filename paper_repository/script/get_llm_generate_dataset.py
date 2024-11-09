import json
from config import *
import os
import re

def extract_llm_generate_dataset(json_string):#用于从答案的json中提取LLM_related字段
    pattern = r'"datasets-generation-via-LLM":\s*"([^"]*)"'
    match = re.search(pattern, json_string)
    if match:
        return match.group(1)
    return None
    
def filter_llm_generate_dataset(name:str, year:str):
    current_directory = os.path.dirname(os.path.abspath(__file__))
    target_directory = os.path.join(current_directory, "LLM_Generate_Dataset")
    if not os.path.exists(target_directory):
        os.makedirs(target_directory)
    in_path = current_directory + "\Title_and_Abstract\\"+ f"{name}{year}.json"
    out_path = os.path.join(target_directory, f"{name}{year}.json")
    llm_generate_dataset_papers = {}
    
    with open(in_path, "r", encoding="utf-8") as f:
        data = json.load(f)
        for title, abstract in data.items():
            file_content = {"title": title, "abstract": abstract}
            prompt=f"""
        Now I will give you the title and abstract of a paper. Your task is to analyze whether the paper utilizes a large language model (LLM) to generate datasets. To make this determination, please follow these steps for each paper( For each step, you should make judgements literally, not make assumptions or inferences):

        Step 1: Check for Dataset Generation:
        Does the paper directly mentions the emergence of new datasets? The new datasets should be generated for specific tasks or domains, such as CoCo, ImageNet or CIFAR-10, which were generated for computer vision tasks. 
        
        Step 2: Check for LLM Usage in Dataset Generation:
        Does the paper explicitly mention the use of a large language model (LLM) during the datasets generation process identified in Step 1? The LLM could be used to generate the datasets from scratch or augment existing datasets.
        
        Step 3: Verify the Role of the LLM in Dataset Generation:
        Does the paper explicitly state that the LLM is specifically employed as a data generator to create or augment the datasets identified in Step 1? This would imply that the LLM is not utilized for task-solving, training, tuning, or testing on the newly generated datasets, nor is it used as an evaluator in the assessment process.
        
        If both steps are satisfied (i.e., the paper generates new datasets and uses an LLM as generator during the generation), you should conclude that the paper uses an LLM to generate new datasets. Otherwise, conclude that it does not.
        
For each paper, think step by step. After considering the information, provide a conclusion in JSON format with "yes" (the paper uses LLM to generate new datasets) or "no" (the paper doesn't use llm to generate new datasets).

Input format:
{{
    "title": the paper's title,"abstract": the paper's abstract
}}

Output format:
{{
  "reasoning": "[step-by-step reasoning]",
  "datasets-generation-via-LLM": "yes/no"
}}

Here is the information for the paper:{file_content}
        """

            ans = get_completion(prompt)  
            llm_generate_dataset = extract_llm_generate_dataset(ans)
            if llm_generate_dataset == "yes":
                llm_generate_dataset_papers[title] = abstract
                print(f"{title} uses LLM to generate new datasets.")
            else:
                print(f"{title} doesn't use LLM to generate new datasets.")
                
    with open(out_path, 'w', encoding='utf-8') as json_file:
        json.dump(llm_generate_dataset_papers, json_file, ensure_ascii=False, indent=4)

filter_llm_generate_dataset("ACL", "2024")