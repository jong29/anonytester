import streamlit as st
from funcs.similarity import similarity
from funcs.utility import convert_df2csv

class syn_use:
    def __init__(self):
        if ("syn_data" in st.session_state) and ("raw_data" in st.session_state):
            if "val_similarity" not in st.session_state:
                with st.spinner("유사도 계산중..."):
                    st.session_state.val_similarity, st.session_state.attr_similarity, st.session_state.record_similarity, st.session_state.table_similarity\
                        = similarity(st.session_state.raw_data, st.session_state.syn_data)

            tab1, tab2, tab3, tab4 = st.tabs(["테이블 유사도", "특성 유사도", "속성 유사도", "레코드 유사도"])

            with tab1:
                self.table_sim()
            with tab2:
                self.val_sim()
            with tab3:
                self.attr_sim()
            with tab4:
                self.record_sim()
        else:
            st.markdown("##  \n##  \n## 원본데이터 또는 재현데이터가 업로드 되지 않았습니다")    

    def val_sim(self):
        st.markdown("### 특성 유사도")
        st.dataframe(st.session_state.val_similarity.round(decimals = 3).head(200))
        st.download_button(
            label="특성 유사도 csv로 저장",
            data = convert_df2csv(st.session_state.val_similarity),
            file_name=st.session_state.syn_file_name[:-4] + '_특성유사도.csv',
            mime='text/csv',
        )

    def attr_sim(self):
        st.markdown("### 속성 유사도")
        st.dataframe(st.session_state.attr_similarity)
        st.download_button(
            label="속성 유사도 csv로 저장",
            data = convert_df2csv(st.session_state.attr_similarity),
            file_name=st.session_state.syn_file_name[:-4] + '_속성유사도.csv',
            mime='text/csv',
        )

    def record_sim(self):
        st.markdown("### 레코드 유사도")
        st.dataframe(st.session_state.record_similarity.round(decimals = 3).head(200))
        st.download_button(
            label="레코드 유사도 csv로 저장",
            data = convert_df2csv(st.session_state.record_similarity),
            file_name=st.session_state.syn_file_name[:-4] + '_레코드유사도.csv',
            mime='text/csv',
        )

    def table_sim(self):
        st.markdown("### 테이블 유사도")
        st.dataframe(st.session_state.table_similarity)
        st.download_button(
            label="테이블 유사도 csv로 저장",
            data = convert_df2csv(st.session_state.table_similarity),
            file_name=st.session_state.syn_file_name[:-4] + '_테이블유사도.csv',
            mime='text/csv',
        )
