from tabnanny import check
import streamlit as st

cols = ['i', 'am', 'not', 'afraid']
checkboxes = list()

check1 = st.checkbox(cols[0])

st.write(check1)