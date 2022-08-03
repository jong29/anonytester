import pandas as pd
import streamlit as st
from stqdm import stqdm



#전역변수 구분자
delimiter = '/'

#특성 유사도
def numeric_similarity(vec ,max_val ,min_val):
    raw_val = vec[0]
    syn_val= vec[1]
    return 1-(abs(raw_val-syn_val)/(max_val-min_val))

def category_similarity(vec, distinct):
    raw_cate     = vec[0]
    syn_cate     = vec[1]
    syn_connected = syn_cate.count(delimiter)
    if(syn_connected == 0):
        if(raw_cate == syn_cate):
            return 1
        else:
            return 0
    else:
        return round(1-(syn_connected/distinct),3)
    
def category_similarity_hier(vec, distinct, column_name, hierarchy_table):
    raw_cate     = vec[0]
    syn_cate     = vec[1]
    syn_connected = syn_cate.count(delimiter)
    if(syn_connected == 0):
        if(raw_cate == syn_cate):
            return 1
        else:
            return round(1-((hierarchy_table[column_name][syn_cate]-1)/distinct),3)
    else:
        return round(1-(syn_connected/distinct),3)

def hierarchy_groupby(raw_data, syn_data, similarity_df, category_cols):
    # 임의 계층 구조 테이블 생성하기 위해 재현데이터 속성값이
    # 원본데이터에 존재하지 않는것을 비교 확인하기 위해 원본 재현성값
    # distinct value dictionary 생성
    raw_distinct, syn_distinct = dict(), dict()
    for col in category_cols:
        raw_distinct[col]= raw_data[col].unique().tolist()
        syn_distinct[col]= syn_data[col].unique().tolist()
    
    # 원본데이터에 속성값이 존재하지 않아 계층구조 상승을 의미할때
    # 몇개 원본 속성을 포함하는지 찾기 위해 groupby해서 확인
    for attr in syn_distinct:
        uniqval = list()
        for val in syn_distinct[attr]:
            if not (val in raw_distinct[attr]):
                uniqval.append(val)
        syn_distinct[attr]= uniqval
    
    # 계층상승한 속성값의 레코드 선택하여 해당되는 원본 distinct values찾아
    # 몇개의 하위속성에 해당되는지 세어 딕셔너리로 저장하여 반환
    for attr in syn_distinct:
        child_count = dict()
        for val in syn_distinct[attr]:
            grpby = similarity_df.loc[similarity_df[attr+"_y"] == val]
            children = grpby[attr+'_x'].nunique()
            child_count[val] = children
        syn_distinct[attr] = child_count
    
    return syn_distinct
    
def val_similarity(raw_data, syn_data, apply_hierarchy=False):
    #========================특성 유사도========================
    raw_cols = list(raw_data.columns)
    similarity_df = pd.merge(raw_data,syn_data, left_index=True, right_index=True, how="inner")

    # for comb in loop:
    
    for col in raw_cols:
        #type 맞춤 작업
        try:
            similarity_df[col+"_y"] = similarity_df[col+"_y"].astype("float")    
            similarity_df[col+"_x"] = similarity_df[col+"_x"].astype("float")
        except:
            similarity_df[col+"_x"] = similarity_df[col+"_x"].astype("str")
            similarity_df[col+"_y"] = similarity_df[col+"_y"].astype("str")

    numeric_cols = list(similarity_df.select_dtypes(include=["int","float"]).columns)
    category_cols = list(similarity_df.select_dtypes(include=["object"]).columns)

    for idx in range(len(numeric_cols)):
        numeric_cols[idx] = numeric_cols[idx][:-2]
    numeric_cols = set(numeric_cols)
    for idx in range(len(category_cols)):
        category_cols[idx] = category_cols[idx][:-2]
    category_cols = set(category_cols)

    #apply groupby hierarchy:
    if apply_hierarchy:
        #groupby heirarchy
        hierarchy_df = hierarchy_groupby(raw_data, syn_data, similarity_df, category_cols)
        with st.spinner("수치형 데이터 계산중..."):
            num_loop = stqdm(list(numeric_cols))
            for col in num_loop:
                similarity_df[col] = similarity_df[[col+"_x",col+"_y"]].apply(numeric_similarity, \
                                                                        args=(similarity_df[col+"_x"].max(),similarity_df[col+"_x"].min()), axis=1)
        with st.spinner("범주형 데이터 계산중..."):
            cat_loop = stqdm(list(category_cols))
            for col in cat_loop:
                similarity_df[col] = similarity_df[[col+"_x",col+"_y"]].apply(category_similarity_hier, args=[similarity_df[col+"_x"].nunique(), col, hierarchy_df], axis=1)
    else:
        with st.spinner("수치형 데이터 계산중..."):
            num_loop = stqdm(list(numeric_cols))
            for col in num_loop:
                similarity_df[col] = similarity_df[[col+"_x",col+"_y"]].apply(numeric_similarity, \
                                                                        args=(similarity_df[col+"_x"].max(),similarity_df[col+"_x"].min()), axis=1)
        with st.spinner("범주형 데이터 계산중..."):
            cat_loop = stqdm(list(category_cols))
            for col in cat_loop:
                similarity_df[col] = similarity_df[[col+"_x",col+"_y"]].apply(category_similarity, args=[similarity_df[col+"_x"].nunique()], axis=1)

    similarity_df = similarity_df[raw_cols]
    return similarity_df

#속성 유사도
def attr_simiarlity(similarity_df):
    attr_simiarlity_df = pd.concat([similarity_df.mean(),\
                                   similarity_df.max(),\
                                   similarity_df.min(),\
                                   similarity_df.std()],axis=1)
    attr_simiarlity_df.columns = ['mean','max','min','std']
    attr_simiarlity_df.reset_index(inplace=True)
    attr_simiarlity_df.rename(columns={'index':'속성'}, inplace=True)
    return attr_simiarlity_df

def record_similarity(similarity_df):
    record_similarity_df = pd.DataFrame(columns=['mean','std','max','min'])
    record_similarity_df['mean'] = similarity_df.mean(axis=1)
    record_similarity_df['std'] = similarity_df.std(axis=1)
    record_similarity_df['max'] = similarity_df.max(axis=1)
    record_similarity_df['min'] = similarity_df.min(axis=1)
    return record_similarity_df

def table_similarity(record_similarity_df):
    table_similarity_df = pd.DataFrame([[  record_similarity_df['mean'].mean(),\
                                record_similarity_df['mean'].std(),\
                                record_similarity_df['mean'].max(),\
                                record_similarity_df['mean'].min()]], \
                                    columns = ['mean', 'std', 'max', 'min']) 
    return table_similarity_df

@st.cache(show_spinner=False, suppress_st_warning=True)
def similarity(raw_data, syn_data, apply_hierarchy):
    val_similarity_df = val_similarity(raw_data,syn_data,apply_hierarchy)
    attr_similarity_df = attr_simiarlity(val_similarity_df)
    record_similarity_df = record_similarity(val_similarity_df)
    table_similarity_df = table_similarity(record_similarity_df)
    return val_similarity_df, attr_similarity_df, record_similarity_df, table_similarity_df