#!/usr/lib/ python3
from pyspark.sql import SparkSession, Row
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import logging
import os
import re
import pandas as pd
import requests
import re
import urllib.request
import lzma
import shutil
import time
import sys
import getopt


class MTA_Bus_Route_Analysis_Downloader:
    def __init__(self) -> None:
        self.source_path = '/mnt/data-files'
        self.url = 'http://web.mta.info/developers/MTA-Bus-Time-historical-data.html'
        self.working_dir = os.path.join(self.source_path, 'extracting')
        self.log_file = os.path.join(self.source_path, 'log')
        self.pattern = 'http://s3.amazonaws.com/MTABusTime/AppQuest3/MTA-Bus-Time_.'
        self.file_count = 100
        self.files_processed = 0
        self.help = ''

    def get_file_list(self):
        sql = SparkSession.builder\
            .appName("download-app")\
            .config("spark.jars", "/opt/spark-apps/postgresql-42.2.22.jar")\
            .config("spark.sql.execution.arrow.pyspark.enabled", "true")\
            .getOrCreate()
        sc = sql.sparkContext
        r = requests.get(self.url)

        soup = BeautifulSoup(r.text, 'html.parser')

        anchors = soup.find_all('a', attrs={'href': re.compile(self.pattern)})

        url_list = []
        for a in anchors:
            url_list.append(a.get('href'))
        
        listing = sc.parallelize(url_list[:int(self.file_count)])

        app.file_count = listing.count()

        logging.info(
            f'{str(datetime.now())[:23]} | {app.file_count} file(s) to download...')
        listing.foreach(lambda url: self.download(url))

    def download(self, url):
        fileparts = url.split('_')
        print(fileparts)
        try:
            if (fileparts and len(fileparts) == 2):
                filename = fileparts[1][1:]
                compressed_file = os.path.join(self.working_dir, filename)
                urllib.request.urlretrieve(url, compressed_file)
            else:
                raise NameError(
                    'file URL expected to have only one underscore (_)!')

            decompressed_file = compressed_file.replace('txt.xz', 'txt')
            if (not os.path.exists(decompressed_file)):
                with lzma.open(compressed_file, 'rb') as compressed:
                    with open(decompressed_file, 'wb') as decompressed:
                        shutil.copyfileobj(compressed, decompressed)
                os.remove(compressed_file)
                shutil.move(decompressed_file, self.source_path)
            self.files_processed += 1
        except NameError as e:
            logging.error(f'{str(datetime.now)[:23]} | {e}')

    def check_params(self, argv):
        try:
            self.help = '{0} -f <file-count>'.format(argv[0])
            opts, args = getopt.getopt(argv[1:], 'hf:', ['help', 'file-count='])	         

        except Exception as e:
            self.handle_exception(e)

        for opt, arg in opts:
            if opt in ("-h", "--help"):
                self.handle_exception(Exception('Error - --help option passed to module!'))
            elif opt in ("-f", "--file-count"):          
                self.file_count = arg
            else:
                self.handle_exception(Exception('Error - invalid option passed to module!'))



def main(argv):
    global app
    app = MTA_Bus_Route_Analysis_Downloader()

    app.check_params(argv)

    # Clear any existing tree
    for root, dirs, files in os.walk(app.source_path):
        for f in files:
            os.unlink(os.path.join(root, f))
        for d in dirs:
            shutil.rmtree(os.path.join(root, d))

    logging.basicConfig(level=logging.INFO, filename=app.log_file,
                        format='%(levelname)s | DOWNLOADER | %(message)s')

    # Create working directory
    os.mkdir(app.working_dir)

    total_delta = timedelta(0)
    start = datetime.now()
    logging.info(f'{str(start)[:23]} | Started downloading...')
    app.get_file_list()
    end = datetime.now()
    logging.info(f'{str(end)[:23]} | Finished downloading.')
    total_delta = end-start
    logging.info(f'{str(end)[:23]} | Total download time: {total_delta}')


if __name__ == '__main__':
    main(sys.argv)
