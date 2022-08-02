import pandas as pd
from ast import literal_eval
from joblib import Parallel, delayed
import streamlit as st
import json
from stqdm import stqdm
import timeit

#====================================원본 전처리=============================
"""
원본 데이터 불러오기
data_path = 데이터 경로
drop_cols = 제거할 속성 (키속성 등)
"""

@st.cache(show_spinner=False, suppress_st_warning=True)
def preprocessing_raw(raw_data):
    raw_data = raw_data.reset_index().rename(columns={'index':'abst_row_num__'})
    raw_data['abst_row_num__'] = raw_data['abst_row_num__'] + 1
    raw_data = raw_data.set_index("abst_row_num__")
    raw_data.columns = raw_data.columns.str.lower()
    return raw_data

#====================================고수준 전처리=============================
@st.cache(show_spinner=False, suppress_st_warning=True)
def preprocessing_high(high_data):
    high_data = remove_unneccessary_columns(high_data)
    high_data = preprocess_highlevel_df(high_data)
    high_data = high_data.set_index('abst_row_num__')
    high_data.columns = high_data.columns.str.lower()
    return high_data

@st.cache(show_spinner=False, suppress_st_warning=True)
def preprocess_highlevel_df(syn_data):
    syn_cols = list(syn_data.columns)
    preprocessed_syn_data=pd.DataFrame()
    ##### 고수준 json 처리
    loop = stqdm(list(syn_cols))
    for c in loop:
        preprocessed_syn_data[c] = syn_data[c].apply(preprocess_json)
    return preprocessed_syn_data

#====================================저수준 전처리=============================
def preprocessing_low(low_data):
    low_data = remove_unneccessary_columns(low_data)
    low_data = preprocess_lowlevel_df(low_data)
    low_data = low_data.set_index('abst_row_num__')
    low_data.columns = low_data.columns.str.lower()
    return low_data
    
# ratio 값이 2개 이상이면 연결형, 아니면 최빈값 형태로 반환
def preprocess_json(x):
    if(str(x)[0]=="["):
        try:
            val_list = json.loads(x)
            # try: #int가 json으로 인식되는 경우에 dict로 처리하지 않고 바로 int 그대로 반환
            if(len(val_list)==1):
                return val_list[0]['name']
            else:
                connected = ''
                connected += val_list[0]['name']
                for i in range(1,len(val_list)):
                    connected += '/ '
                    connected += val_list[i]['name']
                return connected
        except: return x
        # else: return x
    else: return x

# ratio parsing 위해 json형태인지 확인
def validateJSON(jsonData):
    try:
        json.loads(jsonData)
    except:
        return False
    return True

def preprocess_lowlevel_df(syn_data):
    syn_cols = list(syn_data.columns)
    preprocessed_syn_data=pd.DataFrame()
    loop = stqdm(list(syn_cols))
    for c in loop:
        preprocessed_syn_data[c] = syn_data[c].apply(preprocess_json)
    return preprocessed_syn_data

def remove_unneccessary_columns(syn_data):
    for c in syn_data.columns:
        if(c[-6:]=="stddev"):
            syn_data.drop(c, axis=1, inplace=True)
        elif(c[-3:]=="max"):
            syn_data.drop(c, axis=1, inplace=True)
        elif(c[-3:]=="min"):
            syn_data.drop(c, axis=1, inplace=True)
        elif(c[-3:]=="avg"):
            syn_data.rename(columns={c:c[:-4]}, inplace=True)
    try:
        syn_data.drop("rec_disim", axis=1, inplace = True)
        syn_data.drop("rec_disim_concat", axis=1, inplace = True)
        syn_data.drop("rec_disim_numerical", axis=1, inplace = True)
    except:
        pass
    return syn_data  

def preprocess_lowlevel_df_parallel(syn_data):
    syn_cols = list(syn_data.columns)
    preprocessed_syn_data=pd.DataFrame()
    with Parallel(n_jobs=-1,prefer="threads") as parallel:
        reuslts = parallel(delayed(preprocess_lowlevel_df_parallel_func_address)\
            (syn_data, col) for col in syn_cols)
    preprocessed_syn_data = pd.concat(reuslts, axis=1)
    return preprocessed_syn_data

# 저수준 데이터 전처리 병렬 버전 (function address)
def preprocess_lowlevel_df_parallel_func_address(syn_data, col):
    return syn_data[col].apply(preprocess_json)
#====================================저수준 전처리=============================

