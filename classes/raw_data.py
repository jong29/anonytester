#modules
import streamlit as st
import pandas as pd
import time

#functions
from funcs.raw_reidentified import get_all_combinations

class raw_data:
    def __init__(self):
        st.markdown("# Raw Data Analysis")
        col1, col2 = st.columns(2)

        raw_data_file = col1.file_uploader("Upload Raw Data")
        if raw_data_file is not None:
            st.session_state.raw_data  = pd.read_csv(raw_data_file)
            add_selectbox = col2.multiselect(
                "제거할 속성을 선택해주세요",
                list(st.session_state.raw_data.columns))
            st.session_state.raw_data = st.session_state.raw_data.drop(add_selectbox,axis=1)

            with st.expander("입력 데이터 확인"):
                    st.caption(f"레코드 수: {str(len(st.session_state.raw_data))}\
                        \n속성 수: {str(len(st.session_state.raw_data.columns))}\
                        \n속성 조합 수 {str(len(get_all_combinations(st.session_state.raw_data, None))-1)}")
                    st.dataframe(st.session_state.raw_data[:1000])

            with st.expander("원본 재식별 위험도"):
                #속성 값 재식별 위험도
                risk_title = st.container()
                risk_container = st.container()
                risk_expander_col1, risk_expander_col2 = risk_container.columns(2)
                risk_kinds = risk_title.radio(
                        "원본데이터 재식별 위험도",
                        ('원본데이터 테이블 재식별 위험도', '원본데이터 레코드 재식별 위험도', '원본데이터 속성 재식별 위험도','원본데이터 속성 값 재식별 위험도'))
                if((raw_data_file is not None)):
                    st.session_state.raw_single_attr_value_risk = single_attr_value_risk(st.session_state.raw_data.copy())
                    st.session_state.raw_one_attr_risk_table = one_attr_risk_table(st.session_state.raw_single_attr_value_risk.copy())
                    st.session_state.raw_record_risk = record_risk(st.session_state.raw_data.copy())
                    st.session_state.raw_table_risk = table_risk(st.session_state.raw_record_risk)
                    if(risk_kinds == '원본데이터 테이블 재식별 위험도'):
                        risk_title.subheader('원본데이터 테이블 재식별 위험도')
                        risk_expander_col2.bar_chart(st.session_state.raw_table_risk)
                        risk_expander_col1.dataframe(st.session_state.raw_table_risk.round(decimals = 4))
                        risk_expander_col1.download_button(
                            label="테이블 재식별 위험도 csv로 저장",
                            data = convert_df(st.session_state.raw_table_risk),
                            file_name='테이블 재식별 위험도.csv',
                            mime='text/csv',
                        )
                    elif(risk_kinds == '원본데이터 레코드 재식별 위험도'):
                        risk_title.subheader('원본데이터 레코드 재식별 위험도')
                        risk_expander_col1.dataframe(st.session_state.raw_record_risk.round(decimals = 4))
                        risk_expander_col1.download_button(
                            label="레코드 재식별 위험도 csv로 저장",
                            data = convert_df(st.session_state.raw_record_risk),
                            file_name='레코드 재식별 위험도.csv',
                            mime='text/csv',
                        )
                    elif(risk_kinds == '원본데이터 속성 재식별 위험도'):
                        risk_title.subheader('원본데이터 속성 재식별 위험도')
                        risk_expander_col2.bar_chart(st.session_state.raw_one_attr_risk_table.round(decimals = 4))
                        risk_expander_col1.dataframe(st.session_state.raw_one_attr_risk_table.round(decimals = 4))
                        risk_expander_col1.download_button(
                            label="속성 재식별 위험도 csv로 저장",
                            data = convert_df(st.session_state.raw_one_attr_risk_table),
                            file_name='속성 재식별 위험도.csv',
                            mime='text/csv',
                        )
                    elif(risk_kinds == '원본데이터 속성 값 재식별 위험도'):
                        risk_title.subheader('원본데이터 속성값 재식별 위험도')
                        risk_expander_col1.dataframe(st.session_state.raw_single_attr_value_risk)
                        risk_expander_col1.download_button(
                            label="속성 값 재식별 위험도 csv로 저장",
                            data = convert_df(st.session_state.raw_single_attr_value_risk),
                            file_name='속성 값 재식별 위험도.csv',
                            mime='text/csv',
                        )
