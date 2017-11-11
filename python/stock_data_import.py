from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import requests

import pandas as pd
import numpy as np

from datetime import datetime

# get today's date, used in CSV file path
now = datetime.now()
stocks_data_fname_cur = '../assets/stocks_raw_data_{}_{}_{}.csv'.format(now.day, now.month, now.year)
stocks_data_fname_lastest = '../assets/stocks_raw_data_latest.csv'

url = 'http://www.calcalist.co.il/stocks/home/0,7340,L-4021,00.html'

driver = webdriver.Firefox()
driver.delete_all_cookies()
driver.get(url)
# driver.implicitly_wait(5)  # seconds

max_wait_time = 10

# remove all filters params except market cap
WebDriverWait(driver, max_wait_time).until(
    EC.presence_of_element_located(
        (By.XPATH, '//*[@id="stock_filter_2"]/div/a'))).click()
WebDriverWait(driver, max_wait_time).until(
    EC.presence_of_element_located(
        (By.XPATH, '//*[@id="stock_filter_9"]/div/a'))).click()
WebDriverWait(driver, max_wait_time).until(
    EC.presence_of_element_located(
        (By.XPATH, '//*[@id="stock_filter_29"]/div/a'))).click()

# click on "show results"
results_button = WebDriverWait(driver, max_wait_time).until(
    EC.presence_of_element_located((By.XPATH, '//*[@id="AmountSection"]/div/div/div/a')))
results_button.click()

# get session token
sess_token = WebDriverWait(driver, max_wait_time).until(
    EC.presence_of_element_located((By.XPATH, '//*[@id="StockResultsArea"]/div[4]/a[2]')))
sess_token = sess_token.get_attribute(name='href')

# prase token string (remove and replace)
sess_token = sess_token.split("javascript:SendPrintAndExel('/")[1]
sess_token = sess_token.split("',%20'excel',%200,%20'SelectTitle')")[0]
sess_token = sess_token.replace("1*MARKET_VALUE",
                                "1-2-5-6-7-8-9-12-14-17-18-19-20-21-22-23-24-25-26-27-30-28-31-34-35-29*MARKET_VALUE")
sess_token = sess_token.split('?minmax=replaceminmax&anaf=repanaf&hideParams=REPLACEHIDEPARAMS')[0]

data_download_url = "http://www.calcalist.co.il/" + sess_token

# get data as table
data_file = requests.get(data_download_url)
data_file.encoding = 'UTF-8'

# close webdriver
driver.close()

# read table as pd df
stocks_data = pd.read_html(data_file.text)[-1]
stocks_data.columns = stocks_data.iloc[0]  # make col names
stocks_data = stocks_data.reindex(stocks_data.index.drop(0))  # drop name row and reindex

stocks_data.replace('N/A', np.NaN)
stocks_data.replace('N/A%', np.NaN)
stocks_data.replace('N/A%', np.NaN)


def format_percent_and_float(x):
    try:
        x = x.replace(',', '.')
        if '%' in x:
            x = float(x.strip('%')) / 100
        else:
            x = float(x)
        return x
    except:
        return np.NaN


for col in stocks_data.columns:
    if col in ['שם מניה', 'שווי שוק']:
        pass
    else:
        # transform the columns and replace
        stocks_data[col] = stocks_data[col].apply(format_percent_and_float)
    if col in ['תשואות דיבידנט', 'תשואה על ההון העצמי']:
        stocks_data[col] = stocks_data[col].apply(lambda x: float(x / 100))

# save to file
stocks_data.to_csv(stocks_data_fname_cur,
                   sep=';', na_rep='NaN', index=False, encoding='UTF-8')
stocks_data.to_csv(stocks_data_fname_lastest,
                   sep=';', na_rep='NaN', index=False, encoding='UTF-8')
