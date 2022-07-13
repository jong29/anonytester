import streamlit as st
from streamlit_option_menu import option_menu
from classes.raw_data import raw_data
from classes.syn_risk import syn_risk
from classes.home import home
from classes.comb_reid import comb_reid
from classes.syn_use import syn_use

class SideBar:
    def __init__(self):
        with st.sidebar:
            selected = option_menu(
                    menu_title = "페이지 설정",
                    options=["Home", "원본데이터", "재현데이터 안정성", "재현데이터 유용성", "재현데이터 결합"],
                    orientation="vertical"
                )
        if selected == "Home":
            home()
        if selected == "원본데이터":
            raw_data()
        if selected == "재현데이터 안정성":
            syn_risk()
        if selected == "재현데이터 유용성": 
            syn_use()
        if selected == '재현데이터 결합':
            comb_reid()

        with st.sidebar:
            st.sidebar.title("About")
            st.sidebar.info(
                '''
                연세대학교 데이터베이스 연구실
                연락처: 010-1234-5678\n
                이메일: gmail.com\n
                홈페이지: <http://database.yonsei.ac.kr/>
                '''
            )

    