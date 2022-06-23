import pandas as pd
from datetime import datetime

import os

dirpath = os.getcwd()

date = datetime.today().strftime('%Y-%m-%d')
time_of_day = datetime.today().strftime('%H:%M')

def excel_with_proper_col_widths(filename, dict_of_dfs, export_index=False):
    
    file_name = f"{filename}_{date}.xlsx"
    
    output_path = os.path.join(dirpath,file_name)
    
    writer = pd.ExcelWriter(output_path, engine='xlsxwriter')
    
    i = 1 
    
    for sheetname, df in dict_of_dfs.items():  # {sheetname: df, sheetname2: df2}
        
        print(f'Sheetname #{i}: {sheetname}')
        i += 1
                
        df.to_excel( # df from dict_of_dfs
            writer,  # send df to writer
            sheet_name=f'{sheetname}', # sheetname from dict_of_dfs
            index=export_index
        )  
        
        worksheet = writer.sheets[sheetname]  # pull worksheet object
        
        for idx, col in enumerate(df):  # loop through all columns
            
            series = df[col]
            
            max_len = max(( # get max len of series for col sizing
                series.astype(str).map(len).max(),  # len of largest item
                len(str(series.name))  # len of column name/header
                )) + 1  # adding a little extra space
            
            if max_len < 70: # check if max_len is less than 70
                
                worksheet.set_column(idx, idx, max_len)  # then set column width
                
            else: 
                
                worksheet.set_column(idx, idx, 70) # if max_len is greater than 70, set column width to 70
                
    writer.save()
    
    return output_path

