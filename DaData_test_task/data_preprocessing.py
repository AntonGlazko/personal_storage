"""" This code designed for data preparation."""

import pandas as pd
import numpy as np

import requests
from urllib.request import urlopen
from urllib.parse import urlencode
from io import BytesIO
from zipfile import ZipFile
from bs4 import BeautifulSoup
import lxml

# the class implemented to downloading, reading and concatenating data
class DataCollector:

    def __init__(self, data=None):
        self.data = data

    def parse_rospatent(self, headers):
        url = 'https://rospatent.gov.ru/opendata/7730176088-tz'

        query = requests.get(url=url, headers=headers, verify=False)
        content = query.content

        soup = BeautifulSoup(content, 'lxml')
        data_url = soup.find(class_='table').find_all('a', href=True)[1]['href']
        csv_file = urlopen(data_url)
        self.data = csv_file
        return self


    def get_zip_yandex_disk(self, public_key):

        base_url = 'https://cloud-api.yandex.net/v1/disk/public/resources/download?'
        url = base_url + urlencode(dict(public_key=public_key))
        response = requests.get(url)
        download_link = response.json()['href']
        download_response = urlopen(download_link)
        zip_file = ZipFile(BytesIO(download_response.read()))
        file_names = list([x.filename for x in zip_file.infolist()])
        print(f'zip file contains {file_names}')
        self.data = zip_file
        return self

    def read_data(self, file_type='csv', delimiter=',', zip_file=True):

        if zip_file is True:
            file_names = list([x.filename for x in self.data.infolist()])
            data_dict = dict()
            for file in file_names:
                if file_type == 'parquet':
                    data_piece = pd.read_parquet(self.data.open(file), engine='pyarrow')
                    data_dict[file.strip().split('.')[0]] = data_piece
                elif file_type == 'csv':
                    data_piece = pd.read_csv(self.data.open(file), sep=delimiter)
                    data_dict[file.strip().split('.')[0]] = data_piece
            self.data = data_dict
            return self
        else:
            if file_type == 'parquet':
                self.data = pd.read_parquet(self.data, engine='pyarrow')
            elif file_type == 'csv':
                self.data = pd.read_csv(self.data, sep=delimiter)
            return self

    def concat_parts(self):

        result_df = pd.DataFrame()
        iterable = self.data.values()
        for file in iterable:
            result_df = pd.concat([result_df, file], ignore_index=True)
        self.data = result_df
        return self

    def get_data(self, file_name=None):
        if file_name is None:
            return self.data
        else:
            return self.data[file_name]