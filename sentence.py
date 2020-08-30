from bs4 import BeautifulSoup
import requests

def getSentence():
    url = "http://www.esdict.cn/home/dailysentence"
    req = requests.get(url)
    soup = BeautifulSoup(req.content, "lxml")

    sen = soup.find("p", class_="sect_es").text
    trans = soup.find("p", class_="sect-trans").text

    return sen, trans

