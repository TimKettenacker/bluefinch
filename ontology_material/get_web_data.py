import requests
from bs4 import BeautifulSoup
import json

# pass urls to this function to retrieve common product data dictionary
def parse_web_article_data_to_dict(url):

    page = requests.get(url)
    soup = BeautifulSoup(page.text, 'html.parser')

    article_dict = {}
    article_dict['Id'] = soup.find(class_='productID').text.strip().split("\n")
    article_dict['Artikelname'] = soup.find(class_='title').text.strip().split("\n")

    return article_dict


# pass urls to this function to retrieve product data dictionary
def parse_web_product_data_to_dict(url):

    page = requests.get(url)
    soup = BeautifulSoup(page.text, 'html.parser')

    datasheet_raw = soup.find(class_='productDetailDatasheet')

    categories = []
    specifics = []
    for category in datasheet_raw.find_all(class_='detailTitle'):
        categories.append(category.text)

    for specific in datasheet_raw.find_all(class_='article'):
        specifics.append(specific.text)

    for i, specific in enumerate(specifics):
        specifics[i] = specific.strip().split("\n")

    product_dict = {categories[i]: specifics[i] for i in range(len(categories))}

    return product_dict

# pass urls to this function to retrieve product pricing data dictionary
def parse_web_product_pricing_data_to_dict(url):

    page = requests.get(url)
    soup = BeautifulSoup(page.text, 'html.parser')

    finance_raw = soup.find(class_='additionalOptions')

    pricing_dict = {}
    pricing_dict['regulärer_Preis'] = finance_raw.find('span', 'fnzPrice').next
    pricing_dict['monatliche_Rate'] = finance_raw.find('span', id='financingrate').next
    pricing_dict['monatliche_Zinsrate'] = finance_raw.find(id='financingzinskosten').next

    return pricing_dict


urls = ["https://www.cyberport.de/apple-und-zubehoer/apple-iphone/apple/pdp/a415-1fr/apple-iphone-11-64-gb-weiss-mwlu2zd-a.html",
        "https://www.cyberport.de/apple-und-zubehoer/apple-iphone/apple-iphone-11/apple/pdp/a415-1fx/apple-iphone-11-128-gb-weiss-mwm22zd-a.html",
        "https://www.cyberport.de/apple-und-zubehoer/apple-iphone/apple-iphone-11/apple/pdp/a415-1g3/apple-iphone-11-256-gb-weiss-mwm82zd-a.html",
        "https://www.cyberport.de/apple-und-zubehoer/apple-iphone/apple-iphone-11/apple/pdp/a415-1ft/apple-iphone-11-64-gb-gelb-mwlw2zd-a.html",
        "https://www.cyberport.de/apple-und-zubehoer/apple-iphone/apple-iphone-11/apple/pdp/a415-1g5/apple-iphone-11-256-gb-gelb-mwma2zd-a.html",
        "https://www.cyberport.de/apple-und-zubehoer/apple-iphone/apple-iphone-11-pro/apple/pdp/a415-1gc/apple-iphone-11-pro-64-gb-nachtgruen-mwc62zd-a.html",
        "https://www.cyberport.de/apple-und-zubehoer/apple-iphone/apple-iphone-11-pro/apple/pdp/a415-1gg/apple-iphone-11-pro-256-gb-nachtgruen-mwcc2zd-a.html",
        "https://www.cyberport.de/apple-und-zubehoer/apple-iphone/apple-iphone-11-pro/apple/pdp/a415-1gl/apple-iphone-11-pro-512-gb-nachtgruen-mwcg2zd-a.html"]


iphones = []
# iphone 11 white and all its storage combinations
iphone11w64gb = dict()
iphone11w64gb.update(parse_web_article_data_to_dict(urls[0]))
iphone11w64gb.update(parse_web_product_data_to_dict(urls[0]))
iphone11w64gb.update(parse_web_product_pricing_data_to_dict(urls[0]))
iphones.append(iphone11w64gb)

iphone11w128gb = dict()
iphone11w128gb.update(parse_web_article_data_to_dict(urls[1]))
iphone11w128gb.update(parse_web_product_data_to_dict(urls[1]))
iphone11w128gb.update(parse_web_product_pricing_data_to_dict(urls[1]))
iphones.append(iphone11w128gb)

iphone11w256gb = dict()
iphone11w256gb.update(parse_web_article_data_to_dict(urls[2]))
iphone11w256gb.update(parse_web_product_data_to_dict(urls[2]))
iphone11w256gb.update(parse_web_product_pricing_data_to_dict(urls[2]))
iphones.append(iphone11w256gb)

# iphone 11 yellow and all its storage combinations
iphone11g64gb = dict()
iphone11g64gb.update(parse_web_article_data_to_dict(urls[3]))
iphone11g64gb.update(parse_web_product_data_to_dict(urls[3]))
iphone11g64gb.update(parse_web_product_pricing_data_to_dict(urls[3]))
iphones.append(iphone11g64gb)

iphone11g256gb = dict()
iphone11g256gb.update(parse_web_article_data_to_dict(urls[4]))
iphone11g256gb.update(parse_web_product_data_to_dict(urls[4]))
iphone11g256gb.update(parse_web_product_pricing_data_to_dict(urls[4]))
iphones.append(iphone11g256gb)

# iphone 11 pro nightgreen and all its storage combinations
iphone11pro64gb = dict()
iphone11pro64gb.update(parse_web_article_data_to_dict(urls[5]))
iphone11pro64gb.update(parse_web_product_data_to_dict(urls[5]))
iphone11pro64gb.update(parse_web_product_pricing_data_to_dict(urls[5]))
iphones.append(iphone11pro64gb)

iphone11pro256gb = dict()
iphone11pro256gb.update(parse_web_article_data_to_dict(urls[6]))
iphone11pro256gb.update(parse_web_product_data_to_dict(urls[6]))
iphone11pro256gb.update(parse_web_product_pricing_data_to_dict(urls[6]))
iphones.append(iphone11pro256gb)

iphone11pro512gb = dict()
iphone11pro512gb.update(parse_web_article_data_to_dict(urls[7]))
iphone11pro512gb.update(parse_web_product_data_to_dict(urls[7]))
iphone11pro512gb.update(parse_web_product_pricing_data_to_dict(urls[7]))
iphones.append(iphone11pro512gb)

with open('ontology_material/instance_data.json', 'w') as outfile:
    json.dump(iphones, outfile, ensure_ascii=False)
    outfile.close()