# -*- coding: utf8 -*-
import streamlit as st
import pandas as pd
import numpy as np

if 'df' not in st.session_state:
    st.session_state.df = pd.DataFrame(
        {
            "투자자명" : ["박주주","벤쳐소프트","구글벤쳐스"],
            "투자 주식 수" : ["10","100","1000"],
            "비율" : ["10","100","1000"],
        }
    )

if 'df_stat' not in st.session_state:
    st.session_state.df_stat = pd.DataFrame(
        {
            "A" : ["총 주식","총 주주", "회사 가치", "1주당 가격"],
            "B" : [0,0,0,0],
        }
    )

if 'company_value' not in st.session_state:
    st.session_state.company_value = 10000000


st.title("투자 계산 프로그램")

# 데이터 업로드 
uploaded_file = st.file_uploader("이전에 저장해 둔 것 업로드", type=['csv'])
if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    st.session_state.df = df # uploaded_file을 읽은 후에 st.session_state.df에 저장


col1, col2 = st.columns(2)
col1_c = col1.container()
# 회사 가치 입력
companyValue = col1_c.text_input("여기에 회사 가치 입력")
if col1_c.button("회사가치 입력"):
    if companyValue == "": # 입력칸 비어있는지 확인 
        st.error("회사 가치를 입력해 주세요.")
    elif not companyValue.isdigit():
        st.error("회사 가치는 숫자만 입력해 주세요.")
    else: 
        st.session_state.company_value = int(companyValue)


# 투자자 추가 
col2_c = col2.container()
userName = col2_c.text_input("여기에 투자자 이름 입력")
stockNum = col2_c.text_input("여기에 투자 주식 수 입력")
if col2_c.button("투자자 추가"):
    if userName == "" or stockNum == "": # 입력칸 비어있는지 확인 
        st.error("투자자 이름과 투자 주식 수를 모두 입력해주세요.")
    elif not stockNum.isdigit(): # 투자 주식 수가 숫자인지 확인
        st.error("투자 주식 수는 숫자만 입력해주세요.") # 에러 메시지 출력
    else:
        #st.write(userName, "Write Test")
        new_row = pd.DataFrame(
            {
                "투자자명" : [userName],
                "투자 주식 수" : [stockNum],
                "비율" : ["50"],
            }
        )
        df = st.session_state.df
        st.session_state.df = pd.concat([df, new_row], ignore_index=True)
        print(st.session_state.df)
        #st.session_state.df = st.session_state.df.append(new_row, ignore_index=True)




# 업데이트 DF
def update_df(df_data):
    st.markdown("**정보 편집기**")
    df = st.data_editor(df_data.drop("비율", axis=1), disabled=("비율",), key="data_editor") # 편집기 출력
    df["비율"] = pd.to_numeric(df["투자 주식 수"]) / pd.to_numeric(df["투자 주식 수"]).sum() # 비율 계산 
    df["비율"] = df["비율"].apply(lambda x: '{:,.2%}'.format(x)) # 소수 -> 퍼센트 변환 
    st.session_state.df = df
    
    st.markdown("**비율 계산**")
    st.write(df)
    
    # 통계 표 보여주기 
    st.markdown("**통계**")
    st.session_state.df_stat.loc[0, "B"] = pd.to_numeric(df["투자 주식 수"]).sum()
    st.session_state.df_stat.loc[1, "B"] = df.shape[0]
    st.session_state.df_stat.loc[2, "B"] = (f"{st.session_state.company_value:,}원")
    zoodang_price = int(st.session_state.company_value) // pd.to_numeric(df["투자 주식 수"]).sum()
    st.session_state.df_stat.loc[3, "B"] = (f"{zoodang_price:,}원")
    st.dataframe(st.session_state.df_stat.set_index(st.session_state.df_stat.columns[0]))
    
    return df


# 표 보여주기
df = update_df(st.session_state.df)



# 표 내용 다운로드 
#csv = df.to_csv(index=False).encode('utf-8')
st.download_button(
    label="투자자 내용 저장하기 (csv file)",
    data=st.session_state.df.to_csv(index=False).encode('utf-8'),
    file_name='df.csv',
    mime='text/csv',
)

