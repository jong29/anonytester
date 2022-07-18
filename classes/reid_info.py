import streamlit as st
from os import listdir
from os.path import isfile, join
import json

class reid_info:
    def __init__(self):
        st.session_state.reid_dir = st.text_input("재식별 정보 디렉토리를 입력하세요.")
        st.write("여기에서 파일 검색을 하겠습니다: " + st.session_state.reid_dir)
        if "reid_dir" in st.session_state and st.session_state.reid_dir != "":
            onlyfiles = [f for f in listdir(st.session_state.reid_dir) if isfile(join(st.session_state.reid_dir, f))]
            for file in onlyfiles:
                if file[-4:] == "json":
                    f=open(st.session_state.reid_dir + '/' + file, 'r', encoding='utf-8')
                    data = json.load(f)
                    st.write(data)
                    st.markdown(f"### 검사 완료한 디멘션:  \n{data['dimensions'][0]}에서 {data['dimensions'][1]}")
                    
                    f.close()

def update_json():
    pass