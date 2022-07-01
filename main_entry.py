import streamlit as st
from classes.sidebar import SideBar

class main_UI:
    def __init__(self):
        st.set_page_config(
            page_title = "Anony Tester",
            layout = "wide"
        )
        SideBar()
        
if __name__ == '__main__':
    main_UI()

