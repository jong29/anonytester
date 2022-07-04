#modules
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from io import BytesIO

#functions
from funcs.raw_reidentified import get_all_combinations
from funcs.risk import compute_risk
from funcs.utility import convert_df2csv

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

            st.subheader("원본 재식별 위험도")
            st.session_state.raw_single_attr, st.session_state.raw_one_attr, st.session_state.raw_record, st.session_state.raw_table \
                    = compute_risk(st.session_state.raw_data)

            with st.expander("원본데이터 테이블 재식별 위험도"):
                #속성 값 재식별 위험도
                st.download_button(
                    label="테이블 재식별 위험도 csv로 저장",
                    data = convert_df2csv(st.session_state.raw_table),
                    file_name='테이블 재식별 위험도.csv',
                    mime='text/csv',
                )
                col1, col2 = st.columns(2)
                col1.dataframe(st.session_state.raw_table.round(decimals = 4))
                fig, ax = plt.subplots(figsize=(4,4))
                means = st.session_state.raw_table.iloc[0].iat[0]
                mins = st.session_state.raw_table.iloc[0].iat[3]
                maxes = st.session_state.raw_table.iloc[0].iat[2]
                std = st.session_state.raw_table.iloc[0].iat[1]

                ax.errorbar('Table Reidentification Risk', means, yerr=std, fmt='8r', markersize=10, ecolor='tab:blue', lw=10)
                ax.errorbar('Table Reidentification Risk', means, yerr=[[means-mins],[maxes-means]],
                            fmt='_r', ecolor='tab:orange', lw=3, capsize=3)
                buf = BytesIO()
                fig.savefig(buf, format="png")
                col2.image(buf)
                

            with st.expander("원본데이터 레코드 재식별 위험도"):
                st.download_button(
                    label="레코드 재식별 위험도 csv로 저장",
                    data = convert_df2csv(st.session_state.raw_record),
                    file_name='레코드 재식별 위험도.csv',
                    mime='text/csv',
                )
                st.dataframe(st.session_state.raw_record.round(decimals = 4))
                

            with st.expander('원본데이터 속성 재식별 위험도'):
                st.download_button(
                    label="속성 재식별 위험도 csv로 저장",
                    data = convert_df2csv(st.session_state.raw_one_attr),
                    file_name='속성 재식별 위험도.csv',
                    mime='text/csv',
                )
                st.subheader('원본데이터 속성 재식별 위험도')
                # st.bar_chart(st.session_state.raw_one_attr.round(decimals = 4))
                st.dataframe(st.session_state.raw_one_attr.round(decimals = 4))
                fig, ax = plt.subplots(figsize=(12,4))
                means = st.session_state.raw_one_attr['mean']
                mins = st.session_state.raw_one_attr['min']
                maxes = st.session_state.raw_one_attr['max']
                std = st.session_state.raw_one_attr['std']
                errors = pd.concat([means-mins,maxes-means], axis=1)
                ax.errorbar(st.session_state.raw_one_attr.index, means, yerr=std, fmt='8r', markersize=10, ecolor='tab:blue', lw=10)
                ax.errorbar(st.session_state.raw_one_attr.index, means, yerr=errors.T,
                            fmt='_r', ecolor='tab:orange', lw=3, capsize=3)
                buf = BytesIO()
                fig.savefig(buf, format="png")
                st.image(buf)
                

            with st.expander('원본데이터 속성 값 재식별 위험도'):
                st.download_button(
                    label="속성 값 재식별 위험도 csv로 저장",
                    data = convert_df2csv(st.session_state.raw_single_attr),
                    file_name='속성 값 재식별 위험도.csv',
                    mime='text/csv',
                )
                st.session_state.raw_single_attr = st.session_state.raw_single_attr.round(4)
                st.dataframe(st.session_state.raw_single_attr.astype(str))
                