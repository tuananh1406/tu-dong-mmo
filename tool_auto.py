#!/usr/local/bin/python
# coding: utf-8
'''Tự động đăng nhập facebook
'''
import os
import logging

from datetime import datetime

from configparser import ConfigParser
from webdriver_manager.chrome import ChromeDriverManager
import sentry_sdk

import requests
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.options import Options


class CustomLogFilter(logging.Filter):
    def filter(self, record):
        if not hasattr(record, 'cookies_name'):
            record.cookies_name = EXTRA.get('cookies_name')
        return True


EXTRA = dict(cookies_name=None)
TESTING = None
# URL = 'https://gleam.io/L8Tok/lixinft-giveaway'
URL = 'https://share-w.in/hq1d4a-47546'
NAME = 'tool_auto'


def thiet_lap_logging(name):
    sentry_sdk.init(
        'https://2e084979867c4e8c83f0b3b8062afc5b@o1086935.'
        'ingest.sentry.io/6111285',
        traces_sample_rate=1.0,
    )

    log_format = ' - '.join([
        '%(asctime)s',
        '%(name)s',
        '%(levelname)s',
        # '%(cookies_name)s',
        '%(message)s',
    ])
    formatter = logging.Formatter(log_format)
    file_handles = logging.FileHandler(
        filename='%s.log' % (datetime.now().strftime("%d-%m-%Y")),
        mode='a',
        encoding='utf-8',
    )
    file_handles.setFormatter(formatter)

    syslog = logging.StreamHandler()
    syslog.setFormatter(formatter)

    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    logger.addFilter(CustomLogFilter())

    logger.addHandler(syslog)
    if not TESTING:
        logger.addHandler(file_handles)

    return logger


def tam_ngung_den_khi(driver, _xpath):
    '''Hàm tạm ngưng đến khi xuất hiện đường dẫn xpath
    '''
    _tam_ngung = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((
            By.XPATH,
            _xpath,
        )),
    )
    return _tam_ngung


def tam_ngung_va_tim(driver, _xpath):
    '''Hàm tạm ngưng đến khi xuất hiện đường dẫn xpath và chọn xpath đó
    '''
    tam_ngung_den_khi(driver, _xpath)
    return driver.find_element(by='xpath', value=_xpath)


def chay_trinh_duyet(headless=True):
    '''Mở trình duyệt và trả về driver
    '''
    options = webdriver.ChromeOptions()
    options.headless = headless
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    options.add_argument("--disable-blink-features=AutomationControlled")
    service = Service(ChromeDriverManager().install())
    LOGGER.info('Chạy trình duyệt, headless=%s', headless)
    _driver = webdriver.Chrome(
        options=options,
        service=service,
    )
    # Hàm đặt thời gian tải trang, dùng khi tải trang quá lâu
    # _driver.set_page_load_timeout(5)
    return _driver


def mo_website(_driver, url):
    '''Mở thử website
    '''

    # Mở trang
    _driver.get(url)

    return _driver


if __name__ == '__main__':
    THOI_GIAN_HIEN_TAI = datetime.now()
    LOGGER = thiet_lap_logging(NAME)
    LOGGER.info('Chạy chương trình')

    if os.path.isexists('tele.conf'):
        LOGGER.info('Load config')
        CONFIG = ConfigParser()
        CONFIG.read('tele.conf')
        BOT_TELE = CONFIG.get('config', 'BOT_TELE')
        CHAT_ID = CONFIG.get('config', 'CHAT_ID')
        LOGGER.info('Gửi thông báo qua telegram')
        tele_url = f'https://api.telegram.org/bot{BOT_TELE}/sendMessage'
        params = {
            'chat_id': CHAT_ID,
            'text': f'Chạy tool auto: {THOI_GIAN_HIEN_TAI}',
        }
        requests.post(url=tele_url, data=params)
    DRIVER = None

    try:
        LOGGER.info('*' * 50)
        LOGGER.info('Chạy thử chương trình')
        LOGGER.info('*' * 50)
        HEADLESS = False

        DRIVER = chay_trinh_duyet(headless=HEADLESS)
        DRIVER.maximize_window()
        SIZE = DRIVER.get_window_size()
        DRIVER.set_window_size(SIZE['width'] / 2, SIZE['height'])
        DRIVER.set_window_position(
            (SIZE['width'] / 2) + SIZE['width'],
            0,
            windowHandle='current',
        )
        LOGGER.info('Mở trang web')
        DRIVER = mo_website(DRIVER, URL)
        THOI_GIAN_XU_LY = datetime.now() - THOI_GIAN_HIEN_TAI
        LOGGER.info('Thời gian xử lý: %s', THOI_GIAN_XU_LY)
        input("Ấn Enter để thoát: ")
    except Exception as error:
        LOGGER.exception(error)
    finally:
        if DRIVER:
            DRIVER.quit()
