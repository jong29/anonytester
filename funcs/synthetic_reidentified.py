import pandas as pd
import itertools
import numpy as np
from tqdm import tqdm
from stqdm import stqdm
import funcs.risk_syn as risk
import streamlit as st

def is_unique(data):
    dropped_cols = []
    for attr in list(data.columns):
        a = data[attr].to_numpy()
        if (a[0] == a).all():
            data = data.drop(attr,axis=1)
            dropped_cols.append(attr)
    return data, dropped_cols

def find_unique_data(data, comb):
    #특정 속성조합 comb에서 유일한 데이터 반환
    unique = pd.DataFrame(data[list(comb)].drop_duplicates(keep=False)).reset_index()
    return unique

def get_all_combinations(data, start_dim=1,end_dim=-1):
    all_combinations = list()
    if(start_dim == -1):
        start_dim = len(data.columns)
    if(end_dim == -1):
        end_dim = len(data.columns)
    for r in range(start_dim, end_dim+1):
        combinations_object = itertools.combinations(list(data.columns), r)
        combinations_list = list(combinations_object)
        all_combinations += combinations_list
    return list(all_combinations)

@st.cache(suppress_st_warning=True, show_spinner=False)
def syn_reidentified_datas(raw_data, syn_data, syn_one_attr, K=-1, start_dim=1, end_dim=-1):
    # single_attr, one_attr, record, table = risk.compute_risk(syn_data.copy())
    Priority = list(syn_one_attr.index)

    if(K==-1):
        K=len(syn_data)
    
    raw_data,raw_dropped_cols  = is_unique(raw_data)
    syn_data = syn_data.drop(raw_dropped_cols, axis=1)
    print("모두 같은 값을 가져 drop된 속성: ", raw_dropped_cols)

    raw_data =  raw_data.reindex(columns = Priority)
    combs = get_all_combinations(raw_data, start_dim, end_dim)
    print("총: " + str(len(combs)) + " 개의 속성 조합을 검사합니다")
    
    # loop = tqdm(list(combs), total=len(combs), leave=True)
    loop = stqdm(list(combs))

    temp_uniques=pd.DataFrame()
    syn_reident=pd.DataFrame()
    for comb in loop:
        raw_unique = find_unique_data(raw_data,comb)
        syn_unique = find_unique_data(syn_data,comb)
        if((len(raw_unique) != 0) & (len(syn_unique) != 0)):
            temp_uniques = pd.concat([raw_unique,syn_unique],axis=0)
            temp_uniques = temp_uniques[temp_uniques.duplicated(keep=False)]
            if(len(temp_uniques) != 0):
                syn_reident = pd.concat([syn_reident,temp_uniques],axis=0)
                syn_reident = syn_reident.drop_duplicates(subset="abst_row_num__",keep="first")
                if(len(syn_reident) >= K):
                    break
    if not syn_reident.empty:
        syn_reident = syn_reident.sort_values('abst_row_num__').reset_index(drop=True)
    return syn_reident

