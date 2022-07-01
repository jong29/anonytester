#utility functions

def convert_df2csv(df):
    return df.to_csv().encode('utf-8-sig')