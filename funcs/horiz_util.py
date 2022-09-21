import pandas as pd
import funcs.preprocessing as preprocessing
import funcs.risk_syn as risk_syn
import funcs.synthetic_reidentified as synthetic_reidentified
import funcs.similarity as similarity

import streamlit as st
import copy

def process_chunk(chunk, raw_file, dims, record_num):
    # chunk = chunk.drop('an_usr_no', axis=1)
    # chunk = pd.read_csv(syn_file, encoding='utf-8',skiprows=range(1,st.session_state.checked_rows+1), chunksize=st.session_state.div_num)
    prep_syn= preprocessing.preprocessing_syn(chunk)
    start = prep_syn.index[0]
    end = prep_syn.index[-1]


    raw_chunk = pd.read_csv(copy.deepcopy(raw_file), encoding='utf-8', skiprows=range(1,start), nrows=end-start)
    # raw_chunk = raw_chunk.drop('USR_NO', axis=1)
    prep_raw = preprocessing.preprocessing_raw_horiz(raw_chunk, start)
    
    # debugging
    st.write(f"start: {start}, end: {end}")
    st.write("Raw")
    st.write(prep_raw)
    st.write("Synthetic")
    st.write(prep_syn)
    
#     # 재식별도
    syn_reidentified, _ = synthetic_reidentified.syn_reidentified_datas(\
        prep_raw.copy(), prep_syn.copy(), K=record_num, start_dim=dims[0], end_dim=dims[1])
    
    # 재식별 위험도
    _, _, _, syn_table = risk_syn.compute_risk(prep_syn.copy())
    st.write("위험도")
    st.write(syn_table)
    
#     # 유사도
    _, _, _, table_similarity = similarity.similarity(prep_raw.copy(), prep_syn.copy(), apply_hierarchy=False)
    st.write("유사도")
    st.write(table_similarity)

    st.write("재식별 레코드")
    st.write(syn_reidentified)
    