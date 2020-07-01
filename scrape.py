import requests
from urllib.request import urlopen, Request
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
import csv
header= {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) ' 
                        'AppleWebKit/537.11 (KHTML, like Gecko) '
                        'Chrome/23.0.1271.64 Safari/537.11',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
            'Accept-Encoding': 'none',
            'Accept-Language': 'en-US,en;q=0.8',
            'Connection': 'keep-alive'}

#save links
list_link=[]
for a in range(47):
    url="http://www.medguideindia.com/show_generics.php?nav_link=&pageNum_rr="+str(a)+"&nav_link=&selectme="+str(a)
    req=Request(url=url, headers=header)
    page_html=urlopen(req).read()
    soup=BeautifulSoup(page_html, 'html.parser')

    for mytable in soup.find_all("table", {"class": "tabsborder2"}):
        c=0
        for trs in mytable.find_all('tr'):
            c=c+1
            if c==52:
                break
            links = trs.find_all('a')
            tds = trs.find_all('td')
            temp=tds[3].find('a')
            if not temp==None:
                list_link.append("http://www.medguideindia.com/"+temp.get("href"))
        print(str(a+1)+ " of 48 links extracted")  
df = pd.DataFrame(list_link)
df.to_csv('links.csv', index=False)
print("")

#save data of medicine
my_list=[]
c=0
for url in list_link:
    c=c+1
    try:
        req=Request(url=url, headers=header)
        page_html=urlopen(req).read()
        soup=BeautifulSoup(page_html, 'html.parser')
    except:
        print("Error in getting response from website!")

    h=soup.find("td", {"class": "rd-txt"}).text.strip().replace("Matched Brand/Brands of , ","")
    ok=h.replace("Matched Brand/Brands of","")
    for mytable in soup.find_all("table", {"class": "tabsborder2"}):
        for trs in mytable.find_all('tr'):
            tds = trs.find_all('td', {"class": ["red-txt","mosttext"]})
            if(tds):
                row = [elem.text.strip() for elem in tds]
                if(len(row)==1):
                    temp=row
                else:
                    with open('pharma drugs.csv','a') as f:
                        writer = csv.writer(f)
                        writer.writerow([ok]+temp+row)
    print(str(c)+" Pages Scraped")
