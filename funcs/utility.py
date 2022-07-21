import pandas as pd
import funcs.preprocessing as pre

#utility functions

def convert_df2csv(df):
    return df.to_csv().encode('utf-8-sig')

def combine_dims(dim1, dim2):
    comb = pd.concat([dim1, dim2], axis=0)
    comb = comb.drop_duplicates(subset ="abst_row_num__",keep="first")
    comb = comb.drop(comb.columns[0:1], axis=1)
    comb = comb.set_index('abst_row_num__')
    return comb

def combine_dims_recur(dim_list):
    if len(dim_list) != 1:
        comb = pd.concat([dim_list[0], dim_list[1]], axis=0)
        comb = comb.drop_duplicates(subset ="abst_row_num__",keep="first")
        dim_list.pop(0)
        dim_list.pop(0)
        dim_list.insert(0, comb)
        combine_dims_recur(dim_list)
    return dim_list

def load_data_raw(file):
    df = pd.read_csv(file, encoding='utf-8')
    df = pre.preprocessing_raw(df)
    return df

def load_data_syn_high(file):
    df = pd.read_csv(file, encoding='utf-8')
    df = pre.preprocessing_high(df)
    return df

def load_data_syn_low(file):
    df = pd.read_csv(file, encoding='utf-8')
    df = pre.preprocessing_low(df)
    return df

def to_str(drop_list):
    return ", ".join(drop_list)