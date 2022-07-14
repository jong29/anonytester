import streamlit as st
import pandas as pd
from funcs.utility import *

class comb_reid:
    def __init__(self):
        st.header("재식별 데이터 디멘션 결합")
        files = st.file_uploader('결합할 재식별 데이터 업로드', accept_multiple_files=True, type="csv")

        file_list = list()
        if len(files) >= 2:
            for file in files:
                file_list.append(pd.read_csv(file))
            combined = combine_dims_recur(file_list)
            st.write(combined[0])
            combined_file = convert_df2csv(combined[0])
            st.download_button("결합된 재식별데이터 다운로드", combined_file, "결합재식별데이터.csv")
            st.markdown(f"### 재식별된 레코드: {len(combined[0])}")