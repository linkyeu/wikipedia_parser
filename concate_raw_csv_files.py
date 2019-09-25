import pandas as pd
import argparse
import os

# parse input data
parser = argparse.ArgumentParser()
parser.add_argument('--files_folder', default=None, help="Path to parsed raw csv file for each profession")
parser.add_argument('--output_file_name', default='serial_killers', help="Name for output csv file")


def concat_raw_csv(folder: str, file_name: str):
    """Concatenate all raw parsed csv files.
    Args:
        folders: path to folder which contains raw csv file for 
            each profession parsed from wikiperdia.
        column_names: list of strings were each element is a name 
            of column in csv file
        file_name: output csv file name
        
    Returns a csv file with concatenated csv fils for each 
        profession.
    """
    column_names = ['name', 'bday', 'birth_place', 'img_url', 'url', 'lat', 'lon', 'category']
    folder_iterator = os.scandir(folder)
    data = pd.DataFrame()

    data = data.append(
        [pd.read_csv(file_csv.path, index_col=0) for file_csv in folder_iterator],
        ignore_index=True,
        verify_integrity=True,
        )
    
    data.columns = column_names
    data.to_csv(file_name)
    print(f'Output csv file saved to `{file_name}`')


if __name__ == '__main__':
    # read args
    args = parser.parse_args()
    
    # init parser class
    concat_raw_csv(
        folder = args.files_folder, 
        file_name = args.output_file_name, 
        )
    
    