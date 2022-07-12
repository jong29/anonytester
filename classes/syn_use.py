import streamlit as st
from funcs.similarity import similarity

class syn_use:
    def __init__(self):
        st.header("데이터 유사도")
        val_similarity, attr_similarity, record_similarity, table_similarity = similarity(st.session_state.raw_data, st.session_state.syn_data)
        st.markdown("### 특성 유사도")
        st.dataframe(val_similarity.round(decimals = 3)[:100])
        st.markdown("### 속성 유사도")
        st.dataframe(attr_similarity)
        st.markdown("### 레코드 유사도")
        st.dataframe(record_similarity[:100].round(decimals = 3))
        st.markdown("### 테이블 유사도")
        st.dataframe(table_similarity)
