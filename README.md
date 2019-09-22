# Parser for wikipedia.org 
__Parser supports both russiand and english languages.__</br>
I wrote this parser as part of my Career Guidence pet-project to collect open source data (wikipedia.org in this particular case).
This parser designed in way that anyone be able to extend it functionality by redefining `parse_func` method. More details in the following description. </br>

Parser works with wikipedia categories pages. For example if you interseted in data about `science teachers` you are googling `wiki science teachers category` after that google will return you a link to this [category](https://en.wikipedia.org/wiki/Category:Science_teachers). Usually it contains alphabetic list of profiles of persons belonging to this category. Using this parser you can parse any data you need from these profiles.

### Use case - parsing birth days of serial killers
1) __Get URL for category page__ with structure `https://en.wikipedia.org/wiki/Category:x...x`.</br>
Such URLs mean that page contains profiles of persons from some category. To get this URL you can just google something like `wiki category serial killers` and google gives you `https://en.wikipedia.org/wiki/Category:Serial_killers`. 
2) __Define a__ `parse_func`. This is a empty method in base parser class which should be defined by user. It is defines what data should be parsed from a single personal profile. Here is an example of such function for parsing birth days from a person profile. Parser uses multiprocessing so it is important that types of outputs from a function should be defined directly in the function.</br>
```
def parse_bday(x: tuple):
    """Returns name and birth day of a person derived from wikipedia person's profile page.
    
    Args:
        x (str): url to personal profile of a person on wikipedia
    """
    # unpack tuple
    name, url = x  
    
    # parse url
    html = BeautifulSoup(urllib.request.urlopen(url), 'lxml')
    
    # parse required data
    try:
        bday = html.find_all('span', {'class' : 'bday'})
        bday = BeautifulSoup(str(bday), 'lxml')
        bday = bday.span.string
        
    # handle case when bday is unavailable
    except AttributeError: 
        bday = None
        
    # for multiprocessing is very important to directly define type of output vars
    return str(name), str(bday) 
```
__Explanation:__ As you can see the function takes a tuple with predefined structure as input argument. The tuple has a following structure `('Jhon Smith', 'URL to his wikipedia profile')`. The purpose of this function is to define how to parse required by user data from a profile. </br>

3) __Run parser__ ```python wiki_parser.py --category_url='https://en.wikipedia.org/wiki/Category:Serial_killers' --category='serial_killers' --threads=10```</br>
`--category` all parsed profiles will have category name in output csv file. Just to know what category was parsed.
`--threads` this var defines how many processes you want to use while parsing. Some categories for example football players containing 30K profiles and it takes a while to parse it.</br>
__Explanation__: Parser will take defined `parse_func` and using multiprocessing will parse data from each profile in category and __save results in csv file in the current folder__.

### Parsing image of a person from category
All as decribed above except `pars_func`:

```
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
```

### TODO:
- support english wikipedia (change prefix) DONE
- pre-define several methods for `parse_func`
- add use case with parsing images DONE



