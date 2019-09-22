from bs4 import BeautifulSoup
import re
import codecs
import numpy as np
import pandas as pd
import webbrowser
import urllib.request
import urllib
import tqdm
import multiprocessing
import argparse

# parse input data
parser = argparse.ArgumentParser()
parser.add_argument('--category_url', default=None, help="Copy and paste url for required category")
parser.add_argument('--category', default='serial_killers', help="Name of parsing wiki-category")
parser.add_argument('--threads', default=10, help="Number of processing involved for parsing.")


class WikiParser():
    """Data parser from wikipedia.org. Works with russian and english languages. 
    Parse all profiles from `Category X` wikipedia.org page. This class is for 
    terminal usage.
    Class gives you option for parsing any information you want. So you need to
    define you custom `parse_func` method to describe what you want to parse.
    
    Important: For now parser doesn't work when page contain very few profiles.
    
    Args:
        category_url (str): url to wikipedia category page. This page should
            contain links to each separete profile sample in this category. Example
            of page - https://en.wikipedia.org/wiki/Category:German_serial_killers.
        category (str): name of category.
    """
    
    # func for deriving language from URL   
    lang = staticmethod(lambda x: x.split('.')[0].split('//')[-1])
    
    def __init__(self, category_url, category, threads=10):
        self.category = category
        self.threads = threads
        self.category_url = category_url
        self.lang = WikiParser.lang(self.category_url)   # derive language from input URL
        self.PREFIX = 'https://ru.wikipedia.org/' if self.lang=='ru' else 'https://en.wikipedia.org/'
        
    def __call__(self):
        # get profiles from all pages of category
        self.profiles_from_cat = self.parse_profiles_in_cat()
        assert len(self.profiles_from_cat) > 0, "Nothing to parse! Give me really big data!"
        
        # run data parsing process from each profile in category with multiprocessing
        with multiprocessing.Pool(processes=self.threads) as p:
            parsed_data = p.map(func=self.parse_func, iterable=tqdm.tqdm(self.profiles_from_cat))
        
        # convert to csv
        df = pd.DataFrame(data=parsed_data)
        df['category'] = self.category
        df.to_csv(f'{self.category}.csv')
        print(f' `{self.category}.csv` dataframe saved to the current folder.')
            
    def parse_profiles_in_cat(self):
        """Method parses urls of all pages in category. Than parses all profiles from all
        pages and concat them to one list. So method returns all profiles in categry (i.e.
        from all pages).
        
        Returns:
            profiles_from_category (list of tuples): where each tuple is two strings: 
                profile's name and profile's url. This list contains profiles from all
                pages of category. Now it is ready to parse required data from each 
                profile.
        """
    
        # parse all pages (NOT profiles) in category, returns list of strings
        pages_urls = self.parse_urls_of_all_pages()  
        print("Parsed pages: ", len(pages_urls))
                    
        # Get a list of lists (HTML format) with all profiles in category (each page is a separate list)
        # each value in a list is a HTML format's page in category, but we don't have HTMP type so this
        # HTML is cover by list, so we have list of list. Semanticly each value in list is HTML page.
        htmls = [self.parse_urls_of_all_profiles_on_page(page) for page in pages_urls]
            
        # loop over each page (HTML format), returns list of list where each value is name and url
        profiles_from_category = [self.gener_list_of_names_and_urls(html) for html in htmls]
        
        # concat to one list all lists (pages)
        if len(profiles_from_category) > 1: 
            profiles_from_category = np.sum(profiles_from_category)  
        else:
            profiles_from_category = profiles_from_category[0]
        print("Number of profiles from all pages: ", len(profiles_from_category))
        return profiles_from_category      
    
    
    def parse_func(self):
        """Defined by user specific information parsing method. Could be customized for each 
        user dependent from required information. 
        
        NOTE: Each custom func should takes url to persons profile of wiki as input and returns 
        required data. Func should contains asserts for situtaions where profile doesn't contain 
        required info.
        
        Returns arbitrary number of variables. But very important that variables should have 
        directly defined type, e.g. `return str(name), int(date)  
        """
        raise NotImplementedError        
                 
    def parse_urls_of_all_pages(self):   
        """Sometimes category page doesn't fit all profiles in one page, so they are several.
        This method returns urls to all pages on the category page. Each page contains profiles.
        """
        result = []; 
        url = self.category_url
        
        result.append(url)    # add first page by default
        for i in range(500):  # 500 is arbitrary big number
            html = BeautifulSoup(urllib.request.urlopen(url), 'lxml')
            container = html.find_all('div', {'id' : 'mw-pages'})
            container = BeautifulSoup(str(container), 'lxml')
            next_page_text = 'next page' if self.lang=='en' else 'Следующая страница'
            if bool(container.find('a', text=next_page_text)):  # for Eng should be updated
                link_to_next_page = container.find('a', text=next_page_text)['href']
                link_to_next_page = self.PREFIX + link_to_next_page
                result.append(link_to_next_page)
                url = link_to_next_page
            else:
                break
        return result

    def parse_urls_of_all_profiles_on_page(self, category_page):
        """Returns parsed urls for all profiles on a single page in HTML format."""
        return BeautifulSoup(
            urllib.request.urlopen(category_page), 'lxml').find_all('div', {'class': 'mw-category'})
    
    def gener_list_of_names_and_urls(self, html):
        """Generate a list in which each value is a tuple with profile name and url. Applied 
        to each page in the category.
        
        Args:
            html (HTML): page with parsed profiles on a category page.
            
        Returns:
            names_and_urls (list of tuples): each value in list are tuple with profile names 
                and urls.
        """
        names_and_urls = []
        html = BeautifulSoup(str(html), 'lxml')  # read html
        urls = html.find_all('li')               # find all link in the html
        for url in urls:                         # loop over all links to parse names and urls
            url = BeautifulSoup(str(url), 'lxml')
            name = url.string
            url_for_name = self.PREFIX + str(url.find('a').attrs['href'])
            names_and_urls.append((name, url_for_name))
        return names_and_urls
    
    
def parse_image(x: tuple):
    """Parse image from person's url.
    
    Args:
        x (tuple): tuple of strings with following structure ('person name', 'url to wiki page')

    Returns:
        name (str): the same as output, i.e. just copy. Important should be directly defined as str()
        image (str): string with url to image of a person from wikipedia 
    """
    
    name, url = x  # unpack tuple
    html = BeautifulSoup(urllib.request.urlopen(url), 'lxml')
    
    # check it contains photo
    images = html.find_all('img')
    img_exist = images[0]['alt'] == 'Фотография' or images[0]['src'].endswith('.jpg')
    
    if img_exist:
        return str(name), str(images[0].attrs['src'][2:])
    else:
        return str(name), str('None')  
    
    
def parse_bday(x: tuple):
    """Returns name and birth day of a person derived from wiki's preson profile page.
    
    Args:
        x (str): url to personal profile of a person on wikipedia
    Returns:
        name (str): the same as output, i.e. just copy. Important should be directly defined as str()
        image (str): string with date of birthday
    """
    name, url = x  # unpack tuple
    html = BeautifulSoup(urllib.request.urlopen(url), 'lxml')
    try:
        bday = html.find_all('span', {'class' : 'bday'})
        bday = BeautifulSoup(str(bday), 'lxml')
        bday = bday.span.string
    # handle case when bday is unavailable
    except AttributeError: 
        bday = None
    # very !!fucking!! important directly define type of vars
    return str(name), str(bday) 


if __name__ == '__main__':
    # read args
    args = parser.parse_args()
    
    # init parser class
    parser = WikiParser(
        category_url = args.category_url, 
        category = args.category, 
        threads  = args.threads,
    )
    
    # define func for parsing, in this case I want just get birth days
    parser.parse_func = parse_image
    
    # run parser
    parser()
    
    print("Columns in the output csv file don't have names so you need to rename them.")
    