#modules
import streamlit as st
import pandas as pd
import funcs.utility as util

#functions
from funcs.raw_reidentified import get_all_combinations

class home:
    def __init__(self):
        # st.write("# 재현데이터 평가도구 ANONY TESTER")
        st.markdown(
            """
            Anony Tester는 재현데이터의 안정성 및 유용성 지표를 평가합니다.
            <br>
            <br>
            """,
            unsafe_allow_html=True
        )
        col1, col2 = st.columns(2)

        #raw data uploader
        col1.markdown("### 원본데이터")
        raw_data_file = col1.file_uploader("원본데이터 업로드", type="csv")

        #first raw data upload
        if (raw_data_file is not None) and ("raw_data" not in st.session_state):
            st.session_state.raw_file_name = str(raw_data_file.name)
            try:
                st.session_state.raw_data  = util.load_data_raw(raw_data_file)
            except ValueError as er:
                st.error(f"ValueError {er}  \n업로드된 파일의 포맷이 잘못되었습니다.  \n원본데이터인지 확인해주세요.")

        #consecutive uploads
        if raw_data_file is not None:
            if raw_data_file.name != st.session_state.raw_file_name:
                st.session_state.raw_file_name = str(raw_data_file.name)
                st.session_state.drop_raw_disp = list()
                try:
                    st.session_state.raw_data  = util.load_data_raw(raw_data_file)
                except ValueError as er:
                    st.error(f"ValueError {er}  \n업로드된 파일의 포맷이 잘못되었습니다.  \n원본데이터인지 확인해주세요.")

        if "raw_data" in st.session_state:
            if "drop_raw_disp" not in st.session_state:
                st.session_state.drop_raw_disp = list()
            with col1.expander("제거할 속성을 선택하세요"):
                with st.form("drop select raw", clear_on_submit = True):
                    drop_raw_dict = dict()
                    drop_raw = list()
                    for attr in st.session_state.raw_data.columns:
                        drop_raw_dict[attr] = st.checkbox(attr, key = attr + '_raw')
                    submitted_raw = st.form_submit_button("선택 완료")
            if submitted_raw:
                for attr in st.session_state.raw_data.columns:
                    if drop_raw_dict[attr]:
                        drop_raw.append(attr)
                st.session_state.drop_raw_disp += drop_raw
                st.session_state.raw_data = st.session_state.raw_data.drop(drop_raw,axis=1)
                st.experimental_rerun()
            with col1.expander("입력 데이터 확인"):
                raw_preview = st.session_state.raw_data[:100]
                st.session_state.raw_comb_num = len(get_all_combinations(st.session_state.raw_data))
                st.markdown(f"### {st.session_state.raw_file_name}")
                st.write(f"제거된 속성: {st.session_state.drop_raw_disp}")
                st.caption(f"레코드 수: {len(st.session_state.raw_data)}\
                    \n속성 수: {len(st.session_state.raw_data.columns)}\
                    \n속성 조합 수 {st.session_state.raw_comb_num}")
                st.dataframe(raw_preview)

        # synthetic data uploader
        col2.markdown("### 재현데이터")
        syn_data_file = col2.file_uploader("재현데이터 업로드", type="csv")
 
        # first synthetic data upload
        if (syn_data_file is not None) and ("syn_data" not in st.session_state):
            st.session_state.syn_file_name = str(syn_data_file.name)
            lev_select = col2.form("syn_lev")
            st.session_state.syn_data_lev = lev_select.radio("재현데이터 수준선택", ("고수준", "저수준"), horizontal=True)
            lev_selected = lev_select.form_submit_button("다음")

            if lev_selected:
                try:
                    with st.spinner("재현데이터 속성별 처리중..."):
                        if st.session_state.syn_data_lev == "고수준":
                            st.session_state.syn_data = util.load_data_syn_high(syn_data_file)
                        elif st.session_state.syn_data_lev == "저수준":
                            st.session_state.syn_data = util.load_data_syn_low(syn_data_file)
                        st.experimental_rerun()
                except KeyError as er:
                    st.error(f"KeyError: {er}  \n업로드된 파일의 포맷이 잘못되었습니다.  \n재현데이터인지 확인해주세요.")

        # consecutive uploads
        if syn_data_file is not None:
            if syn_data_file.name != st.session_state.syn_file_name:
                st.session_state.drop_syn_disp = list()
                lev_select = col2.form("syn_lev")
                st.session_state.syn_data_lev = lev_select.radio("재현데이터 수준선택", ("고수준", "저수준"), horizontal=True)
                lev_selected = lev_select.form_submit_button("다음")

                if lev_selected:
                    st.session_state.syn_file_name = str(syn_data_file.name)
                    try:
                        with st.spinner("재현데이터 속성별 처리중..."):
                            if st.session_state.syn_data_lev == "고수준":
                                st.session_state.syn_data = util.load_data_syn_high(syn_data_file)
                            elif st.session_state.syn_data_lev == "저수준":
                                st.session_state.syn_data = util.load_data_syn_low(syn_data_file)
                            st.experimental_rerun()
                    except KeyError as er:
                        st.error(f"KeyError: {er}  \n업로드된 파일의 포맷이 잘못되었습니다.  \n재현데이터인지 확인해주세요.")

        if "syn_data" in st.session_state:
            if "drop_syn_disp" not in st.session_state:
                st.session_state.drop_syn_disp = list()
            with col2.expander("제거할 속성을 선택하세요"):
                with st.form("drop select syn", clear_on_submit = True):
                    drop_syn_dict = dict()
                    drop_syn = list()
                    for attr in st.session_state.syn_data.columns:
                        drop_syn_dict[attr] = st.checkbox(attr, key = attr + '_syn')
                    submitted_syn = st.form_submit_button("선택 완료")
            if submitted_syn:
                for attr in st.session_state.syn_data.columns:
                    if drop_syn_dict[attr]:
                        drop_syn.append(attr)
                st.session_state.drop_syn_disp += drop_syn
                st.session_state.syn_data = st.session_state.syn_data.drop(drop_syn,axis=1)
                st.experimental_rerun()
    
            with col2.expander("입력 데이터 확인"):
                syn_preview = st.session_state.syn_data[:100]
                st.session_state.syn_comb_num = len(get_all_combinations(st.session_state.syn_data))
                st.markdown(f"### {st.session_state.syn_file_name}")
                st.write(f"제거된 속성: {st.session_state.drop_syn_disp}")
                st.caption(f"레코드 수: {len(st.session_state.syn_data)}\
                    \n속성 수: {len(st.session_state.syn_data.columns)}\
                    \n속성 조합 수 {st.session_state.syn_comb_num}")
                st.dataframe(syn_preview)