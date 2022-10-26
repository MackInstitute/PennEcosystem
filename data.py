import urllib
import os
import time
import pandas as pd

df = pd.read_csv('total_links.csv', index_col=0)
links = df.Url
destination_dir = 'home/mgmt/wanxing/html/'
# print(link)
for link in links:
    domain_name=[]
    link_element = link.split('/')
    link_element[2] = link_element[2].replace("www.","")
    reversed_element = ['.'.join(reversed_element[:i][::-1]) for i in range(1,len(reversed_element)+1)]
    link_element[2] = '/'.join(reversed_element)
    for i in range(2, len(link_element)-2):
        if len(link_element[i]) != 0:
            domain_name.append(link_element[i])
    name = link_element[-2]
    # print(link_element)
    domain_name = '/'.join(domain_name)
    # print(domain)
    # print(link)
    # filepath = '/Users/wanxing/PycharmProjects/PennEcosystem/html_data/c3i'
    filepath = os.path.join(destination_dir, domain_name)
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
    print("Downloading "+name)
    time.sleep(5)