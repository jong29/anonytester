#modules
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from io import BytesIO
import time

#functions
from funcs.risk import compute_risk
from funcs.utility import convert_df2csv
from funcs.raw_reidentified import raw_reidentified_datas
from funcs.preprocessing import preprocessing_raw

class raw_data:
    def __init__(self):
        st.markdown("# Raw Data Analysis")
        if st.session_state.raw_data is not None:
            st.subheader("원본데이터 재식별도")
            with st.expander("재식별도 계산"):
                start_cont = st.container()
                start_button = start_cont.button("재식별도 계산 시작")
                if start_button:
                    reidentified_res = st.container()
                    prep_raw_data = preprocessing_raw(st.session_state.raw_data.copy())
                    begin = time.time()
                    raw_reidentified = raw_reidentified_datas(prep_raw_data, K=-1,start_dim=1,end_dim=-1)
                    reidentified_res.write(f"소요시간: {(time.time()-begin):.2f}초")
                    reidentified_res.write(raw_reidentified[:1000])
                    reid_rate = len(raw_reidentified)/len(prep_raw_data)
                    reidentified_res.subheader(f"재식별도: {reid_rate:.2f}")
                    reidentified_res.download_button(
                            label="재식별된 데이터 csv로 저장",
                            data = convert_df2csv(raw_reidentified),
                            file_name='재식별된 데이터.csv',
                            mime='text/csv',
                        )

            st.subheader("원본데이터 재식별 위험도")
            st.session_state.raw_single_attr, st.session_state.raw_one_attr, st.session_state.raw_record, st.session_state.raw_table \
                    = compute_risk(st.session_state.raw_data)

            with st.expander("테이블 재식별 위험도"):
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
                

            with st.expander("레코드 재식별 위험도"):
                st.download_button(
                    label="레코드 재식별 위험도 csv로 저장",
                    data = convert_df2csv(st.session_state.raw_record),
                    file_name='레코드 재식별 위험도.csv',
                    mime='text/csv',
                )
                st.dataframe(st.session_state.raw_record.round(decimals = 4))
                

            with st.expander('속성 재식별 위험도'):
                st.download_button(
                    label="속성 재식별 위험도 csv로 저장",
                    data = convert_df2csv(st.session_state.raw_one_attr),
                    file_name='속성 재식별 위험도.csv',
                    mime='text/csv',
                )
                st.subheader('속성 재식별 위험도')
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
                

            with st.expander('속성 값 재식별 위험도'):
                st.download_button(
                    label="속성 값 재식별 위험도 csv로 저장",
                    data = convert_df2csv(st.session_state.raw_single_attr),
                    file_name='속성 값 재식별 위험도.csv',
                    mime='text/csv',
                )
                st.session_state.raw_single_attr = st.session_state.raw_single_attr.round(4)
                st.dataframe(st.session_state.raw_single_attr.astype(str))
                