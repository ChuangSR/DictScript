import requests
from lxml import etree
import hashlib
import os


def get_pinyin(x: etree._Element):
    span = x.xpath("./p/span[2]")[0]
    pinyin = span.xpath("./text()")[0]
    pinyin_url = span.xpath(".//a")[0].xpath("./@data-src-mp3")[0]
    return pinyin, pinyin_url


def get_phonetic_notation(x: etree._Element):
    phonetic_notation = x.xpath("./p/span[2]/text()")[0]
    return phonetic_notation


# 获取部首，那么既然数部首我为什么写自由基的英语呢？
# md,中文独有的词汇,那个百度翻译就是对于他的一段英文解释，写个棒槌啊！
# 写出来你更看不懂
def get_radicals(x: etree._Element):
    radicals = x.xpath("./p/text()")[0]
    return radicals[-1]


def get_total_stroke(x: etree._Element):
    total_stroke = x.xpath("./p/text()")[0]
    return total_stroke[-1]


def get_other_radicals_stroke(x: etree._Element):
    other_radicals_stroke = x.xpath("./p/text()")[0]
    return other_radicals_stroke[-1]


# 下载语音文件
def download(data, url):
    headers = {
        'authority': 'zidian.gushici.net',
        'range': 'bytes=0-',
        'referer': 'https://zidian.gushici.net/d/mp3/c%C7%8Eo.mp3',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0',
    }

    response = requests.get(fr'https:{url}', headers=headers)

    # 数据加盐，防止被逆推
    data += "nanobot"
    md5 = hashlib.md5(data.encode('utf8')).hexdigest()
    path = f"./{md5}"

    if not os.path.exists(path):
        os.mkdir(path)

    path += f"/{data[0]}.mp3"
    with open(path, mode="wb") as mp3:
        mp3.write(response.content)

    return path


def Main(data):
    data_bean = {}
    headers = {
        'authority': 'zidian.gushici.net',
        'referer': 'https://zidian.gushici.net/',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0',
    }

    params = {
        'zi': data,
    }

    response = requests.get('https://zidian.gushici.net/search/zi.php', params=params, headers=headers)
    response.encoding = "utf-8"
    tree = etree.HTML(response.text)
    trs = tree.xpath("//main//table//table[1]//table/tr")

    # 对于第一部分的td进行解析
    tds = trs[0].xpath("./td")

    # 解析拼音，及其下载路径
    pinyin, pinyin_url = get_pinyin(tds[0])
    data_bean["拼音"] = pinyin
    path = download(data, pinyin_url)
    data_bean["拼音语音文件路径"] = path

    # 解析注音
    phonetic_notation = get_phonetic_notation(tds[1])
    data_bean["注音"] = phonetic_notation

    # 解析部首
    radicals = get_radicals(tds[2])
    data_bean["部首"] = radicals

    # 对于第二部分的td进行解析
    tds = trs[1].xpath("./td")

    # 获取总笔画
    total_stroke = get_total_stroke(tds[0])
    data_bean["总笔画"] = total_stroke

    # 部首外笔画
    other_radicals_stroke = get_other_radicals_stroke(tds[1])
    data_bean["部首外笔画"] = other_radicals_stroke

    # 对于第三部分进行解析
    font_structure = trs[3].xpath("./td[1]/p/text()")[0][1:]
    data_bean["字体结构"] = font_structure

    # 解析基本字义
    basic_word_meanings = []

    lis = tree.xpath("//main//div[@class='nr-box nr-box-shiyi jbjs']/div[2]/ol/li")
    for i in lis:
        basic_word_meanings.append(i.xpath("./text()")[0])
    data_bean["基础字意"] = basic_word_meanings
    return data_bean

if __name__ == '__main__':
    Main('草')
