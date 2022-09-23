#modules
from itertools import count
import os
import streamlit as st
import pandas as pd
from pathlib import Path
import json
import sys
import copy

#functions
from funcs.risk_syn import compute_risk
from funcs.synthetic_reidentified import syn_reidentified_datas
from funcs.similarity import similarity
import funcs.utility as util
import funcs.preprocessing as prep
import funcs.horiz_util as horiz

import timeit
class horiz_part:
    def __init__(self):

        # 분할처리할 데이터 업로드
        st.subheader("재현데이터 재식별도 수평 분할 처리")
        col1, col2 = st.columns(2)
        col1.markdown("#### 원본데이터")
        split_raw_file = col1.file_uploader("원본데이터 업로드", type="csv", key="raw_chunk_file")

        col2.markdown("#### 재현데이터")
        split_syn_file = col2.file_uploader("재현데이터 업로드", type="csv", key="syn_chunk_file")


        

        # 분할처리 위한 기타 파라미터 입력
        if (split_raw_file is not None) and (split_syn_file is not None):
            # 원본 속성 제거
            raw_cols = horiz.get_raw_cols(copy.deepcopy(split_raw_file))
            syn_cols = horiz.get_syn_cols(copy.deepcopy(split_syn_file))
            if "raw_chunk_drop" not in st.session_state:
                st.session_state.raw_chunk_drop = list()
            with col1.expander("원본데이터에서 제거할 속성을 선택하세요"):
                with st.form("drop select raw", clear_on_submit = True):
                    drop_raw_dict = dict()
                    drop_raw = list()
                    for attr in raw_cols: #여기에 preprocess 된 칼럼 넣기
                        drop_raw_dict[attr] = st.checkbox(attr, key = attr + '_raw')
                    submitted_raw = st.form_submit_button("선택 완료")
            if submitted_raw:
                for attr in raw_cols: #여기데도 칼럼
                    if drop_raw_dict[attr]:
                        drop_raw.append(attr)
                st.session_state.raw_chunk_drop += drop_raw
                st.experimental_rerun()
            col1.write(f"제거될 원본 속성: {st.session_state.raw_chunk_drop}")

            # 재현 속성 제거
            if "syn_chunk_drop" not in st.session_state:
                st.session_state.syn_chunk_drop = list()
            with col2.expander("재현데이터에서 제거할 속성을 선택하세요"):
                with st.form("drop select syn", clear_on_submit = True):
                    drop_syn_dict = dict()
                    drop_syn = list()
                    for attr in syn_cols: # 속성
                        drop_syn_dict[attr] = st.checkbox(attr, key = attr + '_syn')
                    submitted_syn = st.form_submit_button("선택 완료")
            if submitted_syn:
                for attr in syn_cols: #속성
                    if drop_syn_dict[attr]:
                        drop_syn.append(attr)
                st.session_state.syn_chunk_drop += drop_syn
                st.experimental_rerun()
            col2.write(f"제거될 재현 속성: {st.session_state.syn_chunk_drop}")
            
            # 반복 정보 취합
            with st.form("number of iterations"):
                col3, col4, col5, col6 = st.columns([3,1,3,1])
                st.session_state.div_num = col3.number_input("한번에 처리할 레코드 수", min_value=1 , value=1000, step=100, help="처리할 레코드 수는 재현데이터 기준입니다.")
                st.session_state.checked_rows = col3.number_input("검사 완료한 재현데이터 레코드 수 입력", min_value=0, step=1)
                if "chunk_no" in st.session_state:
                    st.session_state.repeat_num = col5.number_input("반복 실행 횟수", min_value=1, max_value=st.session_state.chunk_no, step=1)
                chunk_submit = col3.form_submit_button("입력")
                st.caption("숫자 변경하면 입력 버튼 눌러주세요")

                if "chunk_no" in st.session_state:
                    st.write(f"한번에 {st.session_state.div_num}의 레코드를 처리하면 {st.session_state.chunk_no}회 반복해야 됩니다.")
                    st.write(f'검사완료 레코드 수: {st.session_state.checked_rows} | 반복횟수: {st.session_state.repeat_num}')

                if chunk_submit:
                    # 전체 반복 횟수
                    st.session_state.chunk_no = util.count_iterations(copy.deepcopy(split_syn_file), st.session_state.div_num)
                    # 청크로 읽은 재현데이터
                    st.session_state.syn_chunk = pd.read_csv(copy.deepcopy(split_syn_file), encoding='utf-8',skiprows=range(1,st.session_state.checked_rows+1), chunksize=st.session_state.div_num)
                    # 재현데이터 속성 읽기
                    st.session_state.chunk_col_num = pd.read_csv(copy.deepcopy(split_raw_file), encoding='utf-8', index_col=0, nrows=0).reset_index().columns.tolist()
                    # should run a garabge collection here as well
                    # if "chunk_no" in st.session_state:
                        
                    st.experimental_rerun() # 스크립트 재실행 하여야 "반복 실행 횟수"의 else 부분 작동
                

                # 재식별 데이터 저장 디렉토리 강제 생성
                default_dir_path = str(Path.home()) + "/Desktop/Anonytest/"
                self.synfile_dir_path = default_dir_path + str(split_syn_file.name)[:-4]
                self.synfilename = str(split_syn_file.name)[:-4]
                self.create_dirs(default_dir_path, self.synfile_dir_path)
                # input_preview = st.empty()


        if "repeat_num" in st.session_state:
            tab1, tab2 = st.tabs(["재식별도", "진행정보"])
            with tab1:
                self.syn_reid(split_raw_file)
            with tab2:
                self.progress_info()

    def syn_reid(self, raw_file):
        if "syn_chunk" in st.session_state:
            with st.form("reid_calc"):
                col2_0, col2_1, col2_2, col2_3, col2_4 = st.columns([0.3, 5, 1, 20, 1])
                dims = col2_3.slider('재식별도 계산 Dimension을 선택',  
                                    1, len(st.session_state.chunk_col_num),(1, len(st.session_state.chunk_col_num)))
                record_num = col2_1.number_input("재식별 확인 레코드 수", min_value=-1, step=1, help="-1을 입력하시면 전체를 확인합니다.")

                start_button = col2_3.form_submit_button("재식별도 계산 시작")
            
            
            reidentified_res = st.container()
            if start_button:
                loop_count = 0
                reid_collection = pd.DataFrame(columns=st.session_state.chunk_col_num)
                other_collection = ""
                start_index = st.session_state.checked_rows+1
                end_index = st.session_state.checked_rows+st.session_state.div_num
                
                #chunk 자체를 for loop 돌려야 chunk 별로 읽어짐
                for chunk in st.session_state.syn_chunk:
                    reid_chunk, risk_chunk, sim_chunk, = horiz.process_chunk(chunk, raw_file, dims, record_num)
                    chunk_metadata = (loop_count, start_index, end_index, st.session_state.div_num, len(reid_chunk), risk_chunk.iloc[0,0], sim_chunk.iloc[0,0])
                    reid_collection, other_collection = horiz.collect_chunk(reid_collection, other_collection, reid_chunk, chunk_metadata)
                    loop_count += 1
                    if loop_count == st.session_state.repeat_num:
                        break
                    else:
                        start_index = end_index+1
                        end_index = end_index + st.session_state.div_num

                # 기타 정보 취합 파일 생성
                info_file_path = self.synfile_dir_path + f'/p_info_{st.session_state.checked_rows+1}_{end_index}.txt'
                with open(info_file_path,'w',encoding = 'utf-8') as f:
                    f.write(other_collection)

                # 재식별 데이터 csv파일 자동 생성
                reid_file_path = self.synfile_dir_path + f'/p_{self.synfilename}_{st.session_state.checked_rows+1}_{end_index}.csv'
                if reid_collection.empty:
                    st.info(f"재식별된 레코드가 없습니다!")
                elif not os.path.exists(reid_file_path):
                    with open(reid_file_path, 'w', encoding='utf-8-sig', newline='') as f:
                        reid_collection.to_csv(f)
                        st.info(f"재식별도 파일 다운로드 완료!  \n   {reid_file_path}")

            
    def progress_info(self):
        pass

    def create_dirs(self, default_dir_path, synfile_dir_path):
        # anonytester 기본 디렉토리 생성
        try:
            os.mkdir(default_dir_path)
        except FileExistsError:
            pass
        
        # 해당 재현데이터 디렉토리 생성
        try:
            os.mkdir(synfile_dir_path)
        except FileExistsError:
            pass

    def cols2list(self, file):
        cols = pd.read_csv(file, encoding='utf-8', index_col=0).columns.tolist()
        return cols