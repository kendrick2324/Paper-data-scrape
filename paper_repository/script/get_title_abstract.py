import json
import requests
from jsonpath_ng import jsonpath, parse
import urllib.request
import urllib.parse
from bs4 import BeautifulSoup
import os
import re
import time
from urllib.parse import urlparse, parse_qs

# The 'year' in the url will be replaced with the actual year of the conference. (parameter)
Openreview_urls={ 
    # The papers of ICLR, ICML, NeruIPS, COLM, NeruIPS-Datasets and Benchmarks can be accessed by the api2 of openreview. The categorisation and urls of the papers here references their conditions in 2024 and may change in the future, you can modify it according to the actual situation in the openreview.
    "ICLR":['https://api2.openreview.net/notes?content.venue=ICLR%20year%20oral&details=replyCount%2Cpresentation&domain=ICLR.cc%2Fyear%2FConference&limit=25&',
            'https://api2.openreview.net/notes?content.venue=ICLR%20year%20spotlight&details=replyCount%2Cpresentation&domain=ICLR.cc%2Fyear%2FConference&limit=25&',
            'https://api2.openreview.net/notes?content.venue=ICLR%20year%20poster&details=replyCount%2Cpresentation&domain=ICLR.cc%2Fyear%2FConference&limit=25&',
            'https://api2.openreview.net/notes?content.venue=Submitted%20to%20ICLR%20year&details=replyCount%2Cpresentation&domain=ICLR.cc%2Fyear%2FConference&limit=25&'
            ],
    
    "ICML":['https://api2.openreview.net/notes?content.venue=ICML%20year%20Oral&details=replyCount%2Cpresentation&domain=ICML.cc%2Fyear%2FConference&limit=25&',
            'https://api2.openreview.net/notes?content.venue=ICML%20year%20Spotlight&details=replyCount%2Cpresentation&domain=ICML.cc%2Fyear%2FConference&limit=25&',
            'https://api2.openreview.net/notes?content.venue=ICML%20year%20Poster&details=replyCount%2Cpresentation&domain=ICML.cc%2Fyear%2FConference&limit=25&'
            ],
    
    "NeruIPS":['https://api2.openreview.net/notes?content.venue=NeurIPS%20year%20oral&details=replyCount,presentation&domain=NeurIPS.cc/year/Conference&limit=25&',
               'https://api2.openreview.net/notes?content.venue=NeurIPS%20year%20spotlight&details=replyCount%2Cpresentation&domain=NeurIPS.cc%2Fyear%2FConference&limit=25&',
               'https://api2.openreview.net/notes?content.venue=NeurIPS%20year%20poster&details=replyCount,presentation&domain=NeurIPS.cc/year/Conference&limit=25&',
               'https://api2.openreview.net/notes?content.venue=Submitted%20to%20NeurIPS%20year&details=replyCount%2Cpresentation&domain=NeurIPS.cc%2Fyear%2FConference&limit=25&'
            ],
    
    "Nips_dataset":['https://api2.openreview.net/notes?content.venue=NeurIPS%20year%20Datasets%20and%20Benchmarks%20Oral&domain=NeurIPS.cc%2Fyear%2FConference&limit=25&',
                    'https://api2.openreview.net/notes?content.venue=NeurIPS%20year%20Datasets%20and%20Benchmarks%20Spotlight&domain=NeurIPS.cc%2Fyear%2FConference&limit=25&',
                    'https://api2.openreview.net/notes?content.venue=NeurIPS%20year%20Datasets%20and%20Benchmarks%20Poster&domain=NeurIPS.cc%2Fyear%2FConference&limit=25&',
                    'https://api2.openreview.net/notes?content.venue=Submitted%20to%20NeurIPS%20year%20Datasets%20and%20Benchmarks&domain=NeurIPS.cc%2Fyear%2FConference&limit=25&'
            ],
    
    "COLM":['https://api2.openreview.net/notes?content.venue=COLM&details=replyCount%2Cpresentation&domain=colmweb.org&limit=25&'],
    
}

#Considering the quality of the paper and the stability of its reception, we only consider the long/short/findings paper of ACL/NAACL.
ACL_types={
    "ACL":["long","short","findings"],
    "NAACL":["long","short","findings"],
    "EMNLP":["main","findings"]
}

CV_urls={
    "CVPR":"https://openaccess.thecvf.com/CVPRyear?day=all",
    "ICCV":"https://openaccess.thecvf.com/ICCVyear?day=all",
    "ECCV":"https://www.ecva.net/papers.php"
}



headers = {
        'cookie': '_ga=GA1.1.926646815.1652076197; __cuid=6e7a75c726ae4dd39d64b75000eba48a; amp_fef1e8=eec1aab1-0a18-42ea-8ce6-0d89117b5bf6R...1ha9bookf.1ha9bp5nc.4.1.5; _ga_3TRQ40799D=GS1.1.1694678934.1.1.1694679018.0.0.0; _ga_GTB25PBMVL=GS1.1.1706703827.4.1.1706704498.0.0.0',
        'origin': 'https://openreview.net',
        'referer': 'https://openreview.net/',
        'user-agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

def get_content_venue(url:str):
    parsed_url = urlparse(url)
    query_params = parse_qs(parsed_url.query)
    content_venue = query_params.get('content.venue', [None])[0]
    return content_venue

def get_acl_file_count(url: str, conference_name:str, year:str, paper_type: str):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    links = soup.find_all('a', href=True)

    pattern = re.compile(rf'aclanthology\.org/{year}\.{conference_name}-{paper_type}\.\d+\.pdf')
    matching_links = [link['href'] for link in links if pattern.search(link['href'])]

    return len(matching_links)

def get_content(request, retries=3, delay=1):
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

def get_paper_nums(url:str):
    
    response = requests.get(url, headers=headers)
    html_str = json.loads(response.content.decode())
    count = html_str['count']
    
    return count

def write_to_outpath(final_content:dict,count:int,out_path:str):
    if os.path.exists(out_path):
        with open(out_path, 'r', encoding='utf-8') as json_file:
            try:
                existing_content = json.load(json_file)
            except json.JSONDecodeError:
                existing_content = {}
        existing_content.update(final_content)
    else:
        existing_content = final_content
                
    with open(out_path, 'w', encoding='utf-8') as json_file:
        json.dump(existing_content, json_file, ensure_ascii=False, indent=4)
        
    print(f"Totally obtained {count} paper's title and abstract to {out_path}")

def get_id(url, offset):
    id_list = []
    
    for i in range(offset):
        response = requests.get(url + 'offset=' + str(i * 25), headers=headers)
        html_str = json.loads(response.content.decode())
        jsonpath_expr = parse('$..id')
        id_list.extend([match.value for match in jsonpath_expr.find(html_str)])
        
    return id_list

def increment_last_number_in_url(url: str) -> str:
    match = re.search(r'(\d+)/$', url)
    
    if match:
        number = int(match.group(1))
        incremented_number = number + 1
        new_url = re.sub(r'(\d+)/$', f'{incremented_number}/', url)
        return new_url
    
    else:
        raise ValueError("URL does not match the expected format")

def get_info_acl(url):
    try:
        response = requests.get(url)
        response.raise_for_status()  # 如果响应状态码不是200，会引发HTTPError异常
        html_content = response.content
        soup = BeautifulSoup(html_content, 'html.parser')

        title = soup.find('meta', {'property': 'og:title'})['content']
        abstract = soup.find('div', class_='card-body acl-abstract').find('span').text
        
    except requests.exceptions.RequestException as e:
        title, abstract = None, None

    return title, abstract

def download_paper_info(name:str,year:str,batch_size=10):
    current_directory = os.path.dirname(os.path.abspath(__file__))
    target_directory = os.path.join(current_directory, "Title_and_Abstract")
    if not os.path.exists(target_directory):
        os.makedirs(target_directory)
    out_path = os.path.join(target_directory, f"{name}{year}.json")    
    
    if name in Openreview_urls:
        urls = Openreview_urls[name]
        cnt = 0
        i = 0
        final_content = {}
        print(f"There are {len(urls)} batches of paper to be processed.")
        print("--------------------------------------------------------")
        time.sleep(1)
        for url in urls:
            i += 1
            ids=[]
            url = url.replace("year", year)
            base_url="https://api2.openreview.net/notes?forum="
            content_venue = get_content_venue(url)
            print(f"Getting the {i}th batch of papers ids...")
            print("--------------------------------------------------------")
            paper_nums = get_paper_nums(url)
            ids = get_id(url,paper_nums//25+1)
            print(f"Finished getting ids, start to get the title and abstract of the papers:")
            for id in ids:
                url_of_id=base_url+id+'&content.venue='+urllib.parse.quote(content_venue)
                request=urllib.request.Request(url_of_id,headers=headers)
                content = get_content(request)
                data = json.loads(content)
                title = data["notes"][0]["content"]["title"]["value"]
                abstract = data["notes"][0]["content"]["abstract"]["value"]
                file_content={title:abstract}
                if title:
                    print(f"Processed: {title} successfully.")
                else:
                    break
                final_content.update(file_content)
                cnt += 1
                
                time.sleep(0.3)
                
                if cnt % batch_size == 0:
                    write_to_outpath(final_content,cnt,out_path)
                    final_content = {}
            if final_content:
                write_to_outpath(final_content,cnt,out_path)
                final_content = {}
                
    elif name in ACL_types:
        types = ACL_types[name]
        base_url = "https://aclanthology.org/events/"
        specific_url="https://aclanthology.org/events/"+name.lower()+"-"+year+"/"
        for type in types:
            cnt = 0
            final_content = {}
            paper_nums = get_acl_file_count(specific_url,name.lower(),year,type)
            print(f"There are {paper_nums-1} {type} papers to be processed:")
            print("--------------------------------------------------------")
            while cnt + 1 < paper_nums: 
                url = f"https://aclanthology.org/{year}.{name.lower()}-{type}.{cnt+1}/"
                title, abstract = get_info_acl(url)
                if title:
                    print(f"Processed: {title} successfully.")
                file_content={title:abstract}
                final_content.update(file_content)
                cnt += 1
                time.sleep(0.3)
                
                if cnt % batch_size == 0:
                    write_to_outpath(final_content,cnt,out_path)
                    final_content = {}
            if final_content:
                write_to_outpath(final_content,cnt,out_path)
                final_content = {}
                
    elif name in CV_urls and name != "ECCV":
        url = CV_urls[name].replace("year", year)
        cnt = 0
        final_content = {}
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')
        ptitle_elements = soup.find_all('dt', class_='ptitle')
        paper_links = [element.find('a')['href'] for element in ptitle_elements]
        base_url = "https://openaccess.thecvf.com"
        for link in paper_links:
            url = base_url + link
            response = requests.get(url)
            soup = BeautifulSoup(response.content, 'html.parser')
            title = soup.find('meta', {'name': 'citation_title'})['content']
            abstract = soup.find('div', {'id': 'abstract'}).text.strip()
            file_content={title:abstract}
            if title:
                print(f"Processed: {title} successfully.")
            else:
                break
            final_content.update(file_content)
            cnt += 1
            time.sleep(0.3)
            if cnt % batch_size == 0:
                    write_to_outpath(final_content,cnt,out_path)
                    final_content = {}
        if final_content:
            write_to_outpath(final_content,cnt,out_path)
            final_content = {}
        
    elif name in CV_urls and name == "ECCV":
        url = CV_urls[name]
        paper_links = []
        cnt = 0
        final_content = {}
        response = requests.get(url)
        response.encoding = 'utf-8'
        html_content = response.text
        soup = BeautifulSoup(html_content, "html.parser")
        
        for a_tag in soup.find_all("a", href=True):
            href = a_tag['href']
            if "papers/eccv_2024/papers_ECCV/html/" in href:
                full_url = f"https://www.ecva.net/{href}"
                paper_links.append(full_url)
        for link in paper_links:
            response = requests.get(link)
            response.encoding = 'utf-8'
            html_content = response.text
            soup = BeautifulSoup(html_content, "html.parser")
            title = soup.find("div", id="papertitle").text.strip()
            abstract = soup.find("div", id="abstract").text.strip()
            file_content={title:abstract}
            if title:
                print(f"Processed: {title} successfully.")
            else:
                break
            final_content.update(file_content)
            cnt += 1
            time.sleep(0.3)
            if cnt % batch_size == 0:
                    write_to_outpath(final_content,cnt,out_path)
                    final_content = {}
        if final_content:
            write_to_outpath(final_content,cnt,out_path)
            final_content = {}        
    else:
        print("The conference are not in the list.")
        return

download_paper_info("ICLR","2024")    
        
# if __name__ == "__main__":
#     if len(sys.argv) != 3:
#         print("Usage: python run.py <arg1> <arg2>")
#     else:
#         arg1 = sys.argv[1]
#         arg2 = sys.argv[2]
#         print(f"{arg1}, {arg2}")
