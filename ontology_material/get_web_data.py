import requests
from bs4 import BeautifulSoup


# pass urls to this function to retrieve common product data dictionary
def parse_web_article_data_to_dict(url):

    page = requests.get(url)
    soup = BeautifulSoup(page.text, 'html.parser')

    article_dict = {}
    article_dict['id'] = soup.find(class_='productID').text.strip().split("\n")
    article_dict['name'] = soup.find(class_='title').text.strip().split("\n")

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
    pricing_dict['regular_price'] = finance_raw.find('span', 'fnzPrice').next
    pricing_dict['monthly_rate'] = finance_raw.find('span', id='financingrate').next
    pricing_dict['monthly_interest_rate'] = finance_raw.find(id='financingzinskosten').next

    return pricing_dict


article_dict = parse_web_article_data_to_dict("https://www.cyberport.de/apple-und-zubehoer/apple-iphone/"
                       "apple/pdp/a415-1fr/apple-iphone-11-64-gb-weiss-mwlu2zd-a.html")
product_dict = parse_web_product_data_to_dict("https://www.cyberport.de/apple-und-zubehoer/apple-iphone/"
                       "apple/pdp/a415-1fr/apple-iphone-11-64-gb-weiss-mwlu2zd-a.html")
pricing_dict = parse_web_product_pricing_data_to_dict("https://www.cyberport.de/apple-und-zubehoer/apple-iphone/"
                       "apple/pdp/a415-1fr/apple-iphone-11-64-gb-weiss-mwlu2zd-a.html")







