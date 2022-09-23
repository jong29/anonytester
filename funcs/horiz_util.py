import pandas as pd
import funcs.preprocessing as preprocessing
import funcs.risk_syn as risk_syn
import funcs.synthetic_reidentified as synthetic_reidentified
import funcs.similarity as similarity

import streamlit as st
import copy

# 청크별로 재식별도 위험도 유사도 계산
def process_chunk(chunk, raw_file, dims, record_num):
    prep_syn = chunk.drop(st.session_state.syn_chunk_drop, axis=1)
    prep_syn= preprocessing.preprocessing_syn(prep_syn)
    start = prep_syn.index[0]
    end = prep_syn.index[-1]

    raw_chunk = pd.read_csv(copy.deepcopy(raw_file), encoding='utf-8', skiprows=range(1,start), nrows=end-start)
    raw_chunk = raw_chunk.drop(st.session_state.raw_chunk_drop, axis=1)
    prep_raw = preprocessing.preprocessing_raw_horiz(raw_chunk, start)
    
    # 재식별도
    syn_reidentified, _ = synthetic_reidentified.syn_reidentified_datas(\
        prep_raw.copy(), prep_syn.copy(), K=record_num, start_dim=dims[0], end_dim=dims[1])
    
    # 재식별 위험도
    _, _, _, syn_table = risk_syn.compute_risk(prep_syn.copy())
    
    # 유사도
    _, _, _, table_similarity = similarity.similarity(prep_raw.copy(), prep_syn.copy(), apply_hierarchy=False)

    #lets do one garbage collection here

    # debugging
    # st.write(f"start: {start}, end: {end}")
    # st.write("Raw")
    # st.write(prep_raw)
    # st.write("Synthetic")
    # st.write(prep_syn)

    # st.write("위험도")
    # st.write(syn_table)

    # st.write("유사도")
    # st.write(table_similarity)

    # st.write("재식별 레코드수")
    # st.write(len(syn_reidentified))

    # st.write("재식별 레코드")
    # st.write(syn_reidentified)
    
    return syn_reidentified, syn_table, table_similarity

# 기타 정보 취합
def collect_chunk(reid_collection, other_collection, reid_chunk, chunk_metadata):
    reid_collection = pd.concat([reid_collection, reid_chunk], ignore_index=True)
    other_collection += f"회차: {chunk_metadata[0]}, 시작행: {chunk_metadata[1]}, 끝행: {chunk_metadata[2]}, 전체 레코드수: {chunk_metadata[3]}, 재식별 레코드수: {chunk_metadata[4]}, 재식별도: {chunk_metadata[4]/chunk_metadata[3]}, 재식별 위험도: {chunk_metadata[5]}, 유사도: {chunk_metadata[6]}\n"
    return reid_collection, other_collection

# 속성 제거 위해 원본데이터 속성 추출
@st.cache(show_spinner=False, suppress_st_warning=True)
def get_raw_cols(raw_file):
    return pd.read_csv(raw_file, encoding='utf-8', index_col=0, nrows=0).reset_index().columns.tolist()

# 속성 제거 위해 재현데이터 속성 추출
@st.cache(show_spinner=False, suppress_st_warning=True)
def get_syn_cols(syn_file):
    all_col = pd.read_csv(syn_file, encoding='utf-8', nrows=1)
    proc_col = preprocessing.remove_unneccessary_columns(all_col)
    syn_data = proc_col.set_index('abst_row_num__')
    final_col = syn_data.columns
    return final_col