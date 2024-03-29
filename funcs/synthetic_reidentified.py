import pandas as pd
import itertools
from stqdm import stqdm
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

@st.cache(suppress_st_warning=True, show_spinner=False)
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
def syn_reidentified_datas(raw_data, syn_data, K=-1, start_dim=1, end_dim=-1):

    if(K==-1):
        K=len(syn_data)
    
    raw_data,dropped_cols  = is_unique(raw_data)
    syn_data = syn_data.drop(dropped_cols, axis=1)

    # Distinct한 속성값이 많은 속성 순으로 정렬
    Priority = raw_data.nunique().sort_values(ascending=False).index
    raw_data =  raw_data.reindex(columns = Priority)
    combs = get_all_combinations(raw_data, start_dim, end_dim)
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
    return syn_reident, dropped_cols

