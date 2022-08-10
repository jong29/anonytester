import pandas as pd
import itertools
from memory_profiler import profile
import colored_traceback.auto

@profile
def get_all_combinations(data, start_dim=1,end_dim=-1):
    all_combinations = list()
    if(start_dim == -1):
        start_dim = len(data.columns)
    if(end_dim == -1):
        end_dim = len(data.columns)
    for r in range(start_dim, end_dim+1):
        combinations_object = itertools.combinations(list(data.columns), r)
        combinations_list = list(combinations_object)
        all_combinations += combinations_list
    return list(all_combinations)

@profile
def is_unique(data):
    dropped_cols = []
    for attr in list(data.columns):
        a = data[attr].to_numpy()
        if (a[0] == a).all():
            data = data.drop(attr,axis=1)
            dropped_cols.append(attr)
    return data, dropped_cols

@profile
def find_unique_data(data, comb):
    #특정 속성조합 comb에서 유일한 데이터 반환
    unique = pd.DataFrame(data[list(comb)].drop_duplicates(keep=False)).reset_index()
    return unique

@profile
def raw_reidentified_datas(raw_data, K=-1, start_dim=1, end_dim=-1):
    #=============원본 재식별도=============
    #K가 -1이면 전부 검사 (데이터 길이만큼)
    if(K==-1):
        K=len(raw_data)
    
    #모두 같은 값을 가지는 속성 제거
    data,dropped_cols  = is_unique(raw_data)

    # Distinct한 속성값이 많은 속성 순으로 정렬
    Priority = raw_data.nunique().sort_values(ascending=False).index
    data =  data.reindex(columns = Priority)
    #속성 조합 반환
    combs = get_all_combinations(data, start_dim, end_dim)

    reidentified_evidence = pd.DataFrame()
    for comb in combs:
        #특정 속성 조합에서 유일한 데이터 반환
        raw_unique = find_unique_data(data, comb)
        if(len(raw_unique)!=0):
            reidentified_evidence = pd.concat([reidentified_evidence,raw_unique],axis=0)
            reidentified_evidence = reidentified_evidence.drop_duplicates(subset ="abst_row_num__",keep="first")
        if(len(reidentified_evidence) >= K):
            break
    if not reidentified_evidence.empty:
        reidentified_evidence = reidentified_evidence.sort_values("abst_row_num__").reset_index(drop=True)
    return reidentified_evidence, dropped_cols

@profile
def preprocessing_raw(raw_data):
    raw_data = raw_data.reset_index().rename(columns={'index':'abst_row_num__'})
    raw_data['abst_row_num__'] = raw_data['abst_row_num__'] + 1
    raw_data = raw_data.set_index("abst_row_num__")
    raw_data.columns = raw_data.columns.str.lower()
    return raw_data

def main():
    raw_data = pd.read_csv(r"C:\Users\dblab\Documents\jong\data\1.0.3 data\z_ptdrctor_wrtng.csv", encoding="utf-8")
    raw_data.drop(['USR_NO'], axis=1)
    raw_data=preprocessing_raw(raw_data)
    raw_reidentified_datas(raw_data)


if __name__ =="__main__":
    main()