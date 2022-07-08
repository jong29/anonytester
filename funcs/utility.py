import pandas as pd

#utility functions

def convert_df2csv(df):
    return df.to_csv().encode('utf-8-sig')

def combine_dims(dim1, dim2):
    comb = pd.concat([dim1, dim2], axis=0)
    comb = comb.drop_duplicates(subset ="abst_row_num__",keep="first")
    comb = comb.drop(comb.columns[0:1], axis=1)
    comb = comb.set_index('abst_row_num__')
    return comb