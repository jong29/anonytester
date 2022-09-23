# anonytester

## 실행방법  
`streamlit run main.py`

## 디펜던시 설치  
` pip install requirements.txt`  
local URL: http://localhost:8501 으로 접속 가능
### 직접 설치
```
pip install streamlit
pip install streamlit-option-menu
pip install stqdm
pip install joblib
```

### 업로드 데이터 limit 변경 방법
.streamlit > config.toml
[server]
maxuploadsize = {}