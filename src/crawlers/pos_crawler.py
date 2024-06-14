import traceback
import json
import html
import logging
import uuid
from abc import ABC
from datetime import date
from decimal import Decimal

import requests
import pycurl
import certifi
from io import BytesIO
from bs4 import BeautifulSoup

from urllib.parse import urlparse, parse_qs

from src.core.db.base import upsert_pos_schedule
from src.entities.crawl_pos_result import CrawlNewPosResult
from src.entities.pos_schedule import PosSchedule
from src.utils.config import get_pos_schedule_url


class BasePosCrawler(ABC):
    def __init__(self, logging_prefix=""):
        self.logger = logging.getLogger(logging_prefix)

    def debug(self, msg: str):
        self.logger.debug(msg)

    def info(self, msg):
        self.logger.info(msg)

    def warn(self, msg):
        self.logger.warning(msg)

    def error(self, msg):
        self.logger.error(msg)

    def get_traceback(self, e: Exception) -> str:
        return f'\n{"".join(traceback.format_tb(e.__traceback__))}'

    def get_html(self, url):
        response = requests.get(url)
        if response.status_code == 200:
            html = response.text
            soup = BeautifulSoup(html, 'html.parser')
            return soup
        else:
            return response.status_code

    def gen_uuid(self, ):
        return str(uuid.uuid4())

    def reformat_price_data(self, price: str):
        if price:
            if price.find('.') != -1:
                return float(price.replace(',', ''))
            else:
                return int(price.replace(',', ''))
        else:
            return price

    def change_date_format(self, date_str):
        # 문자열을 '~'로 분리하여 시작 날짜와 종료 날짜 추출
        start_date_str, end_date_str = date_str.split('~')

        # 종료 날짜에 연도를 추가
        start_year = start_date_str.split('.')[0]
        end_date_str = f'{start_year}.{end_date_str}'

        # 문자열을 분할하여 각 구성 요소 추출
        start_year, start_month, start_day = map(int, start_date_str.split('.'))
        end_year, end_month, end_day = map(int, end_date_str.split('.'))

        # date 객체로 변환
        start_date = date(start_year, start_month, start_day)
        end_date = date(end_year, end_month, end_day)
        return start_date, end_date

    def request_with_pycurl(
            self,
            url,
    ):
        buffer = BytesIO()
        c = pycurl.Curl()

        fake_user_agent = (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36"
        )
        c.setopt(pycurl.USERAGENT, fake_user_agent)
        c.setopt(pycurl.URL, url)
        c.setopt(pycurl.WRITEDATA, buffer)
        c.setopt(pycurl.CAINFO, certifi.where())
        c.perform()
        status_code = c.getinfo(pycurl.RESPONSE_CODE)
        c.close()
        return buffer.getvalue(), status_code

    def get_post_schedule_data(self, soup):
        table = soup.find('table', summary='공모주 청약일정')
        pos_keys = list(map(lambda x: x.text.strip(), table.find_all('th')))[:-1]
        table_body = table.find('tbody')

        pos_datas: list[PosSchedule] = []
        if table_body:
            table_row = table_body.find_all('tr')
            for tr in table_row:
                table_data = tr.find_all('td')
                pos_dict = dict()
                pos_dict['id'] = self.gen_uuid()
                for i in range(len(pos_keys)):
                    table_data_text = table_data[i].text.strip()
                    if table_data_text == '-' or not table_data_text:
                        value = False
                    else:
                        value = table_data_text

                    if pos_keys[i] == '종목명':
                        pos_dict['pos_name'] = value
                    elif pos_keys[i] == '공모주일정':
                        (start_date, end_date) = self.change_date_format(value)
                        pos_dict['pos_start_date'] = start_date
                        pos_dict['pos_end_date'] = end_date
                    elif pos_keys[i] == '확정공모가':
                        pos_dict['pos_confirmed_price'] = self.reformat_price_data(value)
                    elif pos_keys[i] == '희망공모가':
                        [min, max] = value.split('~')
                        pos_dict['pos_desired_min_price'] = self.reformat_price_data(min)
                        pos_dict['pos_desired_max_price'] = self.reformat_price_data(max)
                    elif pos_keys[i] == '청약경쟁률':
                        if value:
                            decimal_val = value.split(':')
                            pos_dict['pos_competition_rate'] = Decimal(
                                self.reformat_price_data(decimal_val[0])).quantize(
                                Decimal('0.01'))
                        else:
                            pos_dict['pos_competition_rate'] = value
                    elif pos_keys[i] == '주간사':
                        pos_dict['pos_taken_company'] = value
                pos_datas.append(PosSchedule(**pos_dict))
        upsert_pos_schedule(pos_datas)

    def crawl_pos_schedule(self
                           ) -> CrawlNewPosResult:
        body, status_code = self.request_with_pycurl(get_pos_schedule_url(1))
        soup = BeautifulSoup(body, "html.parser")
        url = soup.find('a', string="[마지막]")['href']
        parsed_url = urlparse(url)
        # 쿼리 문자열을 딕셔너리로 변환
        query_params = parse_qs(parsed_url.query)
        # 'page' 파라미터의 값을 추출
        page_value = query_params.get('page', [None])[0]
        try:
            for i in range(1, int(page_value) + 1):
                body, status_code = self.request_with_pycurl(get_pos_schedule_url(i))
                soup = BeautifulSoup(body, "html.parser")
                self.get_post_schedule_data(soup)
                return CrawlNewPosResult(
                    resultCode='0',
                    resultMessage="Crawling Success"
                )
        except Exception as e:
            self.info(f"error info. cause={e}, tb={self.get_traceback(e)}")
            return CrawlNewPosResult(
                resultCode='0',
                resultMessage="Crawling Failed"
            )
