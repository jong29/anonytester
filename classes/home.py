#modules
import streamlit as st
import pandas as pd

#functions
from funcs.raw_reidentified import get_all_combinations

class home:
    def __init__(self):
        st.write("# Welcome to Anonymity Tester!")
        st.markdown(
            """
            Anony Tester는 재현데이터의 안정성 및 유용성 지표를 평가합니다.
            """
        )
        col1, col2 = st.columns(2)
        raw_data_file = col1.file_uploader("Upload Raw Data")
        if "raw_data" not in st.session_state:
            if raw_data_file is not None:
                st.session_state.raw_data  = load_data_raw(raw_data_file)
            else:
                st.experimental_rerun

        if st.session_state.raw_data is not None:
            add_selectbox = col1.multiselect(
                "제거할 속성을 선택해주세요",
                list(st.session_state.raw_data.columns))
            st.session_state.raw_data = st.session_state.raw_data.drop(add_selectbox,axis=1)

            with col1.expander("입력 데이터 확인"):
                    st.caption(f"레코드 수: {str(len(st.session_state.raw_data))}\
                        \n속성 수: {str(len(st.session_state.raw_data.columns))}\
                        \n속성 조합 수 {str(len(get_all_combinations(st.session_state.raw_data, None))-1)}")
                    st.dataframe(st.session_state.raw_data[:1000])


        syn_data_file = col2.file_uploader("Upload Synthetic Data")
        if syn_data_file is not None:
            st.session_state.syn_data  = load_data_syn(syn_data_file)
            add_selectbox = col2.multiselect(
                "제거할 속성을 선택해주세요",
                list(st.session_state.syn_data.columns))
            st.session_state.syn_data = st.session_state.syn_data.drop(add_selectbox,axis=1)

            with col2.expander("입력 데이터 확인"):
                    st.caption(f"레코드 수: {str(len(st.session_state.syn_data))}\
                        \n속성 수: {str(len(st.session_state.syn_data.columns))}\
                        \n속성 조합 수 {str(len(get_all_combinations(st.session_state.syn_data, None))-1)}")
                    st.dataframe(st.session_state.syn_data[:1000])


#cache functions
@st.cache
def load_data_raw(file):
    df = pd.read_csv(file, encoding='utf-8')
    return df 

@st.cache
def load_data_syn(file):
    df = pd.read_csv(file, encoding='utf-8')
    return df 