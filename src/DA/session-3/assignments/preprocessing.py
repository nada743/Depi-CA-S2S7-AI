import pandas as pd

def Read_data_file(file_path):
    try:
        return pd.read_csv(file_path)
    except FileNotFoundError:
        print("Error: File not found.")
        return None
    except Exception as e:
        print(f"Error reading file: {e}")
        return None

def Drop_unnecessary_features(df, cols_to_drop):
    return df.drop(columns=cols_to_drop)

def Check_data_type(df):
    return pd.DataFrame({
        "dtypes": df.dtypes,
        "nunique": df.nunique()
    }).T