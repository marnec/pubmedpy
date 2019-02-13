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
    percent = min(int(count*block_size*100/total_size), 100)

    sys.stdout.write("\r...{:.1f}%, {:.1f} MB, {:.2f} KB/s, {} seconds passed".format(
        percent, progress_size / (1024 * 1024), speed, duration))

    sys.stdout.flush()


def bulk_download_articles(db, n=None, use=None):
    db_opts = {"epmc", "pmc"}
    use_opts = {"comm", "non_comm", "any"}

    if db not in db_opts:
        raise ValueError("Accepted values for db {}; got {}".format(db_opts, db))

    if db == "pmc" and use is None:
        raise ValueError("Argument 'use' must be not None when db=pmc")

    if use not in use_opts:
        raise ValueError("Accepted values for use {}; got {}".format(use_opts, use))

    if db == "epmc":
        _epmc_ftp_bulkdownload(n)

    elif db == "pmc":
        _pmc_ftp_bulkdownload(n, use)


def _epmc_ftp_bulkdownload(n):
    baseurl = 'https://europepmc.org/ftp/oa/'
    lines = request.urlopen(baseurl).read().decode("utf-8").split('\n')
    lines = [l.split()[4:] for l in lines if "xml.gz" in l]
    size, *date, filenames = zip(*lines)
    # size = list(map(lambda s: "{:.1f}MB".format(int(s) / 1000000), size))
    # date = list(map(" ".join, zip(*date[:-1])))
    filenames = list(map(lambda s: s.split('>')[0][6:-1], filenames))

    for i, fname in enumerate(filenames):
        if n is None or (n is not None and i < n):
            link = baseurl + fname
            request.urlretrieve(link, fname, reporthook)
        else:
            break


def _pmc_ftp_bulkdownload(n, use):
    baseurl = 'ftp://ftp.ncbi.nlm.nih.gov/pub/pmc/oa_bulk/'
    lines = request.urlopen(baseurl).read().decode("utf-8").split('\n')
    lines = [l.split()[4:] for l in lines if "xml.tar.gz" in l]
    size, *date, filenames = zip(*lines)
    # size = list(map(lambda s: "{:.1f}MB".format(int(s) / 1000000), size))
    # date = list(map(" ".join, zip(*date[:-1])))

    for i, fname in enumerate(filenames):
        if n is None or (n is not None and i < n):
            if use == "any" or use in fname:
                link = baseurl + fname
                request.urlretrieve(link, fname, reporthook)
        else:
            break


# TODO: investigate 'utf-8' codec can't decode byte 0x8b in position 1: invalid start byte
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
