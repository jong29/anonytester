import streamlit as st
from classes.sidebar import SideBar

class main_UI:
    def __init__(self):
        st.set_page_config(
            page_title = "Anony Tester",
            layout = "wide"
        )   
        st.image(".\logo\로고1_수정.png", width=500)
        SideBar()
        
if __name__ == '__main__':
    main_UI()

