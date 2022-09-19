import pandas as pd
import funcs.preprocessing as preprocessing
import funcs.risk_syn as risk_syn
import funcs.synthetic_reidentified as synthetic_reidentified
import funcs.similarity as similarity

import streamlit as st

def process_chunk(chunk, raw_file):
    # chunk = chunk.drop('an_usr_no', axis=1)
    prep_syn= preprocessing.preprocessing_syn(chunk)
    start = prep_syn.index[0]
    end = prep_syn.index[-1]
    print(f"start: {start}")
    print(f"end: {end}")
    
    raw_chunk = pd.read_csv(raw_file, encoding='utf-8', skiprows=range(1,start-1), nrows =end-start)
    # raw_chunk = raw_chunk.drop('USR_NO', axis=1)
    prep_raw = preprocessing.preprocessing_raw_horiz(raw_chunk, start)
    
    st.write(f"start: {start}, end: {end}")

    st.write("Raw")
    st.write(prep_raw)
    
    st.write("Synthetic")
    st.write(prep_syn)
    
    
    # 재식별 위험도
    _, _, _, syn_table = risk_syn.compute_risk(prep_syn.copy())
    print("위험도")
    print(syn_table)
    
#     # 유사도
    _, _, _, table_similarity = similarity.similarity(prep_raw, prep_syn, apply_hierarchy=False)
    print("유사도")
    print(table_similarity)
    
#     # 재식별도
    syn_reidentified, _ = synthetic_reidentified.syn_reidentified_datas(\
        prep_raw.copy(), prep_syn.copy(), K=-1, start_dim=1, end_dim=-1)

    print("재식별 레코드")
    print(syn_reidentified)
    