from ast import Not
import datetime
import io
import os
from typing import List
from zipfile import ZipFile

import pandas as pd

from xml_sitemap_generator.job import compressed_zip_of_multiple_files, generate_sitemap, get_parent_directory_from_url, main



def test__compressed_zip_of_multiple_files():
    # Generate the list contains sitemap files.
    csv_file = "input.csv"
    file_path = os.path.join('config', csv_file)
    
    urls_df = pd.read_csv(file_path)
    urls_df['first_directory'] = urls_df['URL'].apply(get_parent_directory_from_url) 

    sitemap_generated = generate_sitemap(df=urls_df, use_parent_directory=True)
    
    assert type(sitemap_generated) == list
    # Assert the length of generated list
    assert len(sitemap_generated) == 4
    # Check the match generated filename
    assert sitemap_generated[0] == 'sitemap_root_1.xml'
    assert sitemap_generated[1] == 'sitemap_services_1.xml'
    assert sitemap_generated[2] == 'sitemap_blog_1.xml'
    assert sitemap_generated[3] == 'sitemap_en-us_1.xml'

    # Compress the files.

    file_compressed = compressed_zip_of_multiple_files(sitemap_generated)

    assert file_compressed is not None, "Should not be none."


def test__generate_sitemap():
    csv_file = "input.csv"
    file_path = os.path.join('config', csv_file)
    
    urls_df = pd.read_csv(file_path)
    urls_df['first_directory'] = urls_df['URL'].apply(get_parent_directory_from_url) 

    sitemap_generated = generate_sitemap(df=urls_df, use_parent_directory=True)
    
    assert type(sitemap_generated) == list
    # Assert the length of generated list
    assert len(sitemap_generated) == 4
    # Check the match generated filename
    assert sitemap_generated[0] == 'sitemap_root_1.xml'
    assert sitemap_generated[1] == 'sitemap_services_1.xml'
    assert sitemap_generated[2] == 'sitemap_blog_1.xml'
    assert sitemap_generated[3] == 'sitemap_en-us_1.xml'

def test__main_job():
    csv_file = "input.csv"
    file_path = os.path.join('config', csv_file)
    
    output_generated = main(file=file_path)
    print(output_generated)
    # zip_file_path = os.path.join('config', csv_file)
    today = datetime.datetime.now().strftime('%Y-%m-%d')

    if not os.path.exists('test_files'):
        os.makedirs('test_files')

    generated_zip = 'sitemap_{}.zip'.format(today)
    print('---> generated', generated_zip)
    with ZipFile(generated_zip, 'r') as ref_zip:
        ref_zip.extractall('test_files')

    assert()
    