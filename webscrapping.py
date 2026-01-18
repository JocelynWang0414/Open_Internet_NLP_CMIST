import requests
from bs4 import BeautifulSoup
import time
import re
import os
import json
import csv
from deep_translator import GoogleTranslator

def deep_translate_to_english(ukrainian_text):
    output = ''
    if len(ukrainian_text) < 500:
      return GoogleTranslator(source='uk', target='en').translate(ukrainian_text)
    else:
      i = 0
      while i < len(ukrainian_text):
        if i <= len(ukrainian_text) - 500:
          output += GoogleTranslator(source='uk', target='en').translate(ukrainian_text[i:i+500])
        else:
          output += GoogleTranslator(source='uk', target='en').translate(ukrainian_text[i:])
        i += 500
    return output

def get_vechirka_links(base_url):
    """
    Scrape all relevant links from the archived vechirka.pl.ua website.
    Returns a list of dictionaries with link text and URL.
    """
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"}

    try:
        time.sleep(1)  # Be polite to the server
        response = requests.get(base_url, headers=headers)
        response.raise_for_status()

        print('Check base url: ', base_url)
        soup = BeautifulSoup(response.text, 'html.parser')
        existing_href = set()
        bookmark_links = []
        for link in soup.find_all('a'):
            href = link.get('href', '')
            link_text = link.text.strip()
            
            if 'page' in href:
               continue
            if not "ukrayina" in href:
               continue
            if len(link_text) <= 0: 
               continue
            if not href[-1] in "0123456789": 
               continue
            if href in existing_href:
               continue
            existing_href.add(href)
            
            print('Storing href: ', href)
            bookmark_links.append({
                "Beginning_Texts": deep_translate_to_english(link_text),
                "Basic_URL": href[href.find("http"):],
                "Relative_URL": href})
        return bookmark_links

    except Exception as e:
        print(f"Error getting vechirka links: {str(e)}")
        return []

def extract_article_content_pipepline(article_url):
    """
    Visit an article page and extract the content.
    For vechirka.pl.ua, we'll look for the main article content.
    """
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"}

    try:
        time.sleep(2)  # Longer delay for article pages to be extra polite
        response = requests.get(article_url, headers=headers)
        response.raise_for_status()
        if response.status_code != 200: print('Webscrapping response OK.')
        soup = BeautifulSoup(response.text, 'html.parser')

        # Extract the publication date and time from the dateCreatAdv div
        date_div = soup.find('div', class_='dateCreatAdv')
        publication_datetime = date_div.get_text().strip().split("Опубліковано:")[1].strip()
        day = publication_datetime[:2]
        month = publication_datetime[3:5]
        year = publication_datetime[6:10]
        time_of_day = publication_datetime[11:]
        publication_datetime = "/".join(list((year, month, day, time_of_day)))

        # First try to find content in a div with class field-item even (like in Chayka)
        article_div = soup.find_all('div', class_='field-item even')

        paragraphs = []
        for p in article_div:
            paragraphs.append(p.get_text(strip=False))

        # Join paragraphs with double newlines to preserve structure
        uk_content = "\n".join(paragraphs)
        eng_content = deep_translate_to_english(uk_content)
        return publication_datetime, uk_content, eng_content

    except Exception as e:
        print(f"Error extracting article: {str(e)}")
        return 'Error', 'Error'

def scrape_vechirka_articles(base_url, max_articles=5):
    """
    Main function to scrape vechirka.pl.ua articles.
    Limits the number of articles to scrape to avoid overloading the server.
    """

    print("Finding relevant links on the main page...")
    vechirka_links = get_vechirka_links(base_url)

    if not vechirka_links:
        return {"error": "No relevant links found"}

    # Limit the number of articles to scrape (disabled)
    articles_to_scrape = vechirka_links

    urls = []
    for a in articles_to_scrape:
      url = '/'.join(a['Basic_URL'].split('/')[-5:])
      urls.append(url)

    print(f"Found {len(vechirka_links)} links. Will scrape {len(urls)} articles...")

    for i in range(len(urls)):
      print(f"   Scraping article {i+1}/{len(urls)}: {urls[i][:40]}...")
      print('Extracting...')
      if extract_article_content_pipepline(urls[i]) == ('Error', 'Error'): continue
      published_date_time, uk_content, eng_content = extract_article_content_pipepline(urls[i])
      articles_to_scrape[i]['Published_Date_Time'] = published_date_time
      articles_to_scrape[i]['article_content_english'] = eng_content
      articles_to_scrape[i]['article_content_ukrainian'] = uk_content

    return {
        "Number of links found": len(vechirka_links),
        "Number of articles scraped": len(urls),
        "Articles": articles_to_scrape
    }

def save_to_file(data, timestamp, filename=None):
    filename = f"vechirka.pl.ua_{timestamp}_uk_eng.csv"
    desktop_path = '/Users/wangcancan/Desktop'
    csv_filename = os.path.join(desktop_path, filename)

    # Write the article data to the CSV file
    with open(csv_filename, mode='w', encoding='utf-8', newline='') as file:
      writer = csv.DictWriter(file, fieldnames=data[0].keys())
      writer.writeheader()
      for article in data:
          writer.writerow(article)

    print(f"Data successfully written to {csv_filename}")

def main():
    print("Starting vechirka.pl.ua article scraper...")

    # timestamps = ['20250301192102', '20250302192356', '20250303190339', '20250304193333', '20250305190239', '20250306190643',
    #                  '20250307193835', '20250308191039', '20250310191416', '20250311193550', '20250312190307', '20250313190028',
    #                  '20250314195225', '20250315191939', '20250316191619', '20250317190116', '20250318191156', '20250319191941',
    #                  '20250320191223', '20250321193231', '20250322192445', '20250323191243', '20250324191713', '20250325190336',
    #                  '20250326191356', '20250327191824', '20250328190423', '20250329191300', '20250330191251', '20250331193511']

    timestamps = ['20250302192356']

    max_articles = None # Disabled
    for timestamp in timestamps:
      
      base_url = 'https://web.archive.org/web/' + timestamp + '/http://vechirka.pl.ua/ukrayina/na-liniyi-frontu'
    
      base_url = 'https://web.archive.org/web/' + timestamp + '/http://vechirka.pl.ua/ukrayina/na-liniyi-frontu?page=1' # 20220601021453

      #base_url = 'https://web.archive.org/web/' + timestamp + '/http://vechirka.pl.ua/ukrayina/na-liniyi-frontu?page=2' 

      result = scrape_vechirka_articles(base_url, max_articles)

      if "error" in result: print(f"Error: {result['error']}")
      else: print(f"\nSuccessfully scraped {result['Number of articles scraped']} articles out of {result['Number of links found']} links found.")

      # Only store the articles
      result = result['Articles']
      print(f"Finishing timestamp {timestamp}!")
      # Save all data to a file
      save_to_file(result, timestamp)

if __name__ == "__main__":
    main()