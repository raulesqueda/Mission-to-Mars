# Import Splinter, BeautifulSoup, and Pandas
from splinter import Browser
from bs4 import BeautifulSoup as soup
import pandas as pd
import datetime as dt
from webdriver_manager.chrome import ChromeDriverManager


def scrape_all():
    # Initiate headless driver for deployment
    executable_path = {'executable_path': ChromeDriverManager().install()}
    browser = Browser('chrome', **executable_path, headless=True)

    news_title, news_paragraph = mars_news(browser)

    # Run all scraping functions and store results in a dictionary
    data = {
        "news_title": news_title,
        "news_paragraph": news_paragraph,
        "featured_image": featured_image(browser),
        "facts": mars_facts(),
        "last_modified": dt.datetime.now(),
        "hemisphere_image": hemisphere(browser)
    }

    # Stop webdriver and return data
    browser.quit()
    return data


def mars_news(browser):

   # Visit the mars nasa news site
    url = 'https://redplanetscience.com/'
    browser.visit(url)

   # Optional delay for loading the page
    browser.is_element_present_by_css('div.list_text', wait_time=1)

   # Convert the browser html to a soup object and then quit the browser
    html = browser.html
    news_soup = soup(html, 'html.parser')

    # Add try/except for error handling
    try:
        slide_elem = news_soup.select_one('div.list_text')
        # Use the parent element to find the first 'a' tag and save it as 'news_title'
        news_title = slide_elem.find('div', class_='content_title').get_text()
        # Use the parent element to find the paragraph text
        news_p = slide_elem.find('div', class_='article_teaser_body').get_text()

    except AttributeError:
        return None, None

    return news_title, news_p

# Getting images

def featured_image(browser):
    # Visit URL
    url = 'https://spaceimages-mars.com'
    browser.visit(url)

    # Find and click the full image button
    full_image_elem = browser.find_by_tag('button')[1]
    full_image_elem.click()

    # Parse the resulting html with soup
    html = browser.html
    img_soup = soup(html, 'html.parser')

    # Add try/except for error handling
    try:
   # find the relative image url
        img_url_rel = img_soup.find('img', class_='fancybox-image').get('src')

    except AttributeError:
        return None

    # Use the base url to create an absolute url
    img_url = f'https://spaceimages-mars.com/{img_url_rel}'
    return img_url

## Mars facts 
def mars_facts():
    # Add try/except for error handling
    try:
      # use 'read_html" to scrape the facts table into a dataframe
        df = pd.read_html('https://galaxyfacts-mars.com')[0]
    except BaseException:
        return None

    # Assign columns and set index of dataframe
    df.columns=['Description', 'Mars', 'Earth']
    df.set_index('Description', inplace=True)

    # Convert dataframe into HTML format, add bootstrap
    return df.to_html(classes="mystyle")

## Hemisphere images
def hemisphere(browser):

    # Use browser to visit the URL 
    url = 'https://marshemispheres.com/'
    browser.visit(url)

    # Create a list to hold the images and titles.
    hemisphere_image_urls = []

    # Write code to retrieve the image urls and titles for each hemisphere.
    html = browser.html
    images_soup = soup(html, 'html.parser')

    # Add try/except for error handling
    try:
        # Find a div to get the links to the full-resolution images
        hemi = images_soup.find_all('div', class_='item')

        for img in hemi:
            # get the url for every link
            url = img.find("a", {"class": "itemLink product-item"}).attrs['href']
            # visit every hemisphere link
            browser.visit(f'https://marshemispheres.com/{url}')
            #Second code to retrieve the image urls and titles for each hemisphere.
            html2 = browser.html
            wideimg_soup = soup(html2, 'html.parser')
            # retrieve the title for the hemisphere image
            title = wideimg_soup.find('h2', class_='title').text
            # retrieve the full-resolution image URL string
            div_wideimg_soup = wideimg_soup.find('div', class_='downloads')
            imagen = div_wideimg_soup.li.a.get('href')
            # Append data in the dictionary 
            hemisphere_image_urls.append({"img_url" : f'https://marshemispheres.com/{imagen}',
                                        "title" : title})
            # navigate back to the beginning to get the next hemisphere image.
            browser.back()

    except AttributeError:
        return None

    return hemisphere_image_urls

if __name__ == "__main__":

    # If running as script, print scraped data
    print(scrape_all())