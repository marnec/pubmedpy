import xml.etree.ElementTree as et
from article import Article
from urllib import request
import sys
import time
import gzip
import os


def iter_articles(xml_file):
    ext = os.path.splitext(xml_file)[-1]
    if ext == ".xml":
        open_f = open
    elif ext == (".gz" or ".gzip"):
        open_f = gzip.open
    else:
        raise ValueError("Expecting file extension xml, gz or gzip. Got {}".format(ext))

    with open_f(xml_file) as f:
        for event, elem in et.iterparse(f, events=("end",)):
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


def bulk_download_articles(db, n=None):
    oa_ftp_dbs = {'epmc', 'pmc'}

    if db not in oa_ftp_dbs:
        raise ValueError('Accepted values for db {}; got {}'.format(oa_ftp_dbs, db))

    elif db == 'epmc':
        _epmc_ftp_bulkdownload(n)


def _epmc_ftp_bulkdownload(n):
    baseurl = 'https://europepmc.org/ftp/oa'
    lines = request.urlopen(baseurl).read().decode("utf-8").split('\n')
    lines = [l.split()[4:] for l in lines if "xml.gz" in l]
    size, *date, links = zip(*lines)
    size = list(map(lambda s: "{:.1f}MB".format(int(s) / 1000000), size))
    date = list(map(" ".join, zip(*date[:-1])))
    links = list(map(lambda s: "{}/{}".format(baseurl, s.split('>')[0][6:-1]), links))

    for i, link in enumerate(links):
        if n is None or (n is not None and i < n):
            request.urlretrieve(links[0], 'file', reporthook)
        else:
            break



#TODO: investigate 'utf-8' codec can't decode byte 0x8b in position 1: invalid start byte
def file_type(filename):
    compression_signatures = {
        "\x1f\x8b\x08": "gz",
        "\x42\x5a\x68": "bz2",
        "\x50\x4b\x03\x04": "zip"
    }

    max_len = max(len(x) for x in compression_signatures)

    with open(filename, encoding='utf-8') as f:
        file_start = f.read(max_len)
    for magic, filetype in compression_signatures.items():
        if file_start.startswith(magic):
            return filetype