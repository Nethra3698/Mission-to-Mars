# Import Splinter and BeautifulSoup
from splinter import Browser
from bs4 import BeautifulSoup as soup
import pandas as pd
import datetime as dt

def scrape_all():
    # Initiate headless driver for deployment
    browser = Browser("chrome", executable_path="chromedriver", headless=True)
    news_title, news_paragraph = mars_news(browser)
    mars_images,hemi_title = mars_hemisphere(browser)
    # Run all scraping functions and store results in dictionary
    data = {
        "news_title": news_title,
        "news_paragraph": news_paragraph,
        "featured_image": featured_image(browser),
        "facts": mars_facts(),
        "last_modified": dt.datetime.now(),
        "mars_hemisphere_images": mars_images,
        "mars_hemisphere_titles": hemi_title
    }
    # Stop webdriver and return data
    browser.quit()
    return data
   

# Set the executable path and initialize the chrome browser in splinter
executable_path = {'executable_path': 'chromedriver'}
browser = Browser('chrome', **executable_path)

def mars_news(browser):

    # Visit the mars nasa news site
    url = 'https://mars.nasa.gov/news/'
    browser.visit(url)
    # Optional delay for loading the page
    browser.is_element_present_by_css("ul.item_list li.slide", wait_time=2)

    html = browser.html
    news_soup = soup(html, 'html.parser')

    # Add try/except for error handling
    try:

        slide_elem = news_soup.select_one('ul.item_list li.slide')
        
        # Use the parent element to find the first `a` tag and save it as `news_title`
        news_title = slide_elem.find("div", class_='content_title').get_text()

        # Use the parent element to find the paragraph text
        news_p = slide_elem.find('div', class_="article_teaser_body").get_text()
    
    except AttributeError:
        return None, None
    
    return news_title, news_p

def featured_image(browser):

    # Visit URL
    url = 'https://www.jpl.nasa.gov/spaceimages/?search=&category=Mars'
    browser.visit(url)

    # Find and click the full image button
    full_image_elem = browser.find_by_id('full_image')
    full_image_elem.click()

    # Find the more info button and click that
    browser.is_element_present_by_text('more info', wait_time=1)
    more_info_elem = browser.links.find_by_partial_text('more info')
    more_info_elem.click()

    # Parse the resulting html with soup
    html = browser.html
    img_soup = soup(html, 'html.parser')

    try:
        # Find the relative image url
        img_url_rel = img_soup.select('figure.lede a img').get("src")

    except AttributeError:
        return None

    # Use the base URL to create an absolute URL
    img_url = f'https://www.jpl.nasa.gov{img_url_rel}'

    return img_url

def mars_facts():
    try:
        # Use 'read_html' to scrape the facts table into a dataframe
        df = pd.read_html('http://space-facts.com/mars/')[0]
    except BaseException:
        return None
    df.columns=['description', 'value']
    df.set_index('description', inplace=True)

    return df.to_html(classes="table table-striped") 

# Challenge 
# Scraping mars hemisphere images

def mars_hemisphere(browser):

    img_url=[]
    hemi_title=[]

    for x in range(0,4):

        # Visit URL
        url = 'https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars'
        browser.visit(url)

        # Find and click the full image button
        thumbnail_elem = browser.find_by_tag('h3')[x]
        thumbnail_elem.click()

        # Find the more info button and click that
                
        hemi_elem = browser.find_by_id('wide-image-toggle')
        hemi_elem.click()
        
        html = browser.html
        img_soup = soup(html, 'html.parser')
        title_name = img_soup.find('h2', {'class':'title'}).text

        img_url_r = img_soup.find('img', {'class':'wide-image'}).get("src")

        # Use the base URL to create an absolute URL
        img_url.append(f'https://astrogeology.usgs.gov/{img_url_r}')
        hemi_title.append(title_name)

    return img_url, hemi_title

if __name__ == "__main__":
    # If running as script, print scraped data
    print(scrape_all())


