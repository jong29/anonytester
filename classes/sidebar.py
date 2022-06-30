import streamlit as st


class SideBar:
    def __init__(self):
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

    