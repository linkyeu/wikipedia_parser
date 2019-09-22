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

from wiki_parser import *

# parse input data
parser = argparse.ArgumentParser()
parser.add_argument('--categories_dict', default=None, help="Copy and paste url for required category")
parser.add_argument('--threads', default=10, help="Number of processing involved for parsing.")


if __name__ == '__main__':
    # read args
    args = parser.parse_args()
    
    for i in args.categories_dict.items():
        category_name = i[0]
        category_url  = i[1]
        parser = WikiParser(
            category_url = category_url, 
            category = category_name, 
            threads  = args.threads)
    
        # define func for parsing, in this case I want just get birth days
        parser.parse_func = parse_all
    
        # run parser
        parser()
    
    print("Columns in the output csv file don't have names so you need to rename them.")
    
