import pandas as pd
import itertools
import numpy as np
from tqdm import tqdm
import funcs.risk as risk
import streamlit as st
from stqdm import stqdm


"""
data     : 데이터프레임
start_dim: 시작 차원 수, default = 1
end_dim  : 끝 차원 수,   default = -1
Priority : 속성 재식별 위험도로 우선순위 반환
ex) get_all_combinations(data=raw_data, 1,3)
    -> 원본 데이터 속성들의 1~3차원까지의 속성 조합

return: 속성 조합의 list
"""
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

"""
모두 같은 값을 가지는 속성(컬럼)들을 순회하면서 drop

return: 드랍된 후의 데이터 프레임 & 어떤 컬림이 드랍됐는지
"""
def is_unique(data):
    dropped_cols = []
    for attr in list(data.columns):
        a = data[attr].to_numpy()
        if (a[0] == a).all():
            data = data.drop(attr,axis=1)
            dropped_cols.append(attr)
    return data, dropped_cols

"""
data: 유일성 검사할 데이터 프레임
comb: 어떤 속성 조합을 검사할 것인지

return: 특정 속성 조합에서 유일한 데이터
"""
def find_unique_data(data, comb):
    #특정 속성조합 comb에서 유일한 데이터 반환
    unique = pd.DataFrame(data[list(comb)].drop_duplicates(keep=False)).reset_index()
    return unique


"""
원본 재식별 위험도 & 원본 재식별도

raw_data:   원본 데이터 프레임
K:          임계치
start_dim:  속성 조합 시작 dimension (get_all_combinations 함수에 설명 있음)
end_dim:    속성 조합 끝 dimension   (get_all_combinations 함수에 설명 있음)
"""
@st.cache(suppress_st_warning=True, show_spinner=False)
def raw_reidentified_datas(raw_data, one_attr, K=-1, start_dim=1, end_dim=-1):
    #=============원본 재식별 위험도=============
    # single_attr, one_attr, record, table = risk.compute_risk(raw_data.copy())
    Priority = list(one_attr.index)
    st.write(Priority)

    #=============원본 재식별도=============
    #K가 -1이면 전부 검사 (데이터 길이만큼)
    if(K==-1):
        K=len(raw_data)
    
    #모두 같은 값을 가지는 속성 제거
    data,dropped_cols  = is_unique(raw_data)
    print("모두 같은 값을 가져 drop된 속성: ", dropped_cols)
    #속성 조합 반환
    data =  data.reindex(columns = Priority)
    combs = get_all_combinations(data, start_dim, end_dim)

    reidentified_evidence = pd.DataFrame()
    # loop = tqdm(list(combs), total=len(combs), leave=True)
    loop = stqdm(list(combs))
    for comb in loop:
        #특정 속성 조합에서 유일한 데이터 반환
        raw_unique = find_unique_data(data, comb)
        if(len(raw_unique)!=0):
            reidentified_evidence = pd.concat([reidentified_evidence,raw_unique],axis=0)
            reidentified_evidence = reidentified_evidence.drop_duplicates(subset ="abst_row_num__",keep="first")
        if(len(reidentified_evidence) >= K):
            break
    reidentified_evidence = reidentified_evidence.sort_values("abst_row_num__").reset_index(drop=True)
    return reidentified_evidence