# anonytester

Anonytester는 재현데이터의 안정성을 평가하는 프로그램입니다.  
원본데이터와 재현데이터를 입력하면 재식별도, 유사도, 재식별 위험도 등 지표를 계산해줍니다.

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

```
[server]
maxuploadsize = [용량 입력]
```

### 난독화 방법
```
pip install pyinstaller
pip install pyarmor
pyarmor obfuscate --restrict=0 --recursive --no-cross-protection main_entry.py
```