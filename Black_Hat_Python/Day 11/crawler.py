import requests,argparse
from sys import exit
from termcolor import colored
from bs4 import BeautifulSoup
import re


def get_args():
    parser=argparse.ArgumentParser()
    parser.add_argument('-u','--url',dest='url',help="Specify the urls , Provide it along http/https ",required=True)
    return parser.parse_args()

def crawler(url):
    try:
        response=requests.get(url=f"https://{url}",timeout=3,allow_redirects=True)
    except requests.exceptions.ConnectionError:
        print("[-] Connection Timed out!")
    except Exception as err:
        print(err)
    else:
        global subdomains,links,jsfiles
        soup=BeautifulSoup(response.text,'html.parser')
        subdomain_query=fr"https?://([a-z0-9]+[.])*{url}"
        email_query=fr"([a-zA-Z0-9._-]+@[a-zA-Z0-9._-]+\.[a-zA-Z0-9_-]+)"

        for link in soup.find_all('a'):
            link_text=link.get('href')
            if re.match(subdomain_query,link_text) and link_text not in links:
                subdomains.append(link_text)
            if link_text in url:
                if 'http' not in link_text and (f"https://{url}{link_text}") not in links:
                    new_link='https://'+url+link_text
                    links.append(new_link)
                    crawler(new_link)
                elif '#' in link_text:
                    link=link_text.split('#')[0]
                    if link not in links:
                        links.append(link)
                        crawler(link)
        for file in soup.find_all('script'):
            script_src=file.get('src')
            if script_src and script_src not in jsfiles:
                jsfiles.append(script_src)
                    
def print_banner(url):
    from datetime import datetime
    print("-"*80)
    print(colored(f"Http Form bruteforcing starting at {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}",'yellow',attrs=['bold']))
    print("-"*80)
    print("[*] Url".ljust(20," "),":",f"{url}")
    print("-"*80)

def print_output(subdomains,links,jsfiles):
    if subdomains:
        for subdomain in subdomains:
            print(f"[+] Subdomains : {subdomain}")
    print()
    if links:
        for link in links :
            print(f"[+] Links : {link}")
    print()
    if jsfiles:
        for file in jsfiles:
            print(f"[+] Js Files : {file}")
            
            
if __name__=="__main__":
    arguments=get_args()
    url=arguments.url
    print_banner(url)
    subdomains=[]
    links=[]
    jsfiles=[]
    crawler(url)
    print_output(subdomains,links,jsfiles)
    