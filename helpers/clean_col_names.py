def clean_col_names(df):
    df.columns = [col.lower().replace(" ", "_") for col in df.columns]
    return df