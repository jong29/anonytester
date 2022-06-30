import streamlit as st
from classes.sidebar import SideBar

app_name = "Anony Tester"

class main_UI:
    def __init__(self):
        st.set_page_config(
            page_title = "Anony Tester: Home Page"
        )
        st.write("# Welcome to Anonymity Tester!")
        st.markdown(
            """
            Anony Tester는 재현데이터의 안정성 및 유용성 지표를 평가합니다.\n\n\n
            ... (Additional information)
            """
        )
        side_bar = SideBar()
        
if __name__ == '__main__':
    main_UI()





