# -*- coding: utf8 -*-
import streamlit as st
import pandas as pd
import numpy as np
import pickle
import random

st.set_page_config(layout="wide")


# 세션 값 설정 
if 'df_list' not in st.session_state:
    st.session_state.df_list = []

# df 세션값
if 'df' not in st.session_state:
    st.session_state.df = pd.DataFrame(
        {
            "투자자명" : ["대표이사 최재문","벤쳐소프트","구글벤쳐스"],
            "투자 주식 수" : [800,100,100],
            "비율" : [0,0,0],
            "소유 비중" : [0,0,0],
        }
    )
    st.session_state.df_list.append(st.session_state.df)

df_list = st.session_state.df_list
df = st.session_state.df

# df_stat 세션값
if 'df_stat' not in st.session_state:
    st.session_state.df_stat = pd.DataFrame(
        {
            "A" : ["총 주식","총 주주", "회사 가치", "1주당 가격"],
            "B" : [0,0,0,0],
        }
    )

# company_value 세션값 
if 'company_value' not in st.session_state:
    st.session_state.company_value = 100000

# 1주당 가격
if 'zoodang_price' not in st.session_state:
    st.session_state.zoodang_price = 100

# 현재 라운드 수 
if 'round_count' not in st.session_state:
    st.session_state.round_count = 0

# 퍼센트에서 소수로 변환 함수
def f2p(x):
    return float(x.strip('%')) / 100

#####################################################################
st.title("투자 계산 프로그램")


with st.sidebar:
    st.title("1️⃣Precondition 설정")
    st.caption("❓ 투자를 시작하기 전, 회사의 가치와 현재 투자자 등을 설정합니다.")

    # 데이터 업로드 
    uploaded_file = st.file_uploader("🔼 이전에 저장해 둔 정보 업로드 (csv 파일)", type=['csv'])
    if uploaded_file is not None:
        df = pd.read_csv(uploaded_file)
        st.session_state.df_list[0] = df # uploaded_file을 읽은 후에, 그 df를 st.session_state.df_list의 첫 번째에 저장

    # 레이아웃 구성
    col1, col2 = st.columns(2)

    # 회사 가치 입력
    col1_c = col1.container()
    st.session_state.companyValue = col1_c.number_input("여기에 회사 가치 입력", step=1000, value=100000, format='%d')
    if col1_c.button("회사가치 입력"):
        if st.session_state.companyValue == "": # 입력칸 비어있는지 확인 
            st.error("회사 가치를 입력해 주세요.")
        else: 
            st.session_state.company_value = int(st.session_state.companyValue)

    # 투자자 추가 
    col2_c = col2.container()
    userName = col2_c.text_input("여기에 투자자 이름 입력")
    investment = col2_c.number_input("여기에 투자금액 입력", step=1, value=10000)
    stockNum = investment // st.session_state.zoodang_price
    col2_c.write(f'이 금액으로 사게 되는 주식량 = {stockNum}')
    col2_c.write(f'☑ {((investment // st.session_state.zoodang_price)*st.session_state.zoodang_price)}(조정된 투자금액) ÷ {st.session_state.zoodang_price}(주당 가격) = {stockNum}(개)')
    if col2_c.button("투자자 추가"):
        if userName == "" or investment == "": # 입력칸 비어있는지 확인 
            st.error("투자자 이름과 투자금액을 모두 입력해주세요.")
        else:
            new_row = pd.DataFrame(
                {
                    "투자자명" : [userName],
                    "투자 주식 수" : [stockNum],
                    "비율" : [0],
                    "소유 비중" : [investment]
                }
            )
            df = st.session_state.df_list[0]
            st.session_state.df_list[0] = pd.concat([df, new_row], ignore_index=True)
    
    # 정보 편집 표
    st.markdown("**정보 편집기**")
    sliced_df = st.session_state.df_list[0].drop(["비율", "소유 비중"], axis=1)
    df = st.data_editor(sliced_df, key="data_editor") # 편집기 출력
    df["비율"] = pd.to_numeric(df["투자 주식 수"]) / pd.to_numeric(df["투자 주식 수"]).sum() # 비율 계산 
    df["비율"] = df["비율"] # 소수 -> 퍼센트 변환 
    df["소유 비중"] = st.session_state.company_value * df["비율"]
         

    # 코어 테이블 출력 시작
    st.markdown("**비율 계산**")
    # 임시로 퍼센트 변환용 
    df2 = df
    df2["비율"] = df2["비율"].apply(lambda x: '{:,.2%}'.format(x))
    st.dataframe(df2)

     # 통계 표 보여주기 
    st.markdown("**통계**")
    st.session_state.df_stat.loc[0, "B"] = pd.to_numeric(df["투자 주식 수"]).sum()
    st.session_state.df_stat.loc[1, "B"] = df.shape[0]
    st.session_state.df_stat.loc[2, "B"] = (f"{st.session_state.companyValue:,}원")
    zoodang_price = int(st.session_state.companyValue) // pd.to_numeric(df["투자 주식 수"]).sum()
    st.session_state.zoodang_price = zoodang_price
    st.session_state.df_stat.loc[3, "B"] = (f"{zoodang_price:,}원")
    st.dataframe(st.session_state.df_stat.set_index(st.session_state.df_stat.columns[0]))
    #st.session_state.df = new_df
    
    #df_list[0] = df
    
    # 표 내용 다운로드 
    def update_df():
        st.session_state.df_list[0] = df
    
    st.download_button(
        label="투자자 내용 저장하기 (csv file)",
        data=df.to_csv(index=False).encode('utf-8'),
        file_name='df.csv',
        mime='text/csv',
        on_click= update_df
    )

# 메인 페이지 코드 
uploaded_file = st.file_uploader("전체 상태 파일 업로드", type="pkl")
if uploaded_file is not None:
    df_list = pickle.load(uploaded_file)
    st.write(df_list)
    st.session_state.df_list = df_list
    

# 투자자 정보 입력받기 
newPreValue = st.number_input("여기에 프리 밸류 입력", step=1, value=100000)
newInvestorName = st.text_input("여기에 투자자명 입력")
newInvestorAmount = st.number_input("여기에 투자금액 입력", step=1000, value=10000)
# 살 수 있는 주식 양 계산하기 
newStockNum = newInvestorAmount // st.session_state.zoodang_price
st.write(f'이 금액으로 사게 되는 주식량 = {newStockNum}')
st.write(f'☑ {((newInvestorAmount // st.session_state.zoodang_price)*st.session_state.zoodang_price)}(조정된 투자금액) ÷ {st.session_state.zoodang_price}(주당 가격) = {newStockNum}(개)')

st.write("현재 라운드 수 :",len(df_list))
# 라운드 추가 버튼 
if st.button("라운드 추가"):
    if newPreValue == "" or newInvestorName == "" or newInvestorAmount == "": # 입력칸 비어있는지 확인 
        st.error("프리밸류, 투자자 이름과 투자금액을 모두 입력해주세요.")
    else :
        new_df = df
        new_row = pd.DataFrame(
                {
                    "투자자명" : [newInvestorName],
                    "투자 주식 수" : [newStockNum],
                    "비율" : [100],
                    "소유 비중" : [newInvestorAmount]
                }
            )
        new_df = pd.concat([new_df, new_row], ignore_index=True)
        
        df_list[0] = df # 왼쪽 편집기에서 변경한 내용 반영 
        df_list.append(new_df)
        st.session_state.df_list = df_list # DF_list 세션 갱신
        print("@@debug:",len(df_list))
        # 여기서 DF_list의 비율 정보 갱신 필요 
        index_to_last = len(df_list)-1
        df_list[index_to_last]["비율"] = pd.to_numeric(df_list[index_to_last]["투자 주식 수"]) / pd.to_numeric(df_list[index_to_last]["투자 주식 수"]).sum() # 비율 계산 
        df_list[index_to_last]["비율"] = df_list[index_to_last]["비율"] # 소수 -> 퍼센트 변환 
        df_list[index_to_last]["소유 비중"] = st.session_state.company_value * df_list[index_to_last]["비율"]

        

# 결과 출력 
cols = st.columns(len(df_list))
for i, df in enumerate(df_list):
    cols[i].dataframe(df)



st.download_button("현 상태 전체 저장", pickle.dumps(st.session_state.df_list), file_name="Zuzu_state_file.pkl")
