import argparse,requests
from threading import Thread
from termcolor import colored
from queue import Queue
def get_args():
    parser=argparse.ArgumentParser(description="This tool checks for crlf injection tools!",epilog="Sayonara👋!")
    
    parser.add_argument('-u','--url',dest="url",help="Specify the url",metavar="",required=True)
    parser.add_argument('-H','--Headers',metavar="",dest="headers",help="Specify the headers , if required for authentication !",nargs='*')
    return parser.parse_args()

def injection(url):
    global payloads,headers
    while payloads.not_empty:
        payload=payloads.get()
        
        req=f"https://{url}/{payload}"
        try:
            if headers:
                response=requests.get(url=req,timeout=5,headers=headers)
            else:
                response=requests.get(url=req,timeout=5)
        except:
            pass
        else:
            print(f"Request : {req}")
            headers=response.headers
            for header in headers:
                if headers[header]=='crlf_injection':
                    print(colored(f"[+] Vulnerable to CRLF Header injection, Header Used : {header} and Value {headers[header]} , Payload:{payload}",'green',attrs=['bold']))
                elif 'crlf injection' in response.text:
                    print(colored(f"[+] Crlf Injection Found in body!, Payload {payload}",'green',attrs=['bold']))
    else:
        print("[-] Not vulnerable To clrf injection")
        
def handle_threads(threads,url):
    for _ in range(threads):
        T=Thread(target=injection,args=(url,))
        T.daemon=True   
        T.start()
            
    with open(payload_file,'r') as f:
        for payload in f.readlines():
            payloads.put(payload.strip())
        payloads.join()
if __name__=="__main__":
    
    from os import path
    from sys import exit
    
    payload_file='payloads.txt'
    
    if not path.exists(payload_file):
        print(colored("[-] Default payload file not found",'red',attrs=['bold']))
        exit(-1)
        
    Header=dict()
    arguments=get_args()
    headers=arguments.headers

    if headers:
        for header in headers:
            Header[header.split(':')[0]]=header.split(':')[1]

    url=arguments.url
    threads=10
    payloads=Queue()
    handle_threads(threads=threads,url=url)
    