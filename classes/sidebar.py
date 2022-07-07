import streamlit as st
from streamlit_option_menu import option_menu
from classes.raw_data import raw_data
from classes.syn_data_risk import syn_data_risk
from classes.home import home

class SideBar:
    def __init__(self):
        with st.sidebar:
            selected = option_menu(
                    menu_title = "Navigation",
                    options=["Home", "Raw Data", "Synthetic Data Risk", "Synthetic Data Usefulness"],
                    orientation="vertical"
                )
        if selected == "Home":
            home()
        if selected == "Raw Data":
            raw_data()
        if selected == "Synthetic Data Risk":
            syn_data_risk()
        if selected == "Synthetic Data Usefulness": 
            st.title(f"you selected {selected}")

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

    