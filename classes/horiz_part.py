#modules
from itertools import count
import os
import streamlit as st
import pandas as pd
from pathlib import Path
import json

#functions
from funcs.risk_syn import compute_risk
from funcs.synthetic_reidentified import syn_reidentified_datas
import funcs.utility as util
    
import timeit
class horiz_part:
    def __init__(self):
        # 분할처리할 데이터 업로드
        st.subheader("재현데이터 재식별도 수평 분할 처리")
        col1, col2 = st.columns(2)
        col1.markdown("### 원본데이터")
        split_raw_file = col1.file_uploader("원본데이터 업로드", type="csv")

        col2.markdown("### 재현데이터")
        split_syn_file = col2.file_uploader("재현데이터 업로드", type="csv")

        # 분할처리 위한 기타 파라미터 입력
        with st.form("number of iterations"):
            col3, col4 = st.columns([1, 3])
            st.session_state.div_num = col3.number_input("한번에 처리할 레코드 수", min_value=0, step=10, help="처리할 레코드 수는 재현데이터 기준입니다.")
            chunk_submit = st.form_submit_button("입력")

        #first raw data upload

        if chunk_submit:
            if (split_raw_file is not None) and ("raw_data" not in st.session_state):
                # before was df, but now would be iterator
                st.session_state.raw_chunk  = util.load_raw_iter(split_raw_file, st.session_state.div_num)

            # first synthetic data upload
            if (split_syn_file is not None) and ("syn_data" not in st.session_state):
                st.session_state.syn_chunk = util.load_raw_iter(split_syn_file, st.session_state.div_num)
            
            # 원본 csv의 레코드수 세기
            total_lines = util.count_lines(st.session_state.syn_chunk)
            st.write(f"total records {total_lines}")

        if ("split_raw_file" in st.session_state) and ("split_syn_file" in st.session_state):
            # 원본 재현데이터 칼럼 동일한지 확인
            try:
                if (st.session_state.raw_data.columns == st.session_state.syn_data.columns).all():
                    pass
                else:
                    st.warning("원본데이터와 재현데이터의 속성이 다릅니다.")
            except:
                st.warning("원본데이터와 재현데이터의 속성이 다릅니다.")

        tab1, tab2 = st.tabs(["재식별도", "진행정보"])
        with tab1:
            self.syn_reid()
        with tab2:
            self.progress_info()

    def syn_reid(self):
        start_cont = st.form("reid_calc")
        col0, col1, col2, col3, col4 = start_cont.columns([0.3, 5, 1, 20, 1])
        dims = col3.slider('재식별도 계산 Dimension을 선택',
                            1, len(st.session_state.raw_data.columns),(1, len(st.session_state.raw_data.columns)))
        record_num = col1.number_input("재식별 확인 레코드 수", min_value=-1, step=1, help="-1을 입력하시면 전체를 확인합니다.")

        start_button = col1.form_submit_button("재식별도 계산 시작")
        reidentified_res = st.container()

        if start_button:
            start = timeit.default_timer()

            #재식별 위험도
            with st.spinner("데이터 로딩중..."):
                st.session_state.syn_single_attr, st.session_state.syn_one_attr, st.session_state.syn_record, st.session_state.syn_table \
                    = compute_risk(st.session_state.syn_data.copy())

            # 재식별도
            st.session_state.syn_reidentified, st.session_state.dropped_cols_syn = syn_reidentified_datas(\
                st.session_state.raw_data, st.session_state.syn_data, st.session_state.syn_one_attr,\
                K=record_num,start_dim=dims[0],end_dim=dims[1])
            stop = timeit.default_timer()
            reidentified_res.write(f"계산 시간: {stop-start}")
            
            # 재식별 데이터 저장 디렉토리 강제 생성
            default_dir_path = str(Path.home()) + "/Desktop/Anonytest/"
            synfile_dir_path = default_dir_path + st.session_state.syn_file_name[:-4]
            self.create_dirs(default_dir_path, synfile_dir_path)

            # metadata 파일 처리
            # metadata json 형태로 담을 dictionary
            reid_record_num = len(st.session_state.syn_reidentified)
            reid_rate = reid_record_num/len(st.session_state.syn_data)
            meta_dict = {
                "dims_remaining": [],
                "files_to_combine": [],
                "reid_record": None,
                "reid_rate": None,
                "raw_data_attr_num" : None,
                "raw_data_record_num": None,
            }

            json_file_path = synfile_dir_path + '/metadata.json'
            
            # json 메타데이터 업데이트 재식별도 계산 시
            if os.path.exists(json_file_path): # 메타데이터 파일 업데이트
                with open(json_file_path, 'r', encoding = 'utf-8') as f:
                    meta_dict = json.load(f)
                if dims[1] == len(st.session_state.raw_data.columns):
                    meta_dict["dims_remaining"][0] = -1  # 디멘션 전부 확인했을때 -1로 표시
                else:
                    if meta_dict["dims_remaining"][0] != -1:
                        meta_dict["dims_remaining"][0] = dims[1]+1
                if reid_record_num > meta_dict["reid_record"]: meta_dict["reid_record"] = (reid_record_num)
                if reid_rate > meta_dict["reid_rate"]: meta_dict["reid_rate"] = (reid_rate)
                meta_dict["files_to_combine"].append(str(dims[0]) + '_' + str(dims[1]))
                with open(json_file_path,'w',encoding = 'utf-8') as f:
                    f.write(json.dumps(meta_dict, indent=4))
            else: # 메타데이터 파일 생성
                if dims[1] == len(st.session_state.raw_data.columns):
                    meta_dict["dims_remaining"] = [-1, -1]  # 디멘션 전부 확인했을때 -1로 표시
                else:
                    meta_dict["dims_remaining"] = [dims[1]+1, len(st.session_state.raw_data.columns)]
                meta_dict["reid_record"] = reid_record_num
                meta_dict["reid_rate"] = reid_rate
                meta_dict["raw_data_attr_num"] = len(st.session_state.raw_data.columns)
                meta_dict["raw_data_record_num"] = len(st.session_state.raw_data)
                meta_dict["files_to_combine"].append(str(dims[0]) + '_' + str(dims[1]))
                with open(json_file_path,'w',encoding = 'utf-8') as f:
                    f.write(json.dumps(meta_dict, indent=4))
 
            # 재식별 데이터 csv파일 자동 생성
            reid_file_path = synfile_dir_path + '/' + st.session_state.syn_file_name[:-4] + '_재식별데이터_' + str(dims[0]) + '_' + str(dims[1]) + '.csv'
            if st.session_state.syn_reidentified.empty:
                st.info(f"재식별된 레코드가 없습니다!")
            elif not os.path.exists(reid_file_path):
                with open(reid_file_path, 'w', encoding='utf-8-sig', newline='') as f:
                    st.session_state.syn_reidentified.to_csv(f)
                    st.info(f"재식별도 파일 다운로드 완료!  \n   {reid_file_path}")
        
        # 재식별도 관련 정보 표시
        if "syn_reidentified" in st.session_state:
            reid_record_num = len(st.session_state.syn_reidentified)
            reid_rate = reid_record_num/len(st.session_state.syn_data)
            reidentified_res.subheader(f"재식별도: {reid_rate:.2f}")
            reidentified_res.subheader(f"재식별된 레코드 수: {len(st.session_state.syn_reidentified)}")

            if not st.session_state.syn_reidentified.empty:
                with reidentified_res.expander("재식별된 레코드 확인"):
                    st.dataframe(st.session_state.syn_reidentified[:1000])
            
            # column 전체가 같은 값을 가져서 drop되면 표시
            if st.session_state.dropped_cols_syn:
                drop_str = "모두 같은 값을 가져 drop된 속성: "
                for i in range(len(st.session_state.dropped_cols_syn)):
                    if i != 0:
                        drop_str += ", "
                    drop_str += str(st.session_state.dropped_cols_syn[i])
                st.markdown("##### " + drop_str)
            st.session_state.syn_reid_done = True
            
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