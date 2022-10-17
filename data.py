# %%
# pip install bs4
# pip install selenium
# pip install requests
# pip install webdriver-manager

# %% [markdown]
# https://medium.com/analytics-vidhya/web-scraping-google-search-results-with-selenium-and-beautifulsoup-4c534817ad88

# %%
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
# Import the beautifulsoup and request libraries of python.
import requests
import bs4

# %%
chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument("--headless")
driver = webdriver.Chrome(ChromeDriverManager().install(), chrome_options=chrome_options)
import ssl
ssl._create_default_https_context = ssl._create_unverified_context

# %%

# text= "innovation"
# domain = "q=site%3Aupenn.edu+"
# page = 3
# url = "https://www.google.com/search?" + domain + text + "&start=" + str((page - 1) * 10)
# driver.get(url)
# print(url)
# soup = bs4.BeautifulSoup(driver.page_source, 'html.parser')
# print(soup)

# %%
## Google search
import time
import urllib.request
import os

text= "innovation"
domain = "q=site%3Aupenn.edu+"
links = [] # Initiate empty list to capture final results
destination_dir = '/home/mgmt/wanxing/html_data/'
# Specify number of pages on google search, each page contains 10 #links

n_pages = 50
for page in range(1, n_pages):
    # print(page)
    url = "https://www.google.com/search?" + domain + text + "&start=" + str((page - 1) * 10)
    print(url)
    driver.get(url)
    soup = bs4.BeautifulSoup(driver.page_source, 'html.parser')
    print(soup)
    search = soup.find_all('div', class_="yuRUbf")
    # print(search)
    for h in search:
        links.append(h.a.get('href'))
    for h in search:
        domain=[]
        link = h.a.get('href')
        # print(link)
        if link is not None:
            link_element = link.split('/')
            link_element[2] = link_element[2].replace("www.","").replace(".upenn.edu","")
            for i in range(2, len(link_element)-2):
                if len(link_element[i]) != 0:
                    domain.append(link_element[i])
            name = link_element[-2]
            # print(link_element)
            domain = '/'.join(domain)
            title = h.a.text
            links.append(link)
            # print(domain)
            # print(link)
            # filepath = '/Users/wanxing/PycharmProjects/PennEcosystem/html_data/c3i'
            filepath = os.path.join(destination_dir, domain)
            # print(filepath)
            if not os.path.exists(filepath):
                if not os.path.exists(destination_dir):
                    os.makedirs(destination_dir)
                os.makedirs(filepath)
            filename = os.path.join(filepath, name+".html")
            try:
                urllib.request.urlretrieve(link, filename)
            except:
                continue
            # print(filename)
            print("Downloading "+title)
            time.sleep(3)

# %%
links

# %%
import pandas as pd
links = pd.DataFrame(links, columns=['link'])
links.to_csv('links.csv')

# %%
# import urllib.request
# import os
# # Penn Website search https://www.upenn.edu/search
# text= "innovation"
# links = [] # Initiate empty list to capture final results
# destination_dir = '/Users/wanxing/PycharmProjects/PennEcosystem/html_data/'
# # Specify number of pages on google search, each page contains 10 #links

# n_pages = 20
# for page in range(1, n_pages):
#    #https://www.upenn.edu/search?as_q=innovation#gsc.tab=0&gsc.q=innovation&gsc.page=1 
#     url = "https://www.upenn.edu/search?as_q=" + text + "#gsc.tab=0&gsc.q=innovation&gsc.page=" + str((page))
#     driver.get(url)
#     soup = bs4.BeautifulSoup(driver.page_source, 'html.parser')
#     search = soup.find_all('div', class_="gsc-thumbnail-inside")
#     for h in search:
#         domain=[]
#         link = h.a.get('href')
#         # print(link)
#         if link is not None:
#             link_element = link.split('/')
#             for i in range(2, len(link_element)):
#                 if len(link_element[i]) != 0:
#                     domain.append(link_element[i])
#             domain = '/'.join(domain)
#             title = h.a.text
#             links.append(link)
#             print(page)
#             print(domain)
#             print(link)

#             filepath = os.path.join(destination_dir, domain)
#             print(filepath)
#             if not os.path.exists(filepath):
#                 if not os.path.exists(destination_dir):
#                     os.makedirs(destination_dir)
#                 os.makedirs(filepath)
#             try:
#                 urllib.request.urlretrieve(link, filepath+'.html')
#             except:
#                 continue
#             print("Downloading "+title)

# %%
#   # Make two strings with default google search URL
# # 'https://google.com/search?q=' and
# # our customized search keyword.
# # Concatenate them
# text= "innovation"
# domain = "site%3Aupenn.edu+"
# url = 'https://google.com/search?q=' + domain + text
  
# # Fetch the URL data using requests.get(url),
# # store it in a variable, request_result.
# request_result=requests.get( url )
  
# # Creating soup from the fetched request
# soup = bs4.BeautifulSoup(request_result.text,
#                          "html.parser")
# print(soup)

# %%
# # soup.find.all( h3 ) to grab 
# # all major headings of our search result,
# heading_object=soup.find_all( 'h3' )
  
# # Iterate through the object 
# # and print it as a string.
# for info in heading_object:
#     print(info.getText())
#     print("------")


