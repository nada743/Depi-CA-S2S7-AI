from config import data_path, cols_to_drop
from preprocessing import (
    Read_data_file,
    Drop_unnecessary_features,
    Check_data_type
)


df = Read_data_file(data_path)

if df is not None:

    print("Original Data:")
    print(df.head())

    df = Drop_unnecessary_features(df, cols_to_drop)

    print("\nAfter Removing Unnecessary Features:")
    print(df.head())

    print("\nData Type Information:")
    print(Check_data_type(df))