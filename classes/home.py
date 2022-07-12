#modules
from multiprocessing.sharedctypes import Value
import streamlit as st
import pandas as pd

#functions
from funcs.raw_reidentified import get_all_combinations
from funcs.preprocessing import preprocessing_low, preprocessing_high, preprocessing_raw

class home:
    def __init__(self):
        st.write("# Welcome to Anonymity Tester!")
        st.markdown(
            """
            Anony Tester는 재현데이터의 안정성 및 유용성 지표를 평가합니다.
            """
        )
        col1, col2 = st.columns(2)

        #raw data uploader
        raw_data_file = col1.file_uploader("원본데이터 업로드")
        
        if (raw_data_file is not None) and ("raw_data" not in st.session_state):
            st.session_state.raw_file_name = str(raw_data_file.name)
            try:
                st.session_state.raw_data  = load_data_raw(raw_data_file)
            except ValueError as er:
                st.error(f"ValueError {er}  \n업로드된 파일의 포맷이 잘못되었습니다.  \n원본데이터인지 확인해주세요.")

        if "raw_data" in st.session_state:
            if "drop_raw_disp" not in st.session_state:
                st.session_state.drop_raw_disp = list()
            form_selec_raw = col1.form("drop select raw", clear_on_submit = True)
            add_drop_raw = form_selec_raw.multiselect(
                "제거할 속성을 선택해주세요",
                st.session_state.raw_data.columns)
            submitted_raw = form_selec_raw.form_submit_button("Submit")
            if submitted_raw:
                drop_raw = add_drop_raw
                st.session_state.drop_raw_disp += add_drop_raw
                st.session_state.raw_data = st.session_state.raw_data.drop(drop_raw,axis=1)
    
            with col1.expander("입력 데이터 확인"):
                st.session_state.raw_comb_num = len(get_all_combinations(st.session_state.raw_data))
                st.markdown(f"### {st.session_state.raw_file_name}")
                st.write(f"제거된 속성: {st.session_state.drop_raw_disp}")
                st.caption(f"레코드 수: {len(st.session_state.raw_data)}\
                    \n속성 수: {len(st.session_state.raw_data.columns)}\
                    \n속성 조합 수 {st.session_state.raw_comb_num}")
                st.dataframe(st.session_state.raw_data[:1000])

        #synthetic data uploader
        syn_data_file = col2.file_uploader("재현데이터 업로드")

        if (syn_data_file is not None) and ("syn_data" not in st.session_state):
            lev_select = col2.form("syn_lev")
            st.session_state.syn_data_lev = lev_select.radio("재현데이터 수준선택", ("고수준", "저수준"), horizontal=True)
            lev_selected = lev_select.form_submit_button("선택 완료")

            if lev_selected:
                st.session_state.syn_file_name = str(syn_data_file.name)
                try:
                    if st.session_state.syn_data_lev == "고수준":
                        st.session_state.syn_data  = load_data_syn_high(syn_data_file)
                    elif st.session_state.syn_data_lev == "저수준":
                        with st.spinner("저수준 재현데이터 전처리중..."):
                            st.session_state.syn_data  = load_data_syn_low(syn_data_file)
                except KeyError as er:
                    st.error(f"KeyError: {er}  \n업로드된 파일의 포맷이 잘못되었습니다.  \n재현데이터인지 확인해주세요.")

        if "syn_data" in st.session_state:
            if "drop_syn_disp" not in st.session_state:
                st.session_state.drop_syn_disp = list()
            form_selec_syn = col2.form("drop select syn", clear_on_submit = True)
            add_drop_syn = form_selec_syn.multiselect(
                "제거할 속성을 선택해주세요",
                st.session_state.syn_data.columns)
            submitted_syn = form_selec_syn.form_submit_button("Submit")
            if submitted_syn:
                drop_syn = add_drop_syn
                st.session_state.drop_syn_disp += add_drop_syn
                st.session_state.syn_data = st.session_state.syn_data.drop(drop_syn,axis=1)
    
            with col2.expander("입력 데이터 확인"):
                st.session_state.syn_comb_num = len(get_all_combinations(st.session_state.syn_data))
                st.markdown(f"### {st.session_state.syn_file_name}")
                st.write(f"제거된 속성: {st.session_state.drop_syn_disp}")
                st.caption(f"레코드 수: {len(st.session_state.syn_data)}\
                    \n속성 수: {len(st.session_state.syn_data.columns)}\
                    \n속성 조합 수 {st.session_state.syn_comb_num}")
                st.dataframe(st.session_state.syn_data[:1000])


#cache functions
@st.cache(show_spinner=False)
def load_data_raw(file):
    df = pd.read_csv(file, encoding='utf-8')
    df = preprocessing_raw(df)
    return df

@st.cache(show_spinner=False)
def load_data_syn_high(file):
    df = pd.read_csv(file, encoding='utf-8')
    df = preprocessing_high(df)
    return df 

@st.cache(show_spinner = False)
def load_data_syn_low(file):
    df = pd.read_csv(file, encoding='utf-8')
    df = preprocessing_low(df)
    return df 

def to_str(drop_list):
    return ", ".join(drop_list)
