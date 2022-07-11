import streamlit as st
import pandas as pd
from funcs.utility import *

class comb_reid:
    def __init__(self):
        st.header("재식별 데이터 디멘션 결합")
        col1, col2 = st.columns(2)
        reid_file1 = col1.file_uploader("재식별 데이터1 업로드")
        reid_file2 = col2.file_uploader("재식별 데이터2 업로드")
        if reid_file1 is not None and reid_file2 is not None:
            reid1=pd.read_csv(reid_file1)
            reid2=pd.read_csv(reid_file2)

            combined = combine_dims(reid1, reid2)
            combined_file = convert_df2csv(combined)
            st.download_button("결합된 재식별데이터 다운로드", combined_file, "결합재식별데이터.csv")