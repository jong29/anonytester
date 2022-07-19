#modules
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from io import BytesIO

#functions
from funcs.risk_syn import compute_risk
from funcs.utility import convert_df2csv
from funcs.synthetic_reidentified import syn_reidentified_datas

class syn_risk:
    def __init__(self):
        if ("syn_data" in st.session_state) and ("raw_data" in st.session_state):
            if "syn_single_attr" not in st.session_state:
                with st.spinner("데이터 로딩중..."):
                    st.session_state.syn_single_attr, st.session_state.syn_one_attr, st.session_state.syn_record, st.session_state.syn_table \
                        = compute_risk(st.session_state.syn_data.copy())

            tab1, tab2, tab3, tab4, tab5 = st.tabs(["재현 재식별도", "테이블 재식별 위험도", "속성 재식별 위험도", "속성값 재식별 위험도", "레코드 재식별 위험도"])

            with tab1:
                self.syn_reid()
            with tab2:
                self.syn_table()
            with tab3:
                self.syn_attr()
            with tab4:
                self.syn_attr_val()
            with tab5:
                self.syn_record()
        else:
            st.markdown("##  \n##  \n## 원본데이터 또는 재현데이터가 업로드 되지 않았습니다")
                

            

    def syn_reid(self):
        st.subheader("재현데이터 재식별도")
        start_cont = st.form("reid_calc")
        col0, col1, col2, col3, col4 = start_cont.columns([0.3, 5, 1, 20, 1])
        dims = col3.slider('재식별도 계산 Dimension을 선택',
                            1, len(st.session_state.raw_data.columns),(1, len(st.session_state.raw_data.columns)))
        record_num = col1.number_input("재식별 확인 레코드 수", min_value=-1, step=1, help="-1을 입력하시면 전체를 확인합니다.")
        if "syn_reid_done" not in st.session_state:
            st.session_state.syn_reid_done = False
        start_button = col1.form_submit_button("재식별도 계산 시작")
        if start_button or st.session_state.syn_reid_done:
            reidentified_res = st.container()
            syn_reidentified, dropped_cols = syn_reidentified_datas(st.session_state.raw_data, st.session_state.syn_data, st.session_state.syn_one_attr, K=record_num,start_dim=dims[0],end_dim=dims[1])
            reid_rate = len(syn_reidentified)/len(st.session_state.syn_data)
            reidentified_res.subheader(f"재식별도: {reid_rate:.2f}")
            reidentified_res.subheader(f"재식별된 레코드 수: {len(syn_reidentified)}")
            reidentified_res.download_button(
                    label="재식별된 데이터 csv로 저장",
                    data = convert_df2csv(syn_reidentified),
                    file_name=st.session_state.syn_file_name[:-4] + '_재식별데이터_' + str(dims[0]) + '_' + str(dims[1]) + '.csv',
                    mime='text/csv',
                )
            reidentified_res.write(syn_reidentified[:1000])
            if dropped_cols is not None:
                drop_str = "모두 같은 값을 가져 drop된 속성: "
                for i in range(len(dropped_cols)):
                    if i != 0:
                        drop_str += ", "
                    drop_str += str(dropped_cols[i])
                st.markdown("##### " + drop_str)
            st.session_state.syn_reid_done = True

    def syn_table(self):
        st.subheader('테이블 재식별 위험도')
        st.download_button(
            label="테이블 재식별 위험도 csv로 저장",
            data = convert_df2csv(st.session_state.syn_table),
            file_name=st.session_state.syn_file_name[:-4] + '_테이블 재식별 위험도.csv',
            mime='text/csv',
        )
        col1, col2 = st.columns(2)
        col1.dataframe(st.session_state.syn_table.round(decimals = 4))
        fig, ax = plt.subplots(figsize=(4,4))
        means = st.session_state.syn_table.iloc[0].iat[0]
        mins = st.session_state.syn_table.iloc[0].iat[3]
        maxes = st.session_state.syn_table.iloc[0].iat[2]
        std = st.session_state.syn_table.iloc[0].iat[1]

        ax.errorbar('Table Reidentification Risk', means, yerr=std, fmt='8r', markersize=10, ecolor='tab:blue', lw=10)
        ax.errorbar('Table Reidentification Risk', means, yerr=[[means-mins],[maxes-means]],
                    fmt='_r', ecolor='tab:orange', lw=3, capsize=3)
        buf = BytesIO()
        fig.savefig(buf, format="png")
        show_table_risk = st.checkbox("그래프 보기", key="syn_table_graph")
        if show_table_risk:
            col2.image(buf)
        

    def syn_attr(self):
        st.subheader('속성 재식별 위험도')
        st.download_button(
            label="속성 재식별 위험도 csv로 저장",
            data = convert_df2csv(st.session_state.syn_one_attr),
            file_name=st.session_state.syn_file_name[:-4] + '_속성 재식별 위험도.csv',
            mime='text/csv',
        )
        st.dataframe(st.session_state.syn_one_attr.round(decimals = 4))
        fig, ax = plt.subplots(figsize=(12,4))
        means = st.session_state.syn_one_attr['mean']
        mins = st.session_state.syn_one_attr['min']
        maxes = st.session_state.syn_one_attr['max']
        std = st.session_state.syn_one_attr['std']
        errors = pd.concat([means-mins,maxes-means], axis=1)
        ax.errorbar(st.session_state.syn_one_attr.index, means, yerr=std, fmt='8r', markersize=10, ecolor='tab:blue', lw=10)
        ax.errorbar(st.session_state.syn_one_attr.index, means, yerr=errors.T,
                    fmt='_r', ecolor='tab:orange', lw=3, capsize=3)
        buf = BytesIO()
        fig.savefig(buf, format="png")
        show_attr_risk = st.checkbox("그래프 보기", key="syn_attr_graph")
        if show_attr_risk:
            st.image(buf)


    def syn_attr_val(self):
        st.subheader('속성값 재식별 위험도')
        st.download_button(
            label="속성 값 재식별 위험도 csv로 저장",
            data = convert_df2csv(st.session_state.syn_single_attr),
            file_name=st.session_state.syn_file_name[:-4] + '_속성 값 재식별 위험도.csv',
            mime='text/csv',
        )
        st.session_state.syn_single_attr = st.session_state.syn_single_attr.round(4).head(200)
        st.dataframe(st.session_state.syn_single_attr.astype(str))

        
    def syn_record(self):
        st.subheader('레코드 재식별 위험도')
        st.download_button(
            label="레코드 재식별 위험도 csv로 저장",
            data = convert_df2csv(st.session_state.syn_record),
            file_name=st.session_state.syn_file_name[:-4] + '_레코드 재식별 위험도.csv',
            mime='text/csv',
        )
        st.dataframe(st.session_state.syn_record.round(decimals = 4).head(200))