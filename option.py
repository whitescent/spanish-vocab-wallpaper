from bs4 import BeautifulSoup
from word import *
import random
import requests
import json

dic = dict()
word_dic = dict()

word = []
Data = [Word() for i in range(0, 10)]   # 初始化 10 个类数组


def serchWord(word, index):

    # 爬虫，获取翻译，词性，例句

    url = "http://www.esdict.cn/dicts/es/" + word
    req = requests.get(url)
    soup = BeautifulSoup(req.content, "lxml")
    word = soup.find("span", class_="word")     # 单词
    cara = soup.find("span", class_="cara")     # 词性
    exp = soup.find("span", class_="exp")       # 解释
    eg = soup.find("span", class_="eg")         # 例句

    if word is None or exp is None:
        return 0
    else:
        if word is not None:
            Data[index].word = word.text
        if cara is not None:
            Data[index].cara = cara.text

        if exp is not None:
            expstr = ''.join([str(i) for i in exp.contents])    # 将获取到的解释逐行分布存储为一个列表类型
            Data[index].exp = list(filter(lambda x: x, expstr.split("<br/>")))

        if eg is not None:
            Data[index].eg = eg.text
        return 1

# 取得随机数

def randomNumber():
    return random.randint(1, 57803)


def getWords():
    count = 1
    index = 0

    # 逐行读取 word.txt 中的单词并存在字典变量

    with open('word.txt', encoding="utf-8") as lines:
        for line in lines:
            line = line.strip('\n').strip('\r')
            word_dic[count] = line
            count += 1

    # 取 10 个单词，这里可以自己决定

    while True:
        if index == 10:
            break
        while True:
            num = randomNumber()
            if dic.get(num) is None:
                dic[num] = 1    # 去重
                if serchWord(word_dic[num], index) == 1:
                    index += 1
                    break

    wordStrs = []
    for i in Data:
        wordStrs.append(json.dumps(i.__dict__)) # 将词库中的单词信息转化为 JSON 格式

    wordStr = "[" + ",".join(wordStrs) + "]"

    return wordStr

