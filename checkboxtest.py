from tabnanny import check
import streamlit as st

attrs = ['i', 'am', 'not', 'afraid', 'to', 'take', 'a', 'step']
drop_dict = dict()
drop_cols = list()

with st.form('myform'):
    for col in attrs:
        drop_dict[col] = st.checkbox(col, key = col + '_raw')
    
    submitted = st.form_submit_button("submit cols")

if submitted:
    for col in attrs:
        if drop_dict[col]:
            drop_cols.append(col)

st.write(drop_cols)