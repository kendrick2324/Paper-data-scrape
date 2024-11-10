import requests
from bs4 import BeautifulSoup

def get_paper_details(url: str):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # 提取标题
    title = soup.find('meta', {'name': 'citation_title'})['content']
    
    # 提取摘要
    abstract = soup.find('div', {'id': 'abstract'}).text.strip()
    
    return title, abstract

url = "https://openaccess.thecvf.com/content/CVPR2023/html/Ci_GFPose_Learning_3D_Human_Pose_Prior_With_Gradient_Fields_CVPR_2023_paper.html"
title, abstract = get_paper_details(url)
print("Title:", title)
print("Abstract:", abstract)