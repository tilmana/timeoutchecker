import time
import requests
import argparse
import sys

parser = argparse.ArgumentParser(description="""Script for testing regular and absolute Session Timeout.""")
parser.add_argument('-d', '--delay', type=int, default=60, help='delay between requests in seconds. use -m to convert to minutes automatically (default: 60)')
parser.add_argument('-f', '--file', type=str, help='file containing HTTP request to parse and run (required)', required=True)
parser.add_argument('-p', '--port', type=str, default="443", help='port of remote server (default 443)')
parser.add_argument('-m', '--minutes', action='store_true', help='set delay units from seconds to minutes')
parser.add_argument('-n', '--nossl', action='store_true', help='disable SSL')
parser.add_argument('-p', '--proxy', help='proxies to use for HTTP requests')
args = parser.parse_args()

if args.proxy:
    proxies = {
        "http": args.proxy,
        "https": args.proxy
    }

def ingestHeaders(lines):
    headers = []
    headersContent = []
    for index in range(1, len(lines)):
        if lines[index] != "\n" and lines[index] != "":
            headers.append(lines[index].split(":")[0])
            headersContent.append(''.join(str(content) for content in lines[index].split(": ")[1:]))
        break
    return headers, headersContent

with open(args.file, "r") as f:
    lines = []
    content = f.read()
    lines = content.split("\n")
    headers, headersContent = ingestHeaders(lines)
    method = lines[0].split(" ")[0]
    path = lines[0].split(" ")[1]
    target = headersContent[0]
    headerValues = {}
    dataValues = {}
    for value in range(len(headers)):
        headerValues[headers[value]] = headersContent[value]
    f.close()
    if lines[-1].find("=") != -1 and lines[-2] == "":
        x = lines[-1].split("&")
        for i in x:
            dataValues[i.split("=")[0]] = i.split("=")[1]
    count = 0
    if args.minutes:
        delay = args.delay * 60
    else:
        delay = args.delay
    try:
        if method == "GET":
            while True:
                count += 1
                print(f"[+] Sending request #{count}")
                if args.nossl:
                    try:
                        r = requests.get(url="http://" + target + ":" + args.port + path, headers=headerValues, proxies=None) # default HTTPS unless user specifies
                    except requests.exceptions.ConnectionError:
                        print("[!] Error: host may be down! Exitting...")
                        sys.exit(-1)
                else:
                    r = requests.get(url="https://" + target + ":" + args.port + path, headers=headerValues, proxies=None) # default HTTPS unless user specifies
                time.sleep(delay)
        elif method == "POST":
            while True:
                count += 1
                print(f"[+] Sending request #{count}")
                if args.nossl:
                    r = requests.post(url="http://" + target + ":" + args.port + path, headers=headerValues, data=dataValues, proxies=None) # default HTTPS unless user specifies
                else:
                    r = requests.post(url="https://" + target + ":" + args.port + path, headers=headerValues, data=dataValues, proxies=None) # default HTTPS unless user specifies
                time.sleep(delay)
    except requests.exceptions.ConnectionError:
        print("[!] Error: host may be inaccessible. Exiting...")
        sys.exit(-1)

