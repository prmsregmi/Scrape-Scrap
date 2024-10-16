'''
This script scrapes medicine data from the website "http://medguideindia.info/" and saves it to a CSV file.
Modules:
    - urllib.request: For making HTTP requests.
    - bs4 (BeautifulSoup): For parsing HTML content.
    - pandas: For handling data in DataFrame format.
    - csv: For writing data to CSV files.
    - tqdm: For displaying progress bars.
Functions:
    - get_links(num_pages: int, save: bool = False, base_url: str = "http://www.medguideindia.info/") -> list:
    - save_medicine_data(num_pages: int) -> None:
Usage:
    Call the `save_medicine_data` function with the desired number of pages to scrape.
'''

import csv
from urllib.request import urlopen, Request
from bs4 import BeautifulSoup
import pandas as pd
from tqdm import tqdm

headers = {
    'User-Agent': (
        'Mozilla/5.0 (X11; Linux x86_64) '
        'AppleWebKit/537.11 (KHTML, like Gecko) '
        'Chrome/23.0.1271.64 Safari/537.11'
    ),
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
    'Accept-Encoding': 'none',
    'Accept-Language': 'en-US,en;q=0.8',
    'Connection': 'keep-alive'
}

def get_links(num_pages: int, save: bool = False, base_url: str = "http://www.medguideindia.info/") -> list:
    """
    Fetches links from the specified number of pages and optionally saves them to a CSV file.

    Args:
        num_pages (int): The number of pages to scrape.
        save (bool): Whether to save the links to a CSV file. Default is False.
        base_url (str): The base URL to use for scraping. Default is "http://www.medguideindia.info/".

    Returns:
        list: A list of scraped links.
    """
    links_list = []
    for page_num in range(num_pages):
        try:
            url = f"{base_url}show_generics.php?nav_link=&pageNum_rr={page_num}&nav_link=&selectme={page_num}"
            req = Request(url=url, headers=headers)
            page_html = urlopen(req).read()
            soup = BeautifulSoup(page_html, 'html.parser')
        except Exception as e:
            print(f"Error in getting response from the url {url}.\n {e}.")
            continue

        for table in soup.find_all("table", {"class": "tabsborder2"}):
            row_count = 0
            for row in table.find_all('tr'):
                row_count += 1
                if row_count == 52:
                    break

                cells = row.find_all('td')
                link = cells[3].find('a')
                if link is not None:
                    links_list.append(base_url + link.get("href"))
            print(f"{page_num + 1} of {num_pages} pages extracted")

    if save:
        df = pd.DataFrame(links_list)
        df.to_csv('links.csv', index=False)
    return links_list

def save_medicine_data(num_pages: int) -> None:
    """
    Scrapes medicine data from the given number of pages and saves it to a CSV file.

    Args:
        num_pages (int): The number of pages to scrape.
    """
    links = get_links(num_pages)
    total_links = len(links)
    for url in tqdm(links, desc="Scraping pages", unit="page", total=total_links):
        try:
            req = Request(url=url, headers=headers)
            page_html = urlopen(req).read()
            soup = BeautifulSoup(page_html, 'html.parser')
        except Exception as e:
            tqdm.write(f"Error in getting response from the url {url}.\n {e}.")
            continue

        header_text = soup.find("td", {"class": "rd-txt"}).text.strip().replace("Matched Brand/Brands of , ", "")
        cleaned_header = header_text.replace("Matched Brand/Brands of", "")

        for table in soup.find_all("table", {"class": "tabsborder2"}):
            for row in table.find_all('tr'):
                cells = row.find_all('td', {"class": ["red-txt", "mosttext"]})
                if cells:
                    row_data = [cell.text.strip() for cell in cells]
                    if len(row_data) == 1:
                        temp_data = row_data
                    else:
                        with open('pharma_drugs.csv', 'a', encoding='utf-8') as file:
                            writer = csv.writer(file)
                            writer.writerow([cleaned_header] + temp_data + row_data)


if __name__ == "__main__":
    # Call the function with the desired number of pages
    save_medicine_data(2)
