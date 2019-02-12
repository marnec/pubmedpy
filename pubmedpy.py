import xml.etree.ElementTree as et
from article import Article
from urllib import request
import sys
import time



def iter_articles(xml_file):
    for event, elem in et.iterparse(xml_file, events=("end",)):
        if event == 'end':
            if elem.tag == 'article':
                yield Article(elem)


def reporthook(count, block_size, total_size):
    global start_time
    if count == 0:
        start_time = time.time()
        return
    duration = time.time() - start_time
    progress_size = int(count * block_size)
    speed = int(progress_size / (1024 * duration))
    percent = min(int(count*block_size*100/total_size),100)
    sys.stdout.write("\r...%d%%, %d MB, %d KB/s, %d seconds passed" %
                    (percent, progress_size / (1024 * 1024), speed, duration))
    sys.stdout.flush()


def download_epmc_files(n=None):
    baseurl = 'https://europepmc.org/ftp/oa'
    lines = request.urlopen(baseurl).read().decode("utf-8").split('\n')
    lines = [l.split()[4:] for l in lines if "xml.gz" in l]
    size, *date, links = zip(*lines)
    size = list(map(lambda s: "{:.1f}MB".format(int(s)/1000000), size))
    date = list(map(" ".join, zip(*date[:-1])))
    links = list(map(lambda s: "{}/{}".format(baseurl, s.split('>')[0][6:-1]), links))


    for i, link in enumerate(links):
        if n is None or i < n:
            request.urlretrieve(links[0], 'file', reporthook)
        else:
            break
