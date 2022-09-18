import pandas as pd
import preprocessing
import risk_syn
import synthetic_reidentified

def process_chunk(chunk):
    chunk = chunk.drop('an_usr_no', axis=1)
    prep_syn= preprocessing.preprocessing_syn(chunk)
    start = prep_syn.index[0]
    end = prep_syn.index[-1]
    print(f"start: {start}")
    print(f"end: {end}")
    
    raw_chunk = pd.read_csv("z_ptdrctor_wrtng_debug.csv", encoding='utf-8', skiprows=range(1,start-1), nrows =end-start)
    raw_chunk = raw_chunk.drop('USR_NO', axis=1)
    prep_raw = preprocessing.preprocessing_raw(raw_chunk)
    
#     print("Raw")
#     print(prep_raw)
    
#     print("Synthetic")
#     print(prep_syn)
    
    
    # 재식별 위험도
    _, _, _, syn_table = risk_syn.compute_risk(prep_syn.copy())
    print("위험도")
    print(syn_table)
    
#     # 유사도
#     _, _, _, table_similarity = similarity.similarity(prep_raw, prep_syn, apply_hierarchy=False)
#     print("유사도")
#     print(table_similarity)
    
#     # 재식별도
    syn_reidentified, _ = synthetic_reidentified.syn_reidentified_datas(\
        prep_raw.copy(), prep_syn.copy(), K=-1, start_dim=1, end_dim=-1)

    print("재식별 레코드")
    print(syn_reidentified)
    