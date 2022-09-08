#modules
import os
import streamlit as st
from pathlib import Path
import json

#functions
from funcs.risk_syn import compute_risk
from funcs.utility import convert_df2csv
from funcs.synthetic_reidentified import syn_reidentified_datas

import timeit
class syn_page:
    def __init__(self):
        if ("syn_data" in st.session_state) and ("raw_data" in st.session_state):
            if "syn_single_attr" not in st.session_state:
                # 재현데이터 위험도 계산
                with st.spinner("데이터 로딩중..."):
                    st.session_state.syn_single_attr, st.session_state.syn_one_attr, st.session_state.syn_record, st.session_state.syn_table \
                        = compute_risk(st.session_state.syn_data.copy())
            try:
                if (st.session_state.raw_data.columns == st.session_state.syn_data.columns).all():
                    pass
                else:
                    st.warning("원본데이터와 재현데이터의 속성이 다릅니다.")
            except:
                st.warning("원본데이터와 재현데이터의 속성이 다릅니다.")

            tab1, tab2, tab3, tab4, tab5 = st.tabs(["재현 재식별도", "테이블 재식별 위험도", "속성 재식별 위험도", "속성값 재식별 위험도", "레코드 재식별 위험도"])

            with tab1:
                self.syn_reid()
            with tab2:
                self.syn_table()
            with tab3:
                self.syn_attr()
            with tab4:
                self.syn_attr_val()
            with tab5:
                self.syn_record()
        else:
            st.markdown("##  \n##  \n## 원본데이터 또는 재현데이터가 업로드 되지 않았습니다")
            
    #재현데이터 재식별도 탭
    def syn_reid(self):
        self.reid_info()
        st.subheader("재현데이터 재식별도 계산")
        start_cont = st.form("reid_calc")
        col0, col1, col2, col3, col4 = start_cont.columns([0.3, 5, 1, 20, 1])
        dims = col3.slider('재식별도 계산 Dimension을 선택',
                            1, len(st.session_state.raw_data.columns),(1, len(st.session_state.raw_data.columns)))
        record_num = col1.number_input("재식별 확인 레코드 수", min_value=-1, step=1, help="-1을 입력하시면 전체를 확인합니다.")

        start_button = col1.form_submit_button("재식별도 계산 시작")
        reidentified_res = st.container()

        if start_button:
            start = timeit.default_timer()
            st.session_state.syn_reidentified, st.session_state.dropped_cols_syn = syn_reidentified_datas(\
                st.session_state.raw_data, st.session_state.syn_data, K=record_num,start_dim=dims[0],end_dim=dims[1])
            stop = timeit.default_timer()
            reidentified_res.write(f"계산 시간(초): {stop-start}")
            
            # ------- 재식별도 계산 완료 -------

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
            
    #테이블 재식별 위험도 탭
    def syn_table(self):
        st.subheader('테이블 재식별 위험도')
        st.download_button(
            label="테이블 재식별 위험도 csv로 저장",
            data = convert_df2csv(st.session_state.syn_table),
            file_name=st.session_state.syn_file_name[:-4] + '_테이블 재식별 위험도.csv',
            mime='text/csv',
        )
        col1, col2 = st.columns(2)
        col1.dataframe(st.session_state.syn_table.round(decimals = 4))
        
    #속성 재식별 위험도 탭
    def syn_attr(self):
        st.subheader('속성 재식별 위험도')
        st.download_button(
            label="속성 재식별 위험도 csv로 저장",
            data = convert_df2csv(st.session_state.syn_one_attr),
            file_name=st.session_state.syn_file_name[:-4] + '_속성 재식별 위험도.csv',
            mime='text/csv',
        )
        st.dataframe(st.session_state.syn_one_attr.round(decimals = 4))

    # 속성값 재식별 위험도 탭
    def syn_attr_val(self):
        st.subheader('속성값 재식별 위험도')
        st.download_button(
            label="속성 값 재식별 위험도 csv로 저장",
            data = convert_df2csv(st.session_state.syn_single_attr),
            file_name=st.session_state.syn_file_name[:-4] + '_속성 값 재식별 위험도.csv',
            mime='text/csv',
        )
        st.session_state.syn_single_attr = st.session_state.syn_single_attr.round(4).head(200)
        st.dataframe(st.session_state.syn_single_attr.astype(str))

    # 레코드 재식별 위험도 탭
    def syn_record(self):
        st.subheader('레코드 재식별 위험도')
        st.download_button(
            label="레코드 재식별 위험도 csv로 저장",
            data = convert_df2csv(st.session_state.syn_record),
            file_name=st.session_state.syn_file_name[:-4] + '_레코드 재식별 위험도.csv',
            mime='text/csv',
        )
        st.dataframe(st.session_state.syn_record.round(decimals = 4).head(200))

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

    # 재식별도 계산된 기록(메타데이터) 표시
    def reid_info(self):
        st.subheader('재식별 데이터 검사 기록')
        json_file_path = str(Path.home()) + "/Desktop/Anonytest/" + st.session_state.syn_file_name[:-4] + '/metadata.json'
        if os.path.exists(json_file_path):
            with open(json_file_path, 'r', encoding = 'utf-8') as f:
                meta_dict = json.load(f)
            if meta_dict["dims_remaining"][0] == -1:
                st.success("젠체 디멘션 계산 완료했습니다!")
            else:
                st.warning(f'계산 되지 않은 디멘션: {meta_dict["dims_remaining"][0]} 에서 {meta_dict["dims_remaining"][1]}')

            st.markdown(f"""
                <div>
                    <p style="font-size:18px;"> 전체 디멘션 수: {meta_dict["raw_data_attr_num"]} </p>
                    <p style="font-size:18px;"> 현재까지 재식별된 레코드 수: {meta_dict["reid_record"]} </p>
                    <p style="font-size:18px;"> 현재까지 계산된 재식별도: {meta_dict["reid_rate"]:.3f} </p>
                    <p style="font-size:18px;"> 검사 완료한 재식별 데이터 디멘션: </p>
                </div>
            """, unsafe_allow_html=True)
            for dim in meta_dict["files_to_combine"]:
                st.write(dim)
        else:
            st.markdown('<p style="color: grey; font-size: 22px; font-weight: bold">재식별도 검사 기록이 없습니다</p>', unsafe_allow_html=True)