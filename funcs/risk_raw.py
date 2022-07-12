import pandas as pd
import streamlit as st

#속성값 재식별 위험도
@st.cache(show_spinner=False,suppress_st_warning=True)
def single_attr_value_risk(dataframe):
    dataframe_cols = list(dataframe.columns)
    one_attr_value_risk_table = pd.DataFrame(columns=['속성','속성 값','counts'])
    for attr in dataframe_cols:
        temp = pd.DataFrame(dataframe[[attr]].value_counts())
        temp = temp.reset_index()
        temp = temp.rename(columns={attr:'속성 값',0:'counts'})
        temp['속성'] = attr
        one_attr_value_risk_table = pd.concat([one_attr_value_risk_table, temp],axis=0)
        
    one_attr_value_risk_table['속성 값 재식별 위험도'] =(1- (one_attr_value_risk_table['counts']-1)/(len(dataframe)-1)).astype("float")
    one_attr_value_risk_table = one_attr_value_risk_table.drop('counts',axis=1)
    one_attr_value_risk_table = one_attr_value_risk_table.sort_values(['속성','속성 값 재식별 위험도'],ascending=False).reset_index(drop=True)
    return one_attr_value_risk_table

@st.cache(show_spinner=False,suppress_st_warning=True)
def one_attr_risk(single_attr_value_risk):
    # single_attr_value_risk['속성 값 재식별 위험도'] = single_attr_value_risk['속성 값 재식별 위험도'].astype(int)
    one_attr_risk_table = single_attr_value_risk.pivot_table(index='속성',\
                                                                values=['속성 값 재식별 위험도'],\
                                                                  aggfunc=['mean','std','max','min'])
    one_attr_risk_table.columns = ['mean','std','max','min']
    one_attr_risk_table = one_attr_risk_table.sort_values('mean',ascending=False)
    return one_attr_risk_table

@st.cache(show_spinner=False,suppress_st_warning=True)
def transform_to_risk(raw_data,col_name):
    temp = pd.DataFrame()
    temp[col_name] = (1-(raw_data[col_name].value_counts()-1)/(len(raw_data)-1))
    temp = temp.to_dict()
    return temp[col_name]

@st.cache(show_spinner=False,suppress_st_warning=True)
def record_risk(risk_data):
    record_risk = pd.DataFrame()
    raw_data_cols = list(risk_data.columns)
    for attr in raw_data_cols:
        temp_dict = transform_to_risk(risk_data, attr)
        risk_data[attr] = risk_data[attr].map(temp_dict)
    record_risk['mean'] = risk_data.mean(axis=1)
    record_risk['std'] = risk_data.std(axis=1)
    record_risk['max'] = risk_data.max(axis=1)
    record_risk['min'] = risk_data.min(axis=1)
    record_risk = record_risk.sort_values('mean',ascending=False).reset_index().rename(columns={"abst_row_num__":"기존 행"})
    return record_risk

@st.cache(show_spinner=False,suppress_st_warning=True)
def table_risk(record_risk):
    table_risk = pd.DataFrame(record_risk['mean'].describe()).T
    table_risk = table_risk.rename(index={"mean":"평균"})
    table_risk = table_risk[['mean','std','max','min']]
    table_risk = table_risk.rename(index={"평균":"테이블 재식별 위험도"})
    return table_risk 

@st.cache(show_spinner=False,suppress_st_warning=True)
def compute_risk(dataframe):
    single_attr = single_attr_value_risk(dataframe)
    one_attr = one_attr_risk(single_attr)
    record = record_risk(dataframe)
    table = table_risk(record)
    return single_attr, one_attr, record, table


