import pandas as pd


def read_files(file_path):
    return pd.read_csv(file_path)
def drop_cols(df: pd.DataFrame, cols :list[str])->pd.DataFrame:
    '''  
    
    '''
    return df.drop(columns=cols )

def get_type_Info(df):
    return pd.DataFrame({"dtypes":df.dtypes, "nunique": df.nunique() }).T