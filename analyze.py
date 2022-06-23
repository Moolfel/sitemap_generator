
# * COMPETITIVE STRUCTURED DATA ANALYSIS * #

## ASYNC SCRAPER
import asyncio
import aiohttp

## TIMERS
import time

## DATA CLEANING / ANALYSIS
import json 
import pandas as pd
from bs4 import BeautifulSoup
from lxml import etree

## CUSTOM HELPERS
from helpers.write_to_excel import excel_with_proper_col_widths
from helpers.clean_col_names import clean_col_names
from helpers.load_yaml import load_yaml
from helpers.convert_list_of_lists_to_single_list import convert_list_of_lists_to_single_list



###### ********* JOB CONFIGURATION ********* ######

config = load_yaml(filepath="config/config.yaml")

filename = config['output_filename']
input_file = config['input_filepath']

syntaxes = ["json-ld", "microdata", "opengraph", "rdfa"]



###### ********* ASYNC SCRAPER ********* ######

async def worker(url, session): ## SCRAPER
    headers = {
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "accept-language": "en-GB,en-US;q=0.9,en;q=0.8",
        "referer": "https://www.google.com/",
        "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36",
    }
    print("Worker() - getting url: " + url)
    async with session.get(url, headers=headers) as response:
        
        html = BeautifulSoup(await response.text(), "html.parser")
        json_script_elements = None
        
        list_of_json = []
        
        try: # check if page has json script tag
            json_script_elements = html.find_all('script', type='application/ld+json')    
            for script in json_script_elements:
                list_of_json.append(json.loads(script.text.replace("&quot;", "\""), strict=False))
                
        except AttributeError as e:
            logging.info(f"AttributeError - {url} - {e}")
                
        return [url, html, list_of_json]



async def scrape_and_extract(urlList): ## CALL SCRAPER WITH URL LIST

    async with aiohttp.ClientSession() as session:
        response = await asyncio.gather(  # gather all responses in a list
            *[worker(url, session) for url in urlList]  # get content for each url
        )

        return response

    

###### ********* EXTRACT METADATA ********* ######

def get_jsonld(html):
    
    url = html[0]
        
    if len(html[2]) > 0:

        out = []
        
        for item in html[2]:
            
            try: 
                graph = item['@graph'] # list of dicts
                out.append([item['@type'] for item in graph]) # get @type within @graph
                
            except BaseException as e:
                try:
                    out.append(item['@type']) # get @type directly
                    
                except BaseException as e:
                    print(f"Error - {url} - {e}")
        
        final = convert_list_of_lists_to_single_list(out)

        return { "URL": url,  "structured_data_types": final, "markup_type": "json-ld" }
    
    if len(html[2]) == 0:
        
        return { "URL": url,  "structured_data_types": [], "markup_type": "json-ld" }


def get_microdata(html):
    
    url = html[0]

    dom = etree.HTML(str(html[1]))
    
    nested_schema = dom.xpath('//*[@itemtype]') # itemtype == microdata type

    unpack_microdata = [item.attrib['itemtype'] for item in nested_schema]
    
    unpack_microdata = [item.replace('http://schema.org/', '') for item in unpack_microdata] # strip 'http://schema.org/' from each item
    
    if len(unpack_microdata) > 0: 
        return { "URL": url,  "structured_data_types": unpack_microdata, "markup_type": "microdata" }
    
    else:
        return { "URL": url,  "structured_data_types": [], "markup_type": "microdata" }



###### ********* SCHEMA CLIENT vs COMPETITIVE COMPARISONS ********* ######

def get_schema_client_vs_competitive_comparisons(schema_df):

    client_df = schema_df[schema_df["Site Type"] == "Client"]
    comp_df = schema_df[schema_df["Site Type"] == "Competitor"]

    client_unique_types = client_df[
        ["structured_data_types", "Page Type", "Site Type"]
    ].drop_duplicates()
    
    comp_unique_types = comp_df[
        ["structured_data_types", "Page Type", "Site Type"]
    ].drop_duplicates()

    matching = pd.merge(
        client_unique_types,
        comp_unique_types,
        on=["structured_data_types", "Page Type"],
        how="outer",
        suffixes=("_client", "_comp"),
    )

    matching["Opportunity"] = matching[
        "Site Type_client"
    ].isnull()  # if 'Site Type_client' is nan then True

    matching = matching.drop(  # drop cols 'Site Type_client' and 'Site Type_comp'
        columns=["Site Type_client", "Site Type_comp"]
    )

    output = matching[matching["Opportunity"] == True]  # filter to only opportunities

    return output



###### ********* MAIN FUNCT ********* ######

def main(csv_file):

    ### READ CSV & SCRAPE ###
    df = pd.read_csv(csv_file)

    import urllib.parse as urlparse

    df["Domain"] = df["URL"].apply(lambda x: urlparse.urlparse(x).netloc)
    df = df.groupby("Domain").head(25)

    start = time.time()
    response = asyncio.run(scrape_and_extract(urlList=df["URL"]))
    print(f"ASYNC - Scraping text took {time.time() - start} seconds")


    ### EXTRACT METADATA FROM SCRAPE ###
    start = time.time()
    # list_of_dicts = list(map(extract_metadata_from_html, response))
    jsonld = list(map(get_jsonld, response))
    microdata = list(map(get_microdata, response))
    print(f"Extracting metadata took {time.time() - start} seconds")


    ### COMBINE / CLEAN ###
    # combine
    df_jsonld = pd.DataFrame(jsonld)
    df_microdata = pd.DataFrame(microdata)
    df_all = pd.concat([df_jsonld, df_microdata])
    
    # clean 
    df_all = pd.DataFrame(df_all).explode("structured_data_types").reset_index() # convert cols with lists to rows 
    df_all["structured_data_types"] = df_all["structured_data_types"].fillna("Markup Type Not Found")


    ### FULL SCHEMA LIST DATASET CREATE ###
    final_full_dataset = pd.merge(df_all, df, on="URL")
    
    ### FINAL OPPS DATASET CREATE ###
    final_opportunities = get_schema_client_vs_competitive_comparisons(
        final_full_dataset
    )
    
    final_opportunities = final_opportunities[ # filter out if "structured_data_types" is "No Markup Type Found"
        final_opportunities["structured_data_types"] != "Markup Type Not Found"
    ]
        
    ### WRITING TO OUT ###
    final_full_dataset = final_full_dataset[
        ["Domain", "URL", "Page Type", "Site Type", "structured_data_types", "markup_type"]
    ]

    list_of_dfs = [final_full_dataset, final_opportunities]

    list_of_dfs = [clean_col_names(df) for df in list_of_dfs]  # clean up column names

    dict_of_dfs = {
        "full_dataset": list_of_dfs[0],
        "opportunities": list_of_dfs[1],
    }


    excel_with_proper_col_widths(
        filename= filename,
        dict_of_dfs = dict_of_dfs)
    
    return final_full_dataset


