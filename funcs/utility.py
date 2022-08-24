import pandas as pd
import funcs.preprocessing as pre
import io

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

def comb_org(df2org):
    df2org.sort_values('abst_row_num__', inplace=True, ignore_index=True)
    df2org.drop('Unnamed: 0', axis=1, inplace=True)
    return df2org

# 일반 원본
def load_data_raw(file):
    try:
        df = pd.read_csv(file, encoding='utf-8')
    except ValueError:
        df = pd.read_csv(file, encoding='cp949')
    df = pre.preprocessing_raw(df)
    return df

# 수평분할 원본
def load_raw_iter(file):
    try:
        df = pd.read_csv(file, encoding='utf-8')
    except ValueError:
        df = pd.read_csv(file, encoding='cp949')
    return df

# 일반 재현
def load_data_syn(file, records):
    try:
        df = pd.read_csv(file, encoding='utf-8')
    except ValueError:
        df = pd.read_csv(file, encoding='cp949')
    df = pre.preprocessing_syn(df)
    return df

# 수평분할 재현
def load_syn_iter(file, records):
    try:
        df = pd.read_csv(file, encoding='utf-8')
    except ValueError:
        df = pd.read_csv(file, encoding='cp949')
    return df

def to_str(drop_list):
    return ", ".join(drop_list)

def count_lines(syn_file_iterator):
    for chunk_number, chunk in enumerate(syn_file_iterator):
    # some code here, if needed
        pass
    return chunk_number+1