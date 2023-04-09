import streamlit as st
from classes.sidebar import SideBar
import os

class main_UI:
    def __init__(self):
        st.set_page_config(
            page_title = "Anony Tester",
            layout = "wide"
        )
        path = os.path.join(os.getcwd(), 'logo', 'logo2.png')   
        print(path)
        st.image(path, width=500)
        SideBar()
        
if __name__ == '__main__':
    main_UI()

