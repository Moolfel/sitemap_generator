import datetime
import os
from zipfile import ZipFile

import pandas as pd

from xml_sitemap_generator.job import compressed_zip_of_multiple_files, generate_sitemap, get_parent_directory_from_url, main


class TestJobs:

    def test__job__compressed_zip_of_multiple_files(self):
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

    def test__job__generate_sitemap(self):
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

    def test__job__main(self):
        csv_file = "input.csv"
        file_path = os.path.join('config', csv_file)
        
        output_generated_from_upload = main(file=file_path)
        today = datetime.datetime.now().strftime('%Y-%m-%d')

        if not os.path.exists('test_files'):
            os.makedirs('test_files')

        generated_zip = 'sitemap_{}.zip'.format(today)

        # Extract the generated zip in a specific folder
        with ZipFile(generated_zip, 'r') as ref_zip:
            ref_zip.extractall('test_files')

        extracted_files = os.listdir('test_files')

        # Check extracted files from zip matches the generated files from upload
        assert output_generated_from_upload[0] == extracted_files[0]
        assert output_generated_from_upload[1] == extracted_files[1]
        assert output_generated_from_upload[2] == extracted_files[2]
        assert output_generated_from_upload[3] == extracted_files[3]
