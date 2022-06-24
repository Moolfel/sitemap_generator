import pandas as pd
import datetime 
from jinja2 import Template
from urllib.parse import urlparse
import zipfile

today = datetime.datetime.now().strftime('%Y-%m-%d')

def compressed_zip_of_multiple_files(file_list):
    # create sitemap.zip file from file_list (list of dataframes)
    with zipfile.ZipFile(f'sitemap_{today}.zip', 'w') as f:
        
        for file in file_list:
            
            # write filename with .xml extension
            id = file[2] # either first_directory or 'full'
            xml_file = file[0] # actual template
            index = file[1] + 1 # num of file in list
            
            filename = f'sitemap_{id}_{index}.xml' 
            
            f.writestr(filename, xml_file)
            
            yield  filename


def get_parent_directory_from_url(string_url):
    paths = urlparse(string_url).path.split('/') # split path into list of directories

    # at least 2 directories to include as "first_directory" vs "root"
    i = 0
    for item in paths: 
        if item != '':
            i += 1
    
    if i >= 2:
        return paths[1]

    else:
        return 'root'

def generate_sitemap(df, use_parent_directory=True):
    # create sitemap and save to sitemap.xml file
    sitemap_template = Template('''
    <urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">        
        {% for row in urls_df.itertuples() %}
        <url>
        <loc>{{ row.loc }}</loc>
        <lastmod>{{ row.lastmod_date }}</lastmod>
        <changefreq>{{ row.changefreq }}</changefreq>
        <priority>{{ row.priority }}</priority>
        </url>
        {% endfor %}
    </urlset>
    ''')
    num_of_items = 50000
    
    
    if use_parent_directory:
        
        sitemap_list = []
        
        # for directory in first_directory
        for first_directory in df['first_directory'].unique():
            sitemap_df = df[df['first_directory'] == first_directory]
            
            # get url chunks of sitemap_df
            urls_df_chunks = [sitemap_df[i:i+num_of_items] for i in range(0, len(sitemap_df), num_of_items)]
            
            # enum each chunk (will make the {i} unique for each first_directory chunk)
            for i, chunk in enumerate(urls_df_chunks):
                sitemap_list.append(
                    [
                        sitemap_template.render(urls_df = chunk),
                        i,
                        first_directory
                    ]
                )

        gen = compressed_zip_of_multiple_files(sitemap_list)
                
        return list(gen)
        # list sitemap names 
       
        
        
    else:
        # split urls_df into chunks of 50
        urls_df_chunks = [df[i:i+num_of_items] for i in range(0, len(df), num_of_items)]
        
        sitemap_list = []
        for i, chunk in enumerate(urls_df_chunks):
            sitemap_list.append(
                [
                    sitemap_template.render(urls_df = chunk),
                    i,
                    'full'
                ]
            )

        # create sitemap.xml file zip 
        gen = compressed_zip_of_multiple_files(sitemap_list)

        return list(gen)

def main(file, lastmod_date = None, changefreq = None, priority = None):
    
    urls_df = pd.read_csv(file)
    
    # update urls_df index col 0 to be 'loc'
    urls_df.columns = ['loc']
    
    urls_df['first_directory'] = urls_df['loc'].apply(get_parent_directory_from_url)
            
    if lastmod_date is None:
        lastmod_date = today
    
    if changefreq is None:
        changefreq = 'daily'
    
    if priority is None:
        priority = '0.5'
    
    urls_df['lastmod_date'] = lastmod_date
    urls_df['priority'] = priority
    urls_df['changefreq'] = changefreq
    
    return generate_sitemap( df = urls_df, use_parent_directory = True )

    
   
# df = pd.read_csv('sitemap_urls.csv')
# # df = pd.read_csv('urls.csv')

# main(
#     urls_df = df
# )
