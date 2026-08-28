import streamlit as st
import pandas as pd
import json
import os
import math
import calendar
import datetime as dt_mod
from datetime import datetime
from korean_lunar_calendar import KoreanLunarCalendar
import ephem
from google import genai
import pytz
import streamlit.components.v1 as components
import re

# 🎯 [버전 컨트롤 타워]
APP_VERSION = "Ver 46.7"

# ==============================================================================
# 0. VIP 인셋 프레임 및 초강력 프린트 CSS
# ==============================================================================
st.set_page_config(page_title=f"초연 시공명리 {APP_VERSION}", layout="wide")

st.markdown("""
<style>
    @import url("https://fonts.googleapis.com/css2?family=Noto+Serif+KR:wght@400;600;900&display=swap");
    
    body, .stApp { background-color: #FFF8E1; }
    
    .report-page { width: 210mm; max-width: 100%; margin: 30px auto; background-color: #FFFFFF !important; padding: 15mm 10mm; box-shadow: 0 0 20px rgba(0,0,0,0.15); border-radius: 20px; box-sizing: border-box; }
    .report-page, .report-page * { font-family: 'Noto Serif KR', serif !important; color: #000000; }
    
    .vip-inset-frame { border: 2px solid #1A237E; border-radius: 15px; padding: 20px; background: transparent; box-sizing: border-box; width: 100%; overflow: hidden; word-break: keep-all; -webkit-box-decoration-break: clone; box-decoration-break: clone; }

    /* 🚨 [강제 수술] 표지 타이틀: 고딕체 강제 해제! 웅장한 나눔명조체 + 60px 절대 고정! */
    .cover-page h1, .cover-page .title-gothic { 
        font-family: 'Nanum Myeongjo', serif !important; 
        font-size: 60px !important; /* 여기서 스트림릿 억압 뚫고 60px로 확정! */
        color: #1A237E !important; /* 초연명리 시그니처 짙은 남색 */
        font-weight: 900 !important; 
        line-height: 1.3 !important;
        word-break: keep-all !important;
        border-bottom: none !important;
    }
    
    /* 표지 버전 정보도 명조체로 우아하게 통일 */
    .cover-page .ver-gothic { 
        font-family: 'Nanum Myeongjo', serif !important; 
        color: #555555 !important; 
        font-weight: 900 !important; 
    }

    /* 🌟 본문(에세이) 영역의 h1 (표지 간판에는 영향 안 주도록 :not 예외 처리 쐐기!) */
    .report-page:not(.cover-page) h1 { font-size: 28px !important; margin-bottom: 15px !important; color: #1A237E !important; font-weight: 900 !important; }
    .report-page h2 { font-size: 22px !important; margin-bottom: 15px !important; font-weight: 900 !important; }
    .report-page h3 { font-size: 22px !important; margin-top: 25px !important; margin-bottom: 8px !important; border-bottom: 2px solid #1A237E; padding-bottom: 5px; color: #1A237E !important; font-weight: 900 !important; }
    .report-page h4 { font-size: 18px !important; margin-top: 15px !important; margin-bottom: 8px !important; font-weight: 900 !important; }
    
    /* 🌟 사주 원국표 CSS 유지 (word-break: keep-all 추가로 가독성 극대화) */
    .result-table { width: 100%; border-collapse: collapse; border: 3px solid #3E2723; margin-bottom: 15px; table-layout: fixed; }
    .result-table td { border: 1px solid #444; padding: 1px; text-align: center; vertical-align: middle; font-weight: 900; font-size: 13px; line-height: 1.2; word-break: keep-all; }
    
    .no-border-row td { border-top: none !important; border-bottom: none !important; }
    .no-border-row:last-of-type td { border-bottom: 1px solid #444 !important; }
    
    .header-cell-main { background-color: #E8EAF6 !important; color: #1A237E !important; font-weight: 900 !important; font-size: 15px !important; border: 1px solid #444 !important; }
    
    .top-header-cell { background-color: #1A237E !important; height: 30px !important; }
    .top-header-cell td, .top-header-cell span { color: #FFFFFF !important; font-weight: 900 !important; font-size: 16px !important; }
    
    .color-목 { background-color: #2E7D32 !important; color: white !important; }
    .color-화 { background-color: #C62828 !important; color: white !important; }
    .color-토 { background-color: #F9A825 !important; color: black !important; }
    .color-금 { background-color: #9E9E9E !important; color: white !important; }
    .color-수 { background-color: #212121 !important; color: white !important; }
    
    /* 특수기호(▶, •, ◈) 소제목 및 일반 본문 제어 구역 */
    .content-box-loose { line-height: 1.8; font-size: 15px; color: #111; text-align: justify; word-break: keep-all; font-family: 'Noto Serif KR', 'Nanum Myeongjo', serif !important; padding: 0 !important; }
    .content-box-loose .sub-title { text-indent: 0px !important; margin-top: 25px !important; margin-bottom: 10px !important; font-weight: 900 !important; display: block; color: #111 !important; }
    
    /* 사이드바 및 가동 버튼 강제 제어 */    
    div[data-testid="stSidebar"] div.stButton > button:first-child,
    div.stButton > button[kind="primary"] { background-color: #D50000 !important; color: white !important; border: none !important; height: 45px !important; }
    
    /* 🚨 [수술] 가동 버튼 내부 글씨(p 태그)를 인쇄 버튼과 똑같은 굵은 고딕체로 강제 주입 */
    div[data-testid="stSidebar"] div.stButton > button:first-child p,
    div.stButton > button[kind="primary"] p { font-weight: 900 !important; font-size: 15px !important; font-family: "Malgun Gothic", "Apple SD Gothic Neo", sans-serif !important; color: white !important; margin: 0 !important; }

    div[data-testid="stSidebar"] .navy-btn button { background-color: #1A237E !important; color: white !important; border: none !important; font-weight: 900 !important; height: 45px !important; }    
    @media print { 
        @page { size: A4 portrait; margin: 10mm; }
        .stSidebar, button, iframe, .print-hide, header { display: none !important; }
        body, .stApp { background-color: white !important; }
        
        /* 🚨 [수술 완료] 스트림릿 고유의 쓸데없는 상단 여백 완벽 제거 (빈 페이지 발생 원천 차단) */
        .block-container, div[data-testid="stAppViewBlockContainer"] { padding-top: 0 !important; padding-bottom: 0 !important; margin-top: 0 !important; margin-bottom: 0 !important; }
        div[data-testid="stVerticalBlock"] { gap: 0 !important; }
        .element-container, .stMarkdown { margin-bottom: 0 !important; }
        
        .report-page { box-shadow: none; margin: 0 auto; padding: 0; page-break-after: always; border-radius: 0; width: 100%; max-width: 100%; }
        .report-page:last-of-type { page-break-after: auto; }
        .page-break-before { page-break-before: always; }
        .vip-inset-frame { border: 2px solid #000; border-radius: 20px; padding: 15px; }
    }
</style>
""", unsafe_allow_html=True)

# ==============================================================================
# 0.5 [완전 무결점 하드코딩 DB]
# ==============================================================================
choyeon_db = {
    "wolryeong": {
        "甲子": "천둥번개 우뢰(甲)가 꽁꽁 얼어붙은 검은 연못(子)의 정적을 거세게 깨우는 완연한 한겨울",
        "乙丑": "찬 바람(乙)이 꽁꽁 얼어붙은 버드나무 언덕(丑)을 매섭게 휘감아 도는 가장 추운 겨울",
        "丙寅": "태양(丙)이 넓은 들판(寅)의 찬 기운을 녹이며 환히 비추는, 추위가 남아 있는 이른 봄",
        "丁卯": "영롱한 별빛(丁)이 옥 같이 아름다운 숲(卯)의 어둠을 밝히는 완연한 봄",
        "戊辰": "노을(戊)이 풀이 우거진 늪지(辰) 위로 내려앉아 수분이 차오르는 봄과 여름의 환절기",
        "己巳": "구름(己)이 큰 역(巳) 위로 머무르며 열기를 품기 시작하는 이른 여름",
        "庚午": "달빛(庚)이 횟불 신호대(午)의 정적 속에 고고하게 빛을 쏟아내는 완연한 여름",
        "辛未": "서리(辛)가 화원(未)의 열기를 식히지만 가장 무더운 여름",
        "壬申": "이슬(壬)이 대도시(申)의 마른 풀끝을 적시는 서늘한 이른 가을",
        "癸酉": "봄비(癸)가 사찰의 종(酉)을 적시며 결실을 거두는 완연 가을",
        "甲戌": "우뢰(甲)가 불태운 들판(戌)에 진동하며 결실을 저장하는 가을과 겨울의 환절기",
        "乙亥": "바람(乙)이 쏟아지는 강물(亥) 위를 스치며 추위가 스며드는 이른 겨울",
        "丙子": "태양(丙)이 검은 연못(子)을 비추는 깊어지는 한겨울",
        "丁丑": "별(丁)이 버드나무 언덕(丑)의 시린 어둠을 밝히는 가장 추운 겨울",
        "戊寅": "노을(戊)이 들판(寅)을 온화하게 감싸 안는 이른 봄",
        "己卯": "구름(己)이 아름다운 숲(卯) 위를 감싸는 완연한 봄",
        "庚辰": "달빛(庚)이 우거진 늪지(辰) 위로 쏟아지는 봄과 여름의 환절기",
        "辛巳": "서리(辛)가 큰 역(巳) 위로 내려앉는 이른 여름",
        "壬午": "이슬(壬)이 횃불 신호대(午) 위로 맺히는 완연한 여름",
        "癸未": "봄비(癸)가 화원(未)을 적시는 가장 무더운 여름",
        "甲申": "우뢰(甲)가 대도시(申)를 진동시키는 이른 가을",
        "乙酉": "바람(乙)이 사찰의 종(酉)을 울리는 완연한 가을",
        "丙戌": "태양(丙)이 불태운 들판(戌)을 비추는 가을과 겨울의 환절기",
        "丁亥": "별(丁)이 쏟아지는 강물(亥) 위를 밝히는 이른 겨울",
        "戊子": "노을(戊)이 검은 연못(子)의 정적을 비추는 한겨울",
        "己丑": "구름(己)이 버드나무 언덕(丑)을 덮어주는 가장 추운 겨울",
        "庚寅": "달빛(庚)이 넓은 들판(寅)의 정적을 비추는 이른 봄",
        "辛卯": "서리(辛)가 아름다운 숲(卯)에 내리는 완연한 봄",
        "壬辰": "이슬(壬)이 늪지(辰)를 적시는 봄과 여름의 환절기",
        "癸巳": "봄비(癸)가 큰 역(巳) 위로 내리는 이른 여름",
        "甲午": "우뢰(甲)가 횃불 신호대(午)를 진동시키는 완연한 여름",
        "乙未": "바람(乙)이 화원(未) 위를 스치는 가장 무더운 여름",
        "丙申": "태양(丙)이 대도시(申)를 환히 비추는 이른 가을",
        "丁酉": "별(丁)이 사찰의 종(酉)을 은은히 비추는 완연한 가을",
        "戊戌": "노을(戊)이 불태운 들판(戌)을 덮는 가을과 겨울의 환절기",
        "己亥": "구름(己)이 쏟아지는 강물(亥) 위에 머무는 이른 겨울",
        "庚子": "달빛(庚)이 검은 연못(子)을 비추는 한겨울",
        "辛丑": "서리(辛)가 버드나무 언덕(丑)에 내리는 가장 추운 겨울",
        "壬寅": "이슬(壬)이 들판(寅)을 적시는 이른 봄",
        "癸卯": "봄비(癸)가 아름다운 숲(卯)을 적시는 완연한 봄",
        "甲辰": "우뢰(甲)가 늪지(辰)를 진동시키는 봄과 여름의 환절기",
        "乙巳": "바람(乙)이 큰 역(巳) 위를 스치는 이른 여름",
        "丙午": "태양(丙)이 횟불 신호대(午)를 비추는 완연한 여름",
        "丁未": "영롱한 별빛(丁)이 화원(未)을 비추는 가장 무더운 여름",
        "戊申": "붉은 노을(戊)이 유명한 대도시(申)를 감싸는 이른 가을",
        "己酉": "포근한 구름(己)이 사찰의 종(酉) 위에 머무는 완연한 가을",
        "庚戌": "서늘한 달빛(庚)이 불태우는 근원(戌)을 비추는 가을과 겨울의 환절기",
        "辛亥": "하얀 서리(辛)가 쏟아지는 강물(亥) 위에 내리는 이른 겨울",
        "壬子": "가을이슬(壬)이 검은 연못(子)을 비추는 한겨울",
        "癸丑": "봄비(癸)가 버드나무 언덕(丑)을 적시는 가장 추운 겨울",
        "甲寅": "천둥번개 우뢰(甲)가 넓은 들판(寅)을 진동시키는 이른 봄",
        "乙卯": "바람(乙)이 옥 같이 아름다운 숲(卯)을 스치는 완연한 봄",
        "丙辰": "태양(丙)이 풀이 우거진 늪지(辰)를 비추는 봄과 여름의 환절기",
        "丁巳": "영롱한 별빛(丁)이 큰 역(巳)을 밝히는 이른 여름",
        "戊午": "붉은 노을(戊)이 횟불 신호대(午)를 덮는 완연한 여름",
        "己未": "포근한 구름(己)이 화원(未) 위에 머무는 가장 무더운 여름",
        "庚申": "서늘한 달빛(庚)이 유명한 대도시(申)를 비추는 이른 가을",
        "辛酉": "하얀 서리(辛)가 사찰의 종(酉) 위에 내리는 완연한 가을",
        "壬戌": "가을이슬(壬)이 불태우는 근원(戌) 위에 맺히는 가을과 겨울의 환절기",
        "癸亥": "봄비(癸)가 쏟아지는 강물(亥)을 적시는 이른 겨울"
    },
    "ilju": {
        "甲子": "검은 연못(子) 위에 울려 퍼지는 우레(甲)의 형상",
        "乙丑": "버드나무 언덕(丑)에 불어오는 바람(乙)의 형상",
        "丙寅": "넓은 들판(寅)을 비추는 태양(丙)의 형상",
        "丁卯": "옥 같이 아름다운 숲(卯) 위에 떠있는 밤하늘 별(丁)의 형상",
        "戊辰": "우거진 늪지(辰)에 드리워진 노을(戊)의 형상",
        "己巳": "커다란 역(巳) 위에 떠도는 구름(己)의 형상",
        "庚午": "봉화대(午) 위에 떠있는 밤하늘 달(庚)의 형상",
        "辛未": "아름다운 화원(未) 위에 내려앉은 서리(辛)의 형상",
        "壬申": "대도시(申)를 적시는 가을이슬(壬)의 형상",
        "癸酉": "사찰의 종(酉) 위에 내리는 봄비(癸)의 형상",
        "甲戌": "불 태우는 근원(戌) 위에 울려 퍼지는 우레(甲)의 형상",
        "乙亥": "거대한 강물(亥)에 불어오는 바람(乙)의 형상",
        "丙子": "검은 연못(子)을 비추는 태양(丙)의 형상",
        "丁丑": "버드나무 언덕(丑) 위에 떠있는 밤하늘 별(丁)의 형상",
        "戊寅": "넓은 들판(寅) 위에 드리워진 노을(戊)의 형상",
        "己卯": "옥 같이 아름다운 숲(卯)에 떠도는 구름(己)의 형상",
        "庚辰": "우거진 늪지(辰) 위에 떠있는 밤하늘 달(庚)의 형상",
        "辛巳": "대도시(巳)에 내려앉은 서리(辛)의 형상",
        "壬午": "봉화대(午)에 맺혀진 가을이슬(壬)의 형상",
        "癸未": "아름다운 화원(未)을 적셔주는 봄비(癸)의 형상",
        "甲申": "대도시(申)에 울려 퍼지는 우레(甲)의 형상",
        "乙酉": "사찰의 종(酉)을 스치는 바람(乙)의 형상",
        "丙戌": "불 태우는 근원(戌)를 비추는 태양(丙)의 형상",
        "丁亥": "거대한 강물(亥)를 비치는 밤하늘 별(丁)의 형상",
        "戊子": "검은 연못(子) 위에 드리워진 노을(戊)의 형상",
        "己丑": "버드나무 언덕(丑) 위에 떠도는 구름(己)의 형상",
        "庚寅": "넓은 들판(寅)을 비추는 밤하늘 달(庚)의 형상",
        "辛卯": "옥 같이 아름다운 숲(卯) 위에 내려앉은 서리(辛)의 형상",
        "壬辰": "우거진 늪지(辰) 위에 맺혀진 가을이슬(壬)의 형상",
        "癸巳": "커다란 역(巳)을 적시는 봄비(癸)의 형상",
        "甲午": "봉화대(午) 위에 울려 퍼지는 우레(甲)의 형상",
        "乙未": "아름다운 화원(未)에 불어오는 바람(乙)의 형상",
        "丙申": "대도시(申)를 비추는 태양(丙)의 형상",
        "丁酉": "사찰의 종(酉)을 비추는 밤하늘 별(丁)의 형상",
        "戊戌": "불태우는 근원(戌) 위에 드리워진 노을(戊)의 형상",
        "己亥": "거대한 강물(亥) 위를 떠도는 구름(己)의 형상",
        "庚子": "검은 연못(子) 위에 떠있는 밤하늘 달(庚)의 형상",
        "辛丑": "버드나무 언덕(丑) 위에 내리앉은 서리(辛)의 형상",
        "壬寅": "넓은 들판(寅) 위에 맺혀진 가을이슬(壬)의 형상",
        "癸卯": "옥 같이 아름다운 숲(卯)을 적셔주는 봄비(癸)의 형상",
        "甲辰": "우거진 늪지(辰) 위에 울려 퍼지는 우레(甲)의 형상",
        "乙巳": "커다란 역(巳)으로 불어오는 바람(乙)의 형상",
        "丙午": "봉화대(午) 위에 떠있는 태양(丙)의 형상",
        "丁未": "아름다운 화원(未)를 비추는 밤하늘 별(丁)의 형상",
        "戊申": "대도시(申) 위에 드리워진 노을(戊)의 형상",
        "己酉": "사찰의 종(酉) 위를 떠도는 구름(己)의 형상",
        "庚戌": "불태우는 근원(戌) 위에 떠있는 밤하늘 달(庚)의 형상",
        "辛亥": "거대한 강물(亥)에 내려앉은 서리(辛)의 형상",
        "壬子": "검은 연못(子) 위로 맺혀진 가을이슬(壬)의 형상",
        "癸丑": "버드나무 언덕(丑) 위에 내리는 진눈개비(癸)의 형상",
        "甲寅": "넓은 들판(寅) 위에 울려 퍼지는 우레(甲)의 형상",
        "乙卯": "옥 같이 아름다운 숲(卯)에 불어오는 바람(乙)의 형상",
        "丙辰": "갯벌(辰) 위를 비추는 태양(丙)의 형상",
        "丁巳": "커다란 역(巳)을 비추는 밤하늘 별(丁)의 형상",
        "戊午": "봉화대(午)에 드리워진 노을(戊)의 형상",
        "己未": "아름다운 화원(未) 위를 떠도는 구름(己)의 형상",
        "庚申": "대도시(申) 위에 떠있는 밤하늘 달(庚)의 형상",
        "辛酉": "사찰의 종(酉) 위에 내려 앉은 서리(辛)의 형상",
        "壬戌": "불태우는 근원(戌) 위에 맺혀진 가을이슬(壬)의 형상",
        "癸亥": "거대한 강물(亥) 위에 새차게 내리는 봄비(癸)의 형상"
    },
    "ilju_structure": {
        "甲子": ["인성구조", "자기몰입형", "자의식 발달하여 발상의 전환이 빠르고 임사즉결"],
        "乙丑": ["재관인구조", "출세지향형", "편법적 사고와 신속한 결과를 추구하며 앞서가는 경향"],
        "丙寅": ["인비식구조", "자기중심형", "감정기복이 심하고 매사를 주도하는 구조"],
        "丁卯": ["인성구조", "자기몰입형", "자의식 발달하여 발상의 전환이 빠르고 임사즉결"],
        "戊辰": ["비재관구조", "결과집착형", "원칙을 추구하며 결과를 중시하는 노력파"],
        "己巳": ["인비식구조", "자기중심형", "감정기복이 심하고 매사를 주도하는 구조"],
        "庚午": ["관인구조", "순리중시형", "주어진 환경에 적응하며 자기만족을 느끼며 최선을 다함"],
        "辛未": ["재관인구조", "출세지향형", "편법적 사고와 신속한 결과를 추구하며 앞서가는 경향"],
        "壬申": ["관인비구조", "원칙중시형", "원칙적 삶에 얽매여 노력하며 끊임없는 갈등구조"],
        "癸酉": ["인성구조", "자기몰입형", "자의식 발달하여 발상의 전환이 빠르고 임사즉결"],
        "甲戌": ["식재관구조", "현실타파형", "원칙타파 및 현상개선의 자유주의"],
        "乙亥": ["인비재구조", "자기만족형", "목표 지향적이며 계산적 경제관념이 분명"],
        "丙子": ["관성구조", "자기억제형", "주변 의식하고 내면의 갈등을 억제하여 정제된 삶 추구"],
        "丁丑": ["식재관구조", "현실타파형", "원칙타파 및 현상개선의 자유주의"],
        "戊寅": ["관인비구조", "원칙중시형", "원칙적 삶에 얽매여 노력하며 끊임없는 갈등구조"],
        "己卯": ["관성구조", "자기억제형", "주변 의식하고 내면의 갈등을 억제하여 정제된 삶 추구"],
        "庚辰": ["식재인구조", "다재다능형", "다재다능하고 창조적 감성표출의 달인"],
        "辛巳": ["관인비구조", "원칙중시형", "원칙적 삶에 얽매여 노력하며 끊임없는 갈등구조"],
        "壬午": ["재관구조", "실리추구형", "현실적 이익과 명예를 추구하는 계산된 실속파"],
        "癸未": ["식재관구조", "현실타파형", "원칙타파 및 현상개선의 자유주의"],
        "甲申": ["재관인구조", "출세지향형", "편법적 사고와 신속한 결과를 추구하며 앞서가는 경향"],
        "乙酉": ["관성구조", "자기억제형", "주변 의식하고 내면의 갈등을 억제하여 정제된 삶 추구"],
        "丙戌": ["비식재구조", "분주다망형", "목표추구의 자기주도와 적극적 대외활동"],
        "丁亥": ["식관인구조", "현실동조형", "일처리에 능숙하고 변동과 변화에 초연한 심리"],
        "戊子": ["재성구조", "이재추구형", "결과의 명확성을 추구하며 기민하고 분주하게 활동"],
        "己丑": ["비식재구조", "분주다망형", "목표추구의 자기주도와 적극적 대외활동"],
        "庚寅": ["재관인구조", "출세지향형", "편법적 사고와 신속한 결과를 추구하며 앞서가는 경향"],
        "辛卯": ["재성구조", "이재추구형", "결과의 명확성을 추구하며 기민하고 분주하게 활동"],
        "壬辰": ["비식관구조", "조직봉사형", "조직과 봉사활동을 통해 정체성을 추구"],
        "癸巳": ["재관인구조", "출세지향형", "편법적 사고와 신속한 결과를 추구하며 앞서가는 경향"],
        "甲午": ["식재구조", "자기과시형", "내실보다 외형을 중시하고 다소 무모한 결과를 추구"],
        "乙未": ["비식재구조", "분주다망형", "목표추구의 자기주도와 적극적 대외활동"],
        "丙申": ["식재관구조", "현실타파형", "원칙타파 및 현상개선의 자유주의"],
        "丁酉": ["재성구조", "이재추구형", "결과의 명확성을 추구하며 기민하고 분주하게 활동"],
        "戊戌": ["인비식구조", "자기중심형", "감정기복이 심하고 매사를 주도하는 구조"],
        "己亥": ["비재관구조", "결과집착형", "원칙을 추구하며 결과를 중시하는 노력파"],
        "庚子": ["식상구조", "현실추구형", "능수능란한 수단으로 매사를 주도하며 활로 모색"],
        "辛丑": ["인비식구조", "자기중심형", "감정기복이 심하고 매사를 주도하는 구조"],
        "壬寅": ["식재관구조", "현실타파형", "원칙타파 및 현상개선의 자유주의"],
        "癸卯": ["식상구조", "현실추구형", "능수능란한 수단으로 매사를 주도하며 활로 모색"],
        "甲辰": ["인비재구조", "자기만족형", "목표 지향적이며 계산적 경제관념이 분명"],
        "乙巳": ["식재관구조", "현실타파형", "원칙타파 및 현상개선의 자유주의"],
        "丙午": ["비식구조", "자기주도형", "비교우위에 서고자 매사를 적극적으로 주도하며 외향적"],
        "丁未": ["인비식구조", "자기중심형", "감정기복이 심하고 매사를 주도하는 구조"],
        "戊申": ["비식재구조", "분주다망형", "목표추구의 자기주도와 적극적 대외활동"],
        "己酉": ["식상구조", "현실추구형", "능수능란한 수단으로 매사를 주도하며 활로 모색"],
        "庚戌": ["관인비구조", "원칙중시형", "원칙적 삶에 얽매여 노력하며 끊임없는 갈등구조"],
        "辛亥": ["식재인구조", "다재다능형", "다재다능하고 창조적 감성표출의 달인"],
        "壬子": ["비겁구조", "의지분출형", "독자적 활로 모색과 배타적 자력갱생"],
        "癸丑": ["관인비구조", "원칙중시형", "원칙적 삶에 얽매여 노력하며 끊임없는 갈등구조"],
        "甲寅": ["비식재구조", "분주다망형", "목표추구의 자기주도와 적극적 대외활동"],
        "乙卯": ["비겁구조", "의지분출형", "독자적 활로 모색과 배타적 자력갱생"],
        "丙辰": ["식관인구조", "현실동조형", "일처리에 능숙하고 변동과 변화에 초연한 심리"],
        "丁巳": ["비식재구조", "분주다망형", "목표추구의 자기주도와 적극적 대외활동"],
        "戊午": ["인비구조", "주도면밀형", "치밀하게 이해득실을 추구하는 자기발전형"],
        "己未": ["관인비구조", "원칙중시형", "원칙적 삶에 얽매여 노력하며 끊임없는 갈등구조"],
        "庚申": ["인비식구조", "자기중심형", "감정기복이 심하고 매사를 주도하는 구조"],
        "辛酉": ["비겁구조", "의지분출형", "독자적 활로 모색과 배타적 자력갱생"],
        "壬戌": ["재관인구조", "출세지향형", "편법적 사고와 신속한 결과를 추구하며 앞서가는 경향"],
        "癸亥": ["비식관구조", "조직봉사형", "조직과 봉사활동을 통해 정체성을 추구"]
    }
}

# ==============================================================================
# 1. 시스템 변수 세팅 및 써머타임 엔진
# ==============================================================================
def get_total_time_adjustment(dt):
    adj = -30
    if dt_mod.datetime(1954, 3, 21) <= dt <= dt_mod.datetime(1961, 8, 9, 23, 59): adj = 0
    si = [(dt_mod.datetime(1948,5,31), dt_mod.datetime(1948,9,22)), (dt_mod.datetime(1949,3,31), dt_mod.datetime(1949,9,30)), (dt_mod.datetime(1950,4,1), dt_mod.datetime(1950,9,10)), (dt_mod.datetime(1951,5,6), dt_mod.datetime(1951,9,9)), (dt_mod.datetime(1954,3,21), dt_mod.datetime(1954,5,5)), (dt_mod.datetime(1955,4,6), dt_mod.datetime(1955,9,22)), (dt_mod.datetime(1956,5,20), dt_mod.datetime(1956,9,30)), (dt_mod.datetime(1957,5,5), dt_mod.datetime(1957,9,22)), (dt_mod.datetime(1958,5,4), dt_mod.datetime(1958,9,21)), (dt_mod.datetime(1959,5,4), dt_mod.datetime(1959,9,20)), (dt_mod.datetime(1960,5,1), dt_mod.datetime(1960,9,18)), (dt_mod.datetime(1987,5,10,2), dt_mod.datetime(1987,10,11,3)), (dt_mod.datetime(1988,5,8,2), dt_mod.datetime(1988,10,9,3))]
    for s, e in si:
        if s <= dt <= e: adj -= 60; break
    return adj

# 십천간 / 십이지지 리스트 전역 선언
GAN = ["甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"]
JI = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]

def get_true_year_month_pillar(year, month, day, hour, minute):
    kst = pytz.timezone('Asia/Seoul')
    dt_kst = kst.localize(datetime(year, month, day, hour, minute))
    dt_utc = dt_kst.astimezone(pytz.utc)
    
    sun = ephem.Sun()
    sun.compute(dt_utc)
    lon = math.degrees(ephem.Ecliptic(sun).lon) % 360.0
    
    actual_year = year
    if month <= 2 and lon < 315.0:
        actual_year -= 1
        
    year_idx = (actual_year - 1984) % 60
    y_gan = GAN[year_idx % 10]
    y_ji = JI[year_idx % 12]
    
    if 315 <= lon < 345: m_ji_idx = 2    # 寅(인)월
    elif 345 <= lon or lon < 15: m_ji_idx = 3  # 卯(묘)월
    elif 15 <= lon < 45: m_ji_idx = 4    # 辰(진)월
    elif 45 <= lon < 75: m_ji_idx = 5    # 巳(사)월
    elif 75 <= lon < 105: m_ji_idx = 6   # 午(오)월
    elif 105 <= lon < 135: m_ji_idx = 7  # 未(미)월
    elif 135 <= lon < 165: m_ji_idx = 8  # 申(신)월
    elif 165 <= lon < 195: m_ji_idx = 9  # 酉(유)월
    elif 195 <= lon < 225: m_ji_idx = 10 # 戌(술)월
    elif 225 <= lon < 255: m_ji_idx = 11 # 亥(해)월
    elif 255 <= lon < 285: m_ji_idx = 0  # 子(자)월
    elif 285 <= lon < 315: m_ji_idx = 1  # 丑(축)월
    
    y_gan_idx = year_idx % 10
    start_month_gan_idx = ((y_gan_idx % 5) * 2 + 2) % 10
    m_offset = (m_ji_idx - 2) % 12
    m_gan = GAN[(start_month_gan_idx + m_offset) % 10]
    
    return f"{y_gan}{y_ji}", f"{m_gan}{JI[m_ji_idx]}", lon

components.html("""
<script>
    const doc = window.parent.document;
    doc.addEventListener('keyup', function(e) {
        if (e.target.tagName !== 'INPUT' || e.target.type !== 'text') return;
        let label = e.target.getAttribute('aria-label') || "";
        if (label.includes('년주') || label.includes('월주') || label.includes('일주')) {
            if (e.key === ' ' || e.target.value.includes('년') || e.target.value.includes('월') || e.target.value.includes('일') || e.target.value.includes('시')) {
                let inputs = Array.from(doc.querySelectorAll('input[type="text"]'));
                let idx = inputs.indexOf(e.target);
                if (idx > -1 && idx < inputs.length - 1) inputs[idx + 1].focus();
            }
        }
    });
</script>
""", height=0, width=0)

# ==============================================================================
# 2. AI 및 명리 연산 엔진 (구버전 'model' 변수 완벽 호환 최신 규격)
# ==============================================================================
try:
    # 1. 최신 SDK 클라이언트 생성
    client = genai.Client(api_key=st.secrets["GOOGLE_API_KEY"])
    
    # 2. 구버전 'model' 변수를 그대로 사용하는 코드들과의 완벽 호환성 레이어
    class GeminiModelCompat:
        def __init__(self, genai_client):
            self.client = genai_client
            
        def generate_content(self, contents, **kwargs):
            # 구버전 model.generate_content(...) 호출 시 최신 API로 자동 우회
            res = self.client.models.generate_content(
                model="gemini-2.5-flash",
                contents=contents
            )
            return res

    # 구버전 코드들이 찾고 있던 'model' 변수를 생성하여 매핑
    model = GeminiModelCompat(client)

except Exception as _api_e:
    st.error(f"🚨 Gemini API 키 오류: {_api_e}")
    client = None
    model = None

def call_claude_api(prompt_text, max_tokens=8000):
    # 상단에서 정의한 client 객체 존재 여부 확인
    if client is None:
        return "<div style='color:red;'>🚨 Gemini 모델이 초기화되지 않았습니다. API 키를 확인하세요.</div>"
    try:
        # 최신 google-genai SDK 전용 호출 문법
        response = client.models.generate_content(
            model="gemini-2.5-flash",  # 또는 "gemini-1.5-flash"
            contents=prompt_text
        )
        return response.text.strip()
    except Exception as e:
        return f"<div style='color:red;'>🚨 Gemini AI 서버 통신 장애: {e}</div>"
JIJANGGAN = {'子': ['壬', '-', '癸'], '丑': ['癸', '辛', '己'], '寅': ['戊', '丙', '甲'], '卯': ['甲', '-', '乙'], '辰': ['乙', '癸', '戊'], '巳': ['戊', '庚', '丙'], '午': ['丙', '己', '丁'], '未': ['丁', '乙', '己'], '申': ['戊', '壬', '庚'], '酉': ['庚', '-', '辛'], '戌': ['辛', '丁', '戊'], '亥': ['戊', '甲', '壬'] }

def get_color(c):
    if c in "甲乙寅卯": return "목"
    if c in "丙丁巳午": return "화"
    if c in "戊己辰戌丑未": return "토"
    if c in "庚辛申酉": return "금"
    if c in "壬癸亥子": return "수"
    return "토"

def get_current_saju_data():
    try:
        gans = st.session_state.get('saju_gans', ['?', '?', '?', '?'])
        jjis = st.session_state.get('saju_jjis', ['?', '?', '?', '?'])
        return gans, jjis
    except:
        return ['?', '?', '?', '?'], ['?', '?', '?', '?']

def get_ss(dg, tc):
    if tc in ["?", " ", "-"]: return "-"
    rels = {
        '甲':{'甲':'비견','乙':'겁재','丙':'식신','丁':'상관','戊':'편재','己':'정재','庚':'편관','辛':'정관','壬':'편인','癸':'정인','寅':'비견','卯':'겁재','巳':'식신','午':'상관','辰':'편재','戌':'편재','丑':'정재','未':'정재','申':'편관','酉':'정관','亥':'편인','子':'정인'},
        '乙':{'乙':'비견','甲':'겁재','丁':'식신','丙':'상관','己':'편재','戊':'정재','辛':'편관','庚':'정관','癸':'편인','壬':'정인','卯':'비견','寅':'겁재','午':'식신','巳':'상관','丑':'편재','未':'편재','辰':'정재','戌':'정재','酉':'편관','申':'정관','子':'편인','亥':'정인'},
        '丙':{'丙':'비견','丁':'겁재','戊':'식신','己':'상관','庚':'편재','辛':'정재','壬':'편관','癸':'정관','甲':'편인','乙':'정인','巳':'비견','午':'겁재','辰':'식신','戌':'식신','未':'상관','丑':'상관','申':'편재','酉':'정재','亥':'편관','子':'정관','寅':'편인','卯':'정인'},
        '丁':{'丁':'비견','丙':'겁재','己':'식신','戊':'상관','辛':'편재','庚':'정재','癸':'편관','壬':'정관','乙':'편인','甲':'정인','午':'비견','巳':'겁재','未':'식신','丑':'식신','辰':'상관','戌':'상관','酉':'편재','申':'정재','子':'편관','亥':'정관','卯':'편인','寅':'정인'},
        '戊':{'戊':'비견','己':'겁재','庚':'식신','辛':'상관','壬':'편재','癸':'정재','甲':'편관','乙':'정관','丙':'편인','丁':'정인','辰':'비견','戌':'비견','丑':'겁재','未':'겁재','申':'식신','酉':'상관','亥':'편재','子':'정재','寅':'편관','卯':'정관','巳':'편인','午':'정인'},
        '己':{'己':'비견','戊':'겁재','辛':'식신','庚':'상관','癸':'편재','壬':'정재','乙':'편관','甲':'정관','丁':'편인','丙':'정인','丑':'비견','未':'비견','辰':'겁재','戌':'겁재','酉':'식신','申':'상관','子':'편재','亥':'정재','卯':'편관','寅':'정관','午':'편인','巳':'정인'},
        '庚':{'庚':'비견','辛':'겁재','壬':'식신','癸':'상관','甲':'편재','乙':'정재','丙':'편관','丁':'정관','戊':'편인','己':'정인','申':'비견','酉':'겁재','亥':'식신','子':'상관','寅':'편재','卯':'정재','巳':'편관','午':'정관','辰':'편인','戌':'편인','丑':'정인','未':'정인'},
        '辛':{'辛':'비견','庚':'겁재','癸':'식신','壬':'상관','乙':'편재','甲':'정재','丁':'편관','丙':'정관','己':'편인','戊':'정인','酉':'비견','申':'겁재','子':'식신','亥':'상관','卯':'편재','寅':'정재','午':'편관','巳':'정관','未':'편인','丑':'편인','辰':'정인','戌':'정인'},
        '壬':{'壬':'비견','癸':'겁재','甲':'식신','乙':'상관','丙':'편재','丁':'정재','戊':'편관','己':'정관','庚':'편인','辛':'정인','亥':'비견','子':'겁재','寅':'식신','卯':'상관','巳':'편재','午':'정재','辰':'편관','戌':'편관','丑':'정관','未':'정관','申':'편인','酉':'정인'},
        '癸':{'癸':'비견','壬':'겁재','乙':'식신','甲':'상관','丁':'편재','丙':'정재','己':'편관','戊':'정관','辛':'편인','庚':'정인','子':'비견','亥':'겁재','卯':'식신','寅':'상관','午':'편재','巳':'정재','未':'편관','丑':'편관','戌':'정관','辰':'정관','酉':'편인','申':'정인'}
    }
    return rels.get(dg, {}).get(tc, "-")

def get_unsung(dg, ji):
    if ji in ["?", " ", "-"]: return "-"
    table = {'甲':"亥子丑寅卯辰巳午未申酉戌",'丙':"寅卯辰巳午未申酉戌亥子丑",'戊':"寅卯辰巳午未申酉戌亥子丑",'庚':"巳午未申酉戌亥子丑寅卯辰",'壬':"申酉戌亥子丑寅卯辰巳午未",'乙':"午巳辰卯寅丑子亥戌酉申未",'丁':"酉申未午巳辰卯寅丑子亥戌",'己':"酉申未午巳辰卯寅丑子亥戌",'辛':"子亥戌酉申未午巳辰卯寅丑",'癸':"卯寅丑子亥戌酉申未午巳辰"}
    idx = table.get(dg, "").find(ji)
    return ["장생","목욕","관대","건록","제왕","쇠","병","사","묘","절","태","양"][idx] if idx != -1 else "-"

def get_12_shinsal(year_ji, target_ji):
    if target_ji in ["?", " ", "-"] or not year_ji or year_ji == "?": return "-"
    s_map = {"申":"巳","子":"巳","辰":"巳", "寅":"亥","午":"亥","戌":"亥", "巳":"寅","酉":"寅","丑":"寅", "亥":"申","卯":"申","未":"申"}
    s_idx = (list(JI).index(target_ji) - list(JI).index(s_map.get(year_ji, "巳")) + 12) % 12
    return ["겁살","재살","천살","지살","년살","월살","망신살","장성살","반안살","역마살","육해살","화개살"][s_idx]

def get_samjae(year_ji, target_ji):
    if year_ji in ["?", " ", "-"] or target_ji in ["?", " ", "-"]: return "해당 없음"
    s_map = {
        '申': ['寅','卯','辰'], '子': ['寅','卯','辰'], '辰': ['寅','卯','辰'],
        '亥': ['巳','午','未'], '卯': ['巳','午','未'], '未': ['巳','午','未'],
        '寅': ['申','酉','戌'], '午': ['申','酉','戌'], '戌': ['申','酉','戌'],
        '巳': ['亥','子','丑'], '酉': ['亥','子','丑'], '丑': ['亥','子','丑']
    }
    sj_list = s_map.get(year_ji, [])
    if not sj_list: return "해당 없음"
    if target_ji == sj_list[0]: return "들삼재"
    elif target_ji == sj_list[1]: return "눌삼재"
    elif target_ji == sj_list[2]: return "날삼재"
    return "해당 없음"

def get_gan_rel_all(idx, gans):
    me = gans[idx]; res = []
    if me in ["-", "?", " "]: return "-"
    for i, other in enumerate(gans):
        if i == idx or other in ["-", "?", " "]: continue
        s = {me, other}
        if s in [{'甲','己'}, {'乙','庚'}, {'丙','辛'}, {'丁','壬'}, {'戊','癸'}]: res.append("합")
        if s in [{'甲','庚'}, {'乙','辛'}, {'丙','壬'}, {'丁','癸'}, {'戊','甲'}, {'己','乙'}]: res.append("충")
    return "".join(list(set(res))) if res else "-"

def get_ji_rel_set(me, target):
    if not me or not target or me == "?" or target == "?" or me == target: return "자형" if me == target and me in "辰午酉亥" else "-"
    s, r = {me, target}, []
    if s in [{'寅','卯'}, {'卯','辰'}, {'寅','辰'}, {'巳','午'}, {'午','未'}, {'巳','未'}, {'申','酉'}, {'酉','戌'}, {'申','戌'}, {'亥','子'}, {'子','丑'}, {'亥','丑'}]: r.append("방합")
    if s in [{'申','子'}, {'子','辰'}, {'申','辰'}, {'寅','午'}, {'午','戌'}, {'寅','戌'}, {'亥','卯'}, {'卯','未'}, {'亥','未'}, {'巳','酉'}, {'酉','丑'}, {'巳','丑'}]: r.append("반합")
    if s in [{'子','丑'}, {'寅','亥'}, {'卯','戌'}, {'辰','酉'}, {'巳','申'}, {'午','未'}]: r.append("육합")
    if s in [{'午','亥'}, {'子','戌'}, {'丑','寅'}, {'寅','未'}, {'卯','申'}]: r.append("암합")
    if s in [{'子','午'}, {'丑','未'}, {'寅','申'}, {'卯','酉'}, {'辰','戌'}, {'巳','亥'}]: r.append("충")
    if s in [{'寅','巳'}, {'巳','申'}, {'寅','申'}, {'丑','戌'}, {'戌','未'}, {'丑','未'}, {'子','卯'}]: r.append("형")
    if s in [{'子','未'}, {'丑','午'}, {'寅','巳'}, {'卯','辰'}, {'申','亥'}, {'酉','戌'}]: r.append("해")
    if s in [{'子','酉'}, {'丑','辰'}, {'寅','亥'}, {'卯','午'}, {'巳','申'}, {'未','戌'}]: r.append("파")
    if s in [{'丑','午'}, {'卯','申'}, {'辰','亥'}, {'巳','戌'}]: r.extend(["원진", "귀문"])
    elif s in [{'子','酉'}, {'寅','未'}]: r.append("귀문")
    elif s in [{'寅','酉'}, {'子','未'}]: r.append("원진")
    if s == {'戌','亥'}: r.append("천라")
    if s == {'辰','巳'}: r.append("지망")
    return ", ".join(list(dict.fromkeys(r))) if r else "-"

def get_general_shinsal_filtered(idx, gans, jjis, gender="남성"):
    dc, mc, yc = gans[1], gans[2], gans[3]
    dj, mj, yj = jjis[1], jjis[2], jjis[3]
    cur_g, cur_j = gans[idx], jjis[idx]
    
    if cur_g in ["?", "-", " "] or cur_j in ["?", "-", " "]: return []
    gj = cur_g + cur_j
    noble, ausp, evil = [], [], []
    
    if cur_j in {'甲':'未丑','乙':'申子','丙':'酉亥','丁':'酉亥','戊':'未丑','己':'申子','庚':'未丑','辛':'午寅','壬':'卯巳','癸':'卯巳'}.get(dc,""): noble.append("천을귀인") 
    if cur_j == mj: noble.append("월덕귀인") 
    if cur_j in {'甲':'子午','乙':'子午','丙':'卯酉','丁':'卯酉','戊':'辰戌丑未','己':'辰戌丑未','庚':'寅亥','辛':'寅亥','壬':'巳申','癸':'巳申'}.get(dc,""): noble.append("태극귀인") 
    if cur_j in {'甲':'寅','乙':'卯','丙':'巳','丁':'午','戊':'巳','己':'午','庚':'申','辛':'酉','壬':'亥','癸':'子'}.get(dc,""): noble.append("천록귀인") 
    if cur_j in {'甲':'巳','乙':'午','丙':'申','戊':'申','丁':'酉','己':'酉','庚':'亥','辛':'子','壬':'寅','癸':'卯'}.get(dc,""): noble.append("문창귀인")
    if cur_j in {'甲':'亥','乙':'子','丙':'寅','戊':'寅','丁':'卯','己':'卯','庚':'巳','辛':'午','壬':'申','癸':'酉'}.get(dc,""): noble.append("문곡귀인")
    if cur_j in {'甲':'亥','乙':'午','丙':'寅','戊':'寅','丁':'酉','己':'酉','庚':'巳','辛':'子','壬':'申','癸':'卯'}.get(dc,""): noble.append("학당귀인")
    if gj in ["甲寅", "乙丑", "丙子", "丁酉", "戊申", "己未", "庚午", "辛巳", "壬辰", "癸卯"]: noble.append("복성귀인")
    if cur_j in {'甲':'巳','乙':'午','丙':'巳','丁':'午','戊':'申','己':'酉','庚':'亥','辛':'子','壬':'寅','癸':'卯'}.get(dc,""): noble.append("천주귀인")
    
    if cur_j in {'甲':'寅','乙':'卯','丙':'巳','丁':'午','戊':'巳','己':'午','庚':'申','辛':'酉','壬':'亥','癸':'子'}.get(dc,""): ausp.append("건록")
    if cur_j in {'甲':'亥','乙':'戌','丙':'申','戊':'申','丁':'未','己':'未','庚':'巳','辛':'辰','壬':'寅','癸':'丑'}.get(dc,""): noble.append("암록")
    if cur_j in {'甲':'辰','乙':'巳','丙':'未','戊':'未','丁':'申','己':'申','庚':'戌','辛':'亥','壬':'丑','癸':'寅'}.get(dc,""): ausp.append("금여록")
    if gj in ["甲寅", "丙辰", "戊辰", "庚辰", "壬戌"]: ausp.append("일덕")
    if gj in ["乙丑", "己巳", "癸酉"] and idx in [0, 1]: ausp.append("금신")
    hyeop_map = {'甲':['丑','卯'], '乙':['寅','辰'], '丙':['辰','午'], '戊':['辰','午'], '丁':['巳','未'], '己':['巳','未'], '庚':['未','酉'], '辛':['申','戌'], '壬':['戌','子'], '癸':['亥','丑']}
    if cur_j in hyeop_map.get(dc, []): ausp.append("협록")  
    
    if gj in ["甲辰","乙未","丙戌","丁丑","戊辰","壬戌","癸丑"]: evil.append("백호대살")
    if gj in ["庚辰","庚戌","壬辰","壬戌","戊戌"]: evil.append("괴강살")
    if cur_j in {'甲':'卯','丙':'午','戊':'午','庚':'酉','壬':'子'}.get(dc,""): evil.append("양인살")

    if cur_j in {'甲':'酉','乙':'戌','丙':'子','丁':'丑','戊':'子','己':'丑','庚':'卯','辛':'辰','壬':'午','癸':'未'}.get(dc,""): evil.append("비인살")
    if dj == '寅' and cur_j in ['寅', '巳', '申']: evil.append("탕화살")
    if dj == '午' and cur_j in ['辰', '午', '丑']: evil.append("탕화살")
    if dj == '丑' and cur_j in ['午', '未', '戌']: evil.append("탕화살")
    if cur_g in ['乙', '己'] or cur_j in ['巳', '丑']: evil.append("곡각살")
    if cur_g in ['甲', '辛'] or cur_j in ['卯', '午', '申', '未']: evil.append("현침살")

    if gj in ["甲寅", "乙卯", "丙午", "丁巳", "戊辰", "戊戌", "己未", "己丑", "庚申", "辛酉", "壬子", "癸亥"]: evil.append("간여지동")
    if gj in ["甲寅","乙巳","丁巳","戊申","辛亥"]: evil.append("고란살")
    if gj in ["丙子","丁丑","戊寅","辛卯","壬辰","癸巳","丙午","丁未","戊申","辛酉","壬戌","癸亥"]: evil.append("음양차착")
    if gj in ["甲午", "丙戌", "戊辰", "庚辰", "壬戌", "乙巳", "丁亥", "己亥", "辛巳", "癸亥"]: evil.append("의처의부")
    if cur_j in ['寅','申','巳','亥']: evil.append("효신살")

    dohwa_map = {'寅':'卯', '午':'卯', '戌':'卯', '申':'酉', '子':'酉', '辰':'酉', '巳':'午', '酉':'午', '丑':'午', '亥':'子', '卯':'子', '未':'子'}
    if cur_j == dohwa_map.get(yj, "") or cur_j == dohwa_map.get(dj, ""): evil.append("도화살")
    if gj in ["甲子", "乙巳", "丁卯", "庚午", "辛亥", "癸酉"]: evil.append("나체도화")
    if gj in ["甲午","丙寅","丁未","戊辰","庚戌","辛酉","壬子"]: evil.append("홍염살")
    if gj in ["甲寅", "乙卯", "丁未", "戊戌", "己未", "庚申", "辛酉", "癸丑"]: evil.append("음욕살")
    if gender == "여성" and gj in ["甲寅", "甲申", "丁丑", "戊申", "己丑", "辛未", "壬寅", "癸未"]: evil.append("남연살")
    if gender == "남성" and gj in ["乙丑", "丙申", "丁丑", "己未", "庚寅", "辛未", "壬寅", "壬申"]: evil.append("여연살")

    if cur_j in ['卯','酉','戌'] and (jjis.count('卯') + jjis.count('酉') + jjis.count('戌')) >= 2: evil.append("철쇄개금")
    if cur_j in ['子','午','卯','酉']: evil.append("교신성")
    if idx == 1 and gj in ["丙午", "丁未", "戊午", "戊子", "己未", "己丑"]: evil.append("육수살")
    if gj in ["甲辰","乙巳","丙申","丁亥","戊戌","己丑","庚辰","辛巳","壬申","癸亥"]: evil.append("십악대패살")
    if cur_g in ['甲', '丙', '壬'] and cur_j in ['子', '辰']: evil.append("평두살")
    cheolsa_map = {'甲':'辰', '乙':'寅', '丙':'戌', '丁':'申', '戊':'午', '己':'辰', '庚':'寅', '辛':'戌', '壬':'申', '癸':'午'}
    if cur_j == cheolsa_map.get(dc, ""): evil.append("철사관")

    if gj in ["甲子", "甲午", "己卯", "己酉"]: ausp.append("진신") 
    if gj in ["丙子", "丙午", "辛卯", "辛酉"]: evil.append("교신") 
    if gj in ["丁丑", "丁未", "壬辰", "壬戌"]: evil.append("퇴신") 
    if gj in ["戊寅", "戊申", "癸巳", "癸亥"]: evil.append("복신") 

    result = []
    for n in list(dict.fromkeys(noble)): result.append(f"<span style='color:#0D47A1;'>{n}</span>")
    for a in list(dict.fromkeys(ausp)): result.append(f"<span style='color:#2E7D32;'>{a}</span>")
    for e in list(dict.fromkeys(evil)): result.append(f"<span style='color:#C62828;'>{e}</span>")
    return result

def get_jijanggan_full(dg, ji):
    if ji in ["?", "-", " "]: return "-"
    raw = {'子':['壬','-','癸'],'丑':['癸','辛','己'],'寅':['戊','丙','甲'],'卯':['甲','-','乙'],'辰':['乙','癸','戊'],'巳':['戊','庚','丙'],'午':['丙','己','丁'],'未':['丁','乙','己'],'申':['戊','壬','庚'],'酉':['庚','-','辛'],'戌':['辛','丁','戊'],'亥':['戊','甲','壬']}.get(ji, ['-','-','-'])
    res = "<div style='display:flex; flex-direction:column; height:100%; min-height:65px; gap:2px; padding:2px 0; margin:0;'>"
    for j in raw:
        if j != '-':
            ss_label = get_ss(dg, j)[:2]; color_key = get_color(j)
            bg = {'목':'#2E7D32','화':'#C62828','토':'#F9A825','금':'#9E9E9E','수':'#212121'}.get(color_key, '#888')
            tc = 'white' if color_key != '토' else 'black'
            res += f"<div style='flex-grow:1; display:flex; align-items:center; justify-content:center; background:{bg}; color:{tc}; width:95%; margin:0 auto; font-size:12px; font-weight:900; border-radius:3px;'>{j} ({ss_label})</div>"
        else: 
            res += "<div style='flex-grow:1; display:flex; align-items:center; justify-content:center; background:#f9f9f9; width:95%; margin:0 auto; color:#bbb; border-radius:3px; border:1px dashed #ddd;'>-</div>"
    return res + "</div>"

def check_vault_status(base_gans, base_jjis, attacker_ji):
    vaults = ['辰', '戌', '丑', '未']
    clash_map = {'辰':'戌', '戌':'辰', '丑':'未', '未':'丑'}
    hyung_sets = [{'丑','戌'}, {'戌','未'}, {'丑','未'}]
    core_gans = {'辰':['壬','癸'], '戌':['丙','丁'], '丑':['庚','辛'], '未':['甲','乙']}
    
    results = []
    for i, ji in enumerate(base_jjis):
        if ji in vaults:
            if clash_map.get(ji) == attacker_ji or {ji, attacker_ji} in hyung_sets:
                targets = core_gans.get(ji, [])
                is_trapped = any(g in targets for g in base_gans)
                if is_trapped:
                    trapped_chars = [g for g in targets if g in base_gans]
                    results.append(f"🚨 <b style='color:#C62828;'>[입고(入庫) 주의]</b> {ji} 무덤이 열려 천간의 {','.join(trapped_chars)} 기운이 빨려 들어갑니다.")
                else:
                    results.append(f"💎 <b style='color:#2E7D32;'>[개고(開庫) 발현]</b> {ji} 금고가 열려 지장간의 숨은 보물이 세상에 드러납니다.")
    return results

def get_gyukgook_detailed(ds, ys, ms, hs, mb):
    # 🚨 에러의 원인이었던 _to_hanja 변환 줄을 완전히 삭제했습니다! (엔진이 이미 한자로 넘겨주므로 불필요)
    jg = JIJANGGAN.get(mb, [])
    if not jg: return "알수없음격", "지장간 정보가 없습니다."

    if ds in ['甲', '丙', '戊', '庚', '壬']:
        if mb == '卯' and ds == '甲': return "양인격", "월지 겁재 및 제왕으로 폭발적 에너지인 양인격입니다."
        if mb == '午' and ds == '丙': return "양인격", "월지 겁재 및 제왕으로 폭발적 에너지인 양인격입니다."
        if mb == '酉' and ds == '庚': return "양인격", "월지 겁재 및 제왕으로 폭발적 에너지인 양인격입니다."
        if mb == '子' and ds == '壬': return "양인격", "월지 겁재 및 제왕으로 폭발적 에너지인 양인격입니다."
        if mb == {'甲':'寅', '丙':'巳', '戊':'巳', '庚':'申', '壬':'亥'}.get(ds, ""):
            return "건록격", f"월지 {mb}가 일간 {ds}의 건록(建祿)에 해당하여 건록격으로 정합니다."

    def safe_get_ss(day_gan, target_char):
        if not target_char or target_char == "?": return "무명"
        return get_ss(day_gan, target_char)

    if mb in ["子", "午", "卯", "酉"]:
        core_ss = safe_get_ss(ds, mb)
        if core_ss in ["비견", "겁재"]:
            return "건록(월겁)격", f"월지 {mb}가 일간 {ds}와 같은 기운이므로 건록(월겁)격으로 삼습니다."
        return core_ss + "격", f"월지 {mb}의 순수한 기운인 {core_ss}을 그대로 격으로 삼습니다."
    
    target_gans = [ys, ms, hs] 
    main_qi = jg[-1]
    
    def is_valid_gyuk(char):
        return safe_get_ss(ds, char) not in ["비견", "겁재"]
    
    if main_qi in target_gans and is_valid_gyuk(main_qi):
        return safe_get_ss(ds, main_qi) + "격", f"월지 {mb}의 정기(본기)인 {main_qi}이 천간에 투출하여 {safe_get_ss(ds, main_qi)}격이 되었습니다."
    if len(jg) >= 2 and jg[1] in target_gans and is_valid_gyuk(jg[1]):
        return safe_get_ss(ds, jg[1]) + "격", f"월지 {mb}의 중기인 {jg[1]}이 천간에 투출하여 {safe_get_ss(ds, jg[1])}격이 되었습니다."
    if len(jg) >= 1 and jg[0] in target_gans and is_valid_gyuk(jg[0]):
        return safe_get_ss(ds, jg[0]) + "격", f"월지 {mb}의 여기인 {jg[0]}이 천간에 투출하여 {safe_get_ss(ds, jg[0])}격이 되었습니다."
        
    fallback_ss = safe_get_ss(ds, main_qi)
    if fallback_ss in ["비견", "겁재"]:
        return "건록(월겁)격", f"월지 {mb}의 본기가 {fallback_ss}이므로 건록(월겁)격으로 정합니다."
    
    return fallback_ss + "격", f"월지 {mb}의 지장간(비겁 제외)이 투출하지 않아 정기(본기)인 {main_qi}를 기준으로 {fallback_ss}격으로 정합니다."

def calculate_gongmang(ilgan, ilji):
    if ilgan in ["?"," ","-"] or ilji in ["?"," ","-"]: return "-"
    try:
        base = (list(JI).index(ilji) - list(GAN).index(ilgan) - 2) % 12
        return list(JI)[base] + "," + list(JI)[(base+1)%12]
    except: return "-"

def get_time_ganji(day_gan, time_str, dt_obj=None):
    if "시간 모름" in time_str: return "?", "?"
    if dt_obj:
        adj_mins = get_total_time_adjustment(dt_obj)
        dt_obj += dt_mod.timedelta(minutes=adj_mins)
    
    target_ji, t_idx = "子", 0
    if "朝子" in time_str or "夜子" in time_str: target_ji, t_idx = "子", 0
    else:
        for j in list(JI):
            if j in time_str: target_ji, t_idx = j, list(JI).index(j); break
    start_gan_idx = {"甲":0,"己":0,"乙":2,"庚":2,"丙":4,"辛":4,"丁":6,"壬":6,"戊":8,"癸":8}.get(day_gan, 0)
    return list(GAN)[(start_gan_idx + t_idx) % 10], target_ji

def get_daeun_su_accurate(utc_dt, order):
    try:
        sun = ephem.Sun()
        def get_lon(dt):
            sun.compute(dt)
            return math.degrees(ephem.Ecliptic(sun).lon) % 360.0

        start_lon = get_lon(utc_dt)
        jeol_lons = [315, 345, 15, 45, 75, 105, 135, 165, 195, 225, 255, 285]
        
        if order == 1:
            t_lon_unwrapped = min([l for l in jeol_lons if l > start_lon] + [l + 360 for l in jeol_lons if l <= start_lon])
        else:
            t_lon_unwrapped = max([l for l in jeol_lons if l <= start_lon] + [l - 360 for l in jeol_lons if l > start_lon])
            
        search_dt = utc_dt
        step = dt_mod.timedelta(minutes=10) if order == 1 else dt_mod.timedelta(minutes=-10)
        
        for _ in range(6000):
            search_dt += step
            curr_lon = get_lon(search_dt)
            
            if order == 1 and curr_lon < start_lon and (start_lon - curr_lon) > 180:
                curr_lon += 360
            elif order == -1 and curr_lon > start_lon and (curr_lon - start_lon) > 180:
                curr_lon -= 360
                
            if (order == 1 and curr_lon >= t_lon_unwrapped) or (order == -1 and curr_lon <= t_lon_unwrapped):
                break
                
        total_days = abs((search_dt - utc_dt).total_seconds()) / 86400.0
        d_su = int(round(total_days / 3.0))
        
        if d_su == 0: d_su = 1
        elif d_su > 10: d_su = 10
        
        return d_su
    except Exception as e: 
        return 1

# 🚨 [함수 복구] 출산택일 정밀 연산 엔진 (어디서든 호출 가능하도록 엔진부에 승격 배치)
def get_optimized_delivery_days(start_date, end_date, m_jjis, f_jjis, forbidden_list):
    results = []
    curr_date = start_date
    while curr_date <= end_date:
        # 박사님의 기존 연산 로직이 들어가는 자리입니다. 
        # (현재는 에러 방지를 위해 기본 점수로 상위 5개 날짜를 반환하도록 세팅해 두었습니다.)
        score = 80 
        
        # 금기일 필터링 등 조건 추가 가능
        results.append({'date': curr_date.strftime('%Y-%m-%d'), 'score': score})
        curr_date += dt_mod.timedelta(days=1)
        
    return sorted(results, key=lambda x: x['score'], reverse=True)[:5]

# ==============================================================================
# 3. 프리미엄 궁합 분석 엔진 클래스 (ver 38.0 통합 업그레이드본)
# ==============================================================================
def get_group_ss(ss_str):
    return {'비견':'비겁', '겁재':'비겁', '식신':'식상', '상관':'식상', '편재':'재성', '정재':'재성', '편관':'관성', '정관':'관성', '편인':'인성', '정인':'인성'}.get(ss_str, '비겁')

class UniversalPrintableGunghap:
    def __init__(self, applicant, partner_name, male, female, daeun_score=10):
        self.app, self.p_name, self.daeun_score = applicant, partner_name, daeun_score
        
        male = [m if m and len(m) >= 2 else "  " for m in (list(male) + ["  ", "  ", "  ", "  "])][:4]
        female = [f if f and len(f) >= 2 else "  " for f in (list(female) + ["  ", "  ", "  ", "  "])][:4]
        
        self.m_g = [male[3][0], male[2][0], male[1][0], male[0][0]]
        self.m_j = [male[3][1], male[2][1], male[1][1], male[0][1]]
        self.f_g = [female[3][0], female[2][0], female[1][0], female[0][0]]
        self.f_j = [female[3][1], female[2][1], female[1][1], female[0][1]]
        
        self.logic_flags, self.details = {}, []

    def get_ji_rel(self, j1, j2):
        if not j1 or not j2 or j1=="?" or j2=="?": return "무"
        s = {j1, j2}
        if s in [{'子','丑'}, {'寅','亥'}, {'卯','戌'}, {'辰','酉'}, {'巳','申'}, {'午','未'}]: return "육합"
        if s in [{'寅','卯'}, {'卯','辰'}, {'寅','辰'}, {'巳','午'}, {'午','未'}, {'巳','未'}, {'申','酉'}, {'酉','戌'}, {'申','戌'}, {'亥','子'}, {'子','丑'}, {'亥','丑'}]: return "방합"
        if s in [{'申','子'}, {'子','辰'}, {'申','辰'}, {'寅','午'}, {'午','戌'}, {'寅','戌'}, {'亥','卯'}, {'卯','未'}, {'亥','未'}, {'巳','酉'}, {'酉','丑'}, {'巳','丑'}]: return "반합"
        if s in [{'子','午'}, {'丑','未'}, {'寅','申'}, {'卯','酉'}, {'辰','戌'}, {'巳','亥'}]: return "충"
        if s in [{'子','未'}, {'丑','午'}, {'寅','酉'}, {'卯','申'}, {'辰','亥'}, {'巳','戌'}]: return "원진"
        if s in [{'寅','巳'}, {'巳','申'}, {'寅','申'}, {'丑','戌'}, {'戌','未'}, {'丑','未'}, {'子','卯'}]: return "형"
        if s in [{'子','酉'}, {'丑','辰'}, {'寅','亥'}, {'卯','午'}, {'巳','申'}, {'未','戌'}]: return "파"
        if s in [{'子','未'}, {'丑','午'}, {'寅','巳'}, {'卯','辰'}, {'申','亥'}, {'酉','戌'}]: return "해"
        return "무"

    def count_elements(self, gans, jjis):
        counts = {'목':0, '화':0, '토':0, '금':0, '수':0}
        for c in gans + jjis:
            if c in "甲乙寅卯": counts['목'] += 1
            elif c in "丙丁巳午": counts['화'] += 1
            elif c in "戊己辰戌丑未": counts['토'] += 1
            elif c in "庚辛申酉": counts['금'] += 1
            elif c in "壬癸亥子": counts['수'] += 1
        return counts

    # 🌟 추가 보강: 묘고 및 조후 연산 (run_universal_logic 내에서 호출 가능)
    def get_vault_harmony(self, base_gans, base_jjis, partner_jjis):
        results = []
        for p_ji in partner_jjis:
            results.extend(check_vault_status(base_gans, base_jjis, p_ji))
        return results

    def get_johoo_harmony(self, m_ilgan, m_ec, f_ec):
        # 계절별 조후 용신(水/火 위주) 보완 연산 로직
        score = 0
        if m_ilgan in "丙丁": # 여름생
            if f_ec['수'] >= 2: score += 5
        elif m_ilgan in "壬癸": # 겨울생
            if f_ec['화'] >= 2: score += 5
        return score

    def run_universal_logic(self):
        m_g, m_j, f_g, f_j = self.m_g, self.m_j, self.f_g, self.f_j
        
        # [수술] 인덱스 정상화 (0:년, 1:월, 2:일, 3:시). 일지는 [2]입니다.
        il_rel = self.get_ji_rel(m_j[2], f_j[2])
        
        if il_rel == "육합": s1 = 25
        elif il_rel in ["방합", "반합"]: s1 = 21
        elif il_rel == "무": s1 = 17
        elif il_rel in ["파", "해"]: s1 = 12
        elif il_rel in ["형", "원진"]: s1 = 8
        elif il_rel == "충": s1 = 5
        else: s1 = 17
        p1 = int((s1 / 25) * 100)

        s2 = 5 
        # [수술] 년[0], 월[1], 시[3] 정상 비교
        n_rel, w_rel, si_rel = self.get_ji_rel(m_j[0], f_j[0]), self.get_ji_rel(m_j[1], f_j[1]), self.get_ji_rel(m_j[3], f_j[3]) 
        if n_rel in ["육합", "방합", "반합"]: s2 += 2
        elif n_rel == "충": s2 -= 1
        if w_rel in ["육합", "방합", "반합"]: s2 += 2
        elif w_rel == "충": s2 -= 1
        if si_rel in ["육합", "방합", "반합"]: s2 += 1
        s2 = max(0, min(10, s2))
        p2 = int((s2 / 10) * 100)

        m_ec, f_ec = self.count_elements(m_g, m_j), self.count_elements(f_g, f_j)
        s3 = 5
        for e in ['목','화','토','금','수']:
            if m_ec[e] == 0 and f_ec[e] >= 2: s3 += 2 
            if f_ec[e] == 0 and m_ec[e] >= 2: s3 += 2 
            if m_ec[e] >= 4 and f_ec[e] >= 4: s3 -= 2 
        s3 = max(0, min(10, s3))
        p3 = int((s3 / 10) * 100)

        s4 = 5
        bad_iljus, goran, nache = ["甲寅", "乙卯", "庚申", "辛酉", "戊辰", "戊戌"], ["甲寅", "乙巳", "丁巳", "戊申", "辛亥"], ["甲子", "乙巳", "丁卯", "庚午", "辛亥", "癸酉"] 
        m_ilju, f_ilju = m_g[2] + m_j[2], f_g[2] + f_j[2] # [수술] 일주 합치기 [2]
        if m_ilju in bad_iljus or m_ilju in goran or m_ilju in nache: s4 -= 1
        if f_ilju in bad_iljus or f_ilju in goran or f_ilju in nache: s4 -= 1
        s4 = max(0, min(5, s4))
        p4 = int((s4 / 5) * 100)

        s5 = min(10, self.daeun_score)
        p5 = int((s5 / 10) * 100)

        risk = 0.0
        if il_rel == "충": risk += 0.10 
        elif il_rel in ["형", "원진"]: risk += 0.05 
        
        def count_ss_groups(dc, chars):
            res = {'비겁':0, '식상':0, '재성':0, '관성':0, '인성':0}
            for c in chars:
                if c and c not in ["?", " ", "-"]:
                    try:
                        ss = get_group_ss(get_ss(dc, c))
                        if ss in res: res[ss] += 1
                    except: pass
            return res
        
        m_ss, f_ss = count_ss_groups(m_g[2], m_g + m_j), count_ss_groups(f_g[2], f_g + f_j) # [수술] 일간 [2] 기준
        if m_ss['비겁'] >= 4: risk += 0.05 
        if m_ss['재성'] == 0: risk += 0.05 
        if f_ss['식상'] >= 4: risk += 0.05 
        if f_ss['관성'] >= 4 or f_ss['관성'] == 0: risk += 0.05 

        risk = min(0.20, risk) 
        p6_safety = int((1.0 - risk) * 100)

        base_bonus = 40 
        sub_total = base_bonus + s1 + s2 + s3 + s4 + s5
        self.final_score = max(40, min(100, int(sub_total * (1.0 - risk))))

        if self.final_score >= 90: self.grade = "천생연분 (최고의 인연)"
        elif self.final_score >= 85: self.grade = "상생연분 (함께하면 좋은 인연)"
        elif self.final_score >= 80: self.grade = "동행연분 (편안하고 안정적인 인연)"
        elif self.final_score >= 70: self.grade = "보완연분 (서로를 채워주는 인연)"
        elif self.final_score >= 60: self.grade = "성장연분 (이해하며 맞춰가는 인연)"
        else: self.grade = "조율연분 (인내와 배려가 필요한 인연)"

        self.details = [
            {"label": "내면의 유대감", "pct": p1, "color": "#9b59b6"},
            {"label": "환경 조화", "pct": p2, "color": "#2ecc71"},
            {"label": "기운 상호보완", "pct": p3, "color": "#3498db"},
            {"label": "특수 기운", "pct": p4, "color": "#f1c40f"},
            {"label": "대운 기상도 조화", "pct": p5, "color": "#8e44ad"},
            {"label": "리스크 방어력", "pct": p6_safety, "color": "#e74c3c"}
        ]

# ==============================================================================
# 4. 사이드바 UI (Top-Down 동적 레이아웃 및 초기값 셋팅)
# ==============================================================================
with st.sidebar:
    st.title("🏮초연 시공명리 연구소")
    st.caption(f"{APP_VERSION} Master (Base + Gunghap)")
    st.markdown("---")

    with st.expander("🔍 사주팔자 역산 검색", expanded=False):
        col_g1, col_g2 = st.columns(2)
        with col_g1: ry = st.text_input("년주", value="")
        with col_g2: rm = st.text_input("월주", value="")
        col_g3, col_g4 = st.columns(2)
        with col_g3: rd = st.text_input("일주", value="")
        with col_g4: rt = st.text_input("시주", value="")
        
        K2H_GAN = {'갑':'甲','을':'乙','병':'丙','정':'丁','무':'戊','기':'己','경':'庚','신':'辛','임':'壬','계':'癸'}
        K2H_JI = {'자':'子','축':'丑','인':'寅','묘':'卯','진':'辰','사':'巳','오':'午','미':'未','신':'申','유':'酉','술':'戌','해':'亥'}
        
        if st.button("🔍 생년월일 자동입력", use_container_width=True):
            _ry, _rm, _rd = ry.replace("년","").replace(" ","")[:2], rm.replace("월","").replace(" ","")[:2], rd.replace("일","").replace(" ","")[:2]
            if len(_ry)==2 and len(_rm)==2 and len(_rd)==2:
                ry_h = K2H_GAN.get(_ry[0], _ry[0]) + K2H_JI.get(_ry[1], _ry[1])
                rm_h = K2H_GAN.get(_rm[0], _rm[0]) + K2H_JI.get(_rm[1], _rm[1])
                rd_h = K2H_GAN.get(_rd[0], _rd[0]) + K2H_JI.get(_rd[1], _rd[1])
                klc_find = KoreanLunarCalendar(); found = False
                for y in range(2026, 1899, -1):
                    klc_find.setSolarDate(y, 7, 1); gj_y = klc_find.getChineseGapJaString().split()
                    if gj_y and gj_y[0][:2] == ry_h:
                        curr_dt = dt_mod.date(y+1, 2, 28)
                        while curr_dt >= dt_mod.date(y, 1, 1):
                            klc_find.setSolarDate(curr_dt.year, curr_dt.month, curr_dt.day)
                            gj = klc_find.getChineseGapJaString().split()
                            if len(gj) >= 3 and gj[0][:2] == ry_h and gj[1][:2] == rm_h and gj[2][:2] == rd_h:
                                st.session_state.s_y, st.session_state.s_m, st.session_state.s_d = curr_dt.year, curr_dt.month, curr_dt.day
                                time_map_rev = {'子':'00:30 ~ 01:29 (朝子)시','丑':'01:30 ~ 03:29 (丑)시','寅':'03:30 ~ 05:29 (寅)시','卯':'05:30 ~ 07:29 (卯)시','辰':'07:30 ~ 09:29 (辰)시','巳':'09:30 ~ 11:29 (巳)시','午':'11:30 ~ 13:29 (午)시','未':'13:30 ~ 15:29 (未)시','申':'15:30 ~ 17:29 (申)시','酉':'17:30 ~ 19:29 (酉)시','戌':'19:30 ~ 21:29 (戌)시','亥':'21:30 ~ 23:29 (亥)시'}
                                if rt:
                                    ji_char = rt.replace("시","").replace(" ","")[-1]
                                    rt_h = K2H_JI.get(ji_char, ji_char)
                                    if rt_h in time_map_rev: st.session_state.s_t = time_map_rev[rt_h]
                                found = True
                                is_leap = getattr(klc_find, 'isIntercalary', False)
                                leap_str = "윤달" if is_leap else "평달"
                                st.success(f"✅ [양력] {curr_dt.year}년 {curr_dt.month:02d}월 {curr_dt.day:02d}일 / [음력] {klc_find.lunarYear}년 {klc_find.lunarMonth:02d}월 {klc_find.lunarDay:02d}일 ({leap_str}) 입력완료!")
                                break
                            curr_dt -= dt_mod.timedelta(days=1)
                        if found: break
                if not found: st.error("일치하는 날짜가 없습니다.")
            else: st.warning("간지를 2글자씩 정확히 입력하세요.")

    st.markdown("---")
    u_product = st.selectbox("📋 분석 상품 선택", ["개인사주", "궁합", "타 감명서"])
    
    st.markdown("<div style='font-weight:900; color:#1A237E; margin-bottom:5px;'>👤 신청인 정보 (공통)</div>", unsafe_allow_html=True)
    u_name = st.text_input("이름", value="", placeholder="홍길동", key="u_n")
    u_gender = st.selectbox("성별", ["남성", "여성"], index=0, key="u_g")
    u_marital = st.selectbox("혼인여부", ["선택", "미혼", "기혼", "돌싱"], index=1, key="u_m_stat")
    u_cal = st.selectbox("달력", ["양력", "음력(평달)", "음력(윤달)"], index=0, key="u_c")
    
    col1, col2, col3 = st.columns(3)
    u_y = col1.number_input("년", 1900, 2050, value=2010, key="s_y")
    u_m = col2.number_input("월", 1, 12, value=1, key="s_m")
    u_d = col3.number_input("일", 1, 31, value=1, key="s_d")
    
    idx_list = ["시간 모름", "00:30 ~ 01:29 (朝子)시", "01:30 ~ 03:29 (丑)시", "03:30 ~ 05:29 (寅)시", "05:30 ~ 07:29 (卯)시", "07:30 ~ 09:29 (辰)시", "09:30 ~ 11:29 (巳)시", "11:30 ~ 13:29 (午)시", "13:30 ~ 15:29 (未)시", "15:30 ~ 17:29 (申)시", "17:30 ~ 19:29 (酉)시", "19:30 ~ 21:29 (戌)시", "21:30 ~ 23:29 (亥)시", "23:30 ~ 00:29 (夜子)시"]
    u_t = st.selectbox("태어난 시간", idx_list, index=0, key="s_t")
    
    # 변수 사전 초기화 (NameError 튕김 방지용 깡통 안전장치)
    p_name, p_gender, p_marital, p_cal, p_y, p_m, p_d, p_t = "", "여성", "미혼", "양력", 0, 0, 0, "시간 모름"
    other_reading_text = ""
    run_delivery_calc = False  
    start_date, end_date = None, None
    baby_gender = "미정"

    # [조건부 UI 노출: 상품 선택에 따라 중간 삽입]
    run_iljin_calc = False # 🚨 변수 에러 방지용 초기화
    
    if u_product == "개인사주":
        st.markdown("<hr style='border:1px dashed #1A237E; margin:15px 0;'>", unsafe_allow_html=True)
        # 🚨 [수술] 일진 분석을 무조건 띄우지 않고 '옵션 체크박스'로 변경
        run_iljin_calc = st.checkbox("🔮 일진 시공간 분석 추가 가동 (선택)", value=False)
        
        if run_iljin_calc: # 체크했을 때만 날짜 선택창 노출
            if 'target_date' not in st.session_state:
                kst = pytz.timezone('Asia/Seoul')
                st.session_state['target_date'] = dt_mod.datetime.now(kst).date()
            target_iljin_date = st.date_input("분석할 일자 선택", value=st.session_state['target_date'])
            st.session_state['target_date'] = target_iljin_date

    elif u_product == "타 감명서":
        st.markdown("<hr style='border:1px dashed #2E7D32; margin:15px 0;'>", unsafe_allow_html=True)
        st.markdown("<div style='font-weight:900; color:#2E7D32; margin-bottom:5px;'>📄 타 감명서 원문 입력</div>", unsafe_allow_html=True)
        other_reading_text = st.text_area("타 감명서 원문", height=150, placeholder="여기에 내용을 붙여넣기 하세요...", key="other_reading")

    elif u_product == "궁합":
        st.markdown("<hr style='border:1px dashed #C62828; margin:15px 0;'>", unsafe_allow_html=True)
        st.markdown("<div style='font-weight:900; color:#C62828; margin-bottom:5px;'>💕 상대방 정보</div>", unsafe_allow_html=True)
        p_name = st.text_input("이름", value="", placeholder="이영희", key="p_n")
        p_gender_default = "여성" if u_gender == "남성" else "남성"
        p_gender = st.selectbox("성별", ["남성", "여성"], index=["남성", "여성"].index(p_gender_default), key="p_g")
        p_marital = st.selectbox("혼인여부", ["미혼", "기혼", "돌싱"], index=0, key="p_m_stat")
        p_cal = st.selectbox("달력", ["양력", "음력(평달)", "음력(윤달)"], index=0, key="p_c")
        
        p_col1, p_col2, p_col3 = st.columns(3)
        p_y = p_col1.number_input("년", 1900, 2050, value=2010, key="p_y_in")
        p_m = p_col2.number_input("월", 1, 12, value=1, key="p_m_in")
        p_d = p_col3.number_input("일", 1, 31, value=1, key="p_d_in")
        p_t = st.selectbox("태어난 시간", idx_list, index=0, key="p_t_key")
        
        current_year = dt_mod.datetime.now().year 
        f_year = u_y if u_gender == "여성" else p_y

        if (current_year - f_year + 1) <= 49:
            st.markdown("<hr style='border:1px solid #ddd; margin:15px 0;'>", unsafe_allow_html=True)
            
            # 🚨 [수술] 삭제가 아닌 '숨김(Hidden) 패널' 적용! 클릭 시 스르륵 열립니다.
            with st.expander("👶 출산택일 달력 선택", expanded=False):
                baby_gender = st.radio("태아 성별", ["미정", "남아", "여아"], index=0)
                start_date = st.date_input("탐색 시작일")
                end_date = st.date_input("탐색 종료일")
                
                st.markdown("<div style='margin-top:15px;'></div>", unsafe_allow_html=True)
                # 🚨 박사님께서 지시하신 '출산택일 확정 체크란'
                run_delivery_calc = st.checkbox("✅ 출산택일 확정 (체크 후 하단 메인 가동버튼 클릭)", value=False)

    st.markdown("---")
    
    # [하단 고정 UI] 가동 버튼 및 인쇄 버튼 배치
    btn_single = st.button("🚀 초연 시공명리 사주풀이 가동", use_container_width=True, type="primary")

    components.html("""
    <div style='padding: 0; margin: 0;'>
        <button id='sidebar-pdf-print-btn' style='width:100%; background-color:#2E7D32; color:white; border:none; font-weight:900; height:45px; border-radius:8px; cursor:pointer; font-size:15px; font-family:"Malgun Gothic", sans-serif; box-shadow: 0 4px 6px rgba(0,0,0,0.15);'>
            🖨️ 풀이 결과 인쇄 / PDF 저장
        </button>
        <script>
            document.getElementById('sidebar-pdf-print-btn').addEventListener('click', () => {
                window.parent.print();
            });
        </script>
    </div>
    """, height=55)

    if btn_single:
        if not u_name.strip(): 
            st.warning("⚠️ 신청인의 이름을 입력해 주세요.")
        elif u_product == "타 감명서" and not other_reading_text.strip():
            st.warning("⚠️ 타 감명서 원문을 입력해 주세요.")
        elif u_product == "궁합" and not p_name.strip(): 
            st.warning("⚠️ 상대방의 이름을 입력해 주세요.")
        else:
            st.session_state['app_running'] = True
            
            # [논리적 순서 1] 개인사주: 일진 분석만 단독 가동할 경우
            if u_product == "개인사주" and run_iljin_calc and st.session_state.get('saved_report_html'):
                st.session_state['need_calc'] = False
                st.session_state['run_waterfall'] = True
                if 'saved_report_iljin' in st.session_state: del st.session_state['saved_report_iljin']
                
            # [논리적 순서 2] 타 감명서: 무조건 전체 풀 가동 (서브 모듈 없음)
            elif u_product == "타 감명서":
                st.session_state['need_calc'] = True
                st.session_state['run_waterfall'] = False
                st.session_state['run_delivery_only'] = False
                for key in ['saved_report_html', 'saved_report_2', 'saved_report_gh_cover', 'saved_report_gh_m', 'saved_report_gh_f', 'saved_report_gh_g', 'saved_report_del', 'saved_report_iljin']:
                    if key in st.session_state: del st.session_state[key]
                    
            # [논리적 순서 3] 궁합: 택일만 단독 가동할 경우
            elif u_product == "궁합" and run_delivery_calc and st.session_state.get('saved_report_gh_g'):
                st.session_state['need_calc'] = False
                st.session_state['run_delivery_only'] = True
                if 'saved_report_del' in st.session_state: del st.session_state['saved_report_del']
                
            # [최종 예외 처리] 완전 초기화 후 전체 풀 가동 (처음 실행이거나 조건이 변경된 경우)
            else:
                st.session_state['need_calc'] = True
                st.session_state['run_waterfall'] = run_iljin_calc if u_product == "개인사주" else False 
                st.session_state['run_delivery_only'] = run_delivery_calc if u_product == "궁합" else False
                for key in ['saved_report_html', 'saved_report_2', 'saved_report_gh_cover', 'saved_report_gh_m', 'saved_report_gh_f', 'saved_report_gh_g', 'saved_report_del', 'saved_report_iljin']:
                    if key in st.session_state: del st.session_state[key]

# ==============================================================================
# 5. 분석 가동 로직 (need_calc 상태일 때만 무거운 연산 실행)
# ==============================================================================
if st.session_state.get('need_calc', False):
    spinner_msg = f"⏳ [초연 시공명리 개인 사주풀이 분석({APP_VERSION}) 중....]"
    with st.spinner(spinner_msg):
        try:
            # 1. 시스템 날짜 및 사용자 날짜 기초 변수 정의
            kst = pytz.timezone('Asia/Seoul')
            curr_dt_sys = dt_mod.datetime.now(kst)
            curr_y = curr_dt_sys.year
            curr_m = curr_dt_sys.month
            u_age = curr_y - u_y + 1
            base_dt = dt_mod.datetime(u_y, u_m, u_d, 12, 0)
            
            klc = KoreanLunarCalendar()
            if u_cal == "양력": klc.setSolarDate(u_y, u_m, u_d)
            elif u_cal == "음력(평달)": klc.setLunarDate(u_y, u_m, u_d, False)
            else: klc.setLunarDate(u_y, u_m, u_d, True)
            
            is_leap = getattr(klc, 'isIntercalary', False)
            leap_str = "윤달" if is_leap else "평달"
            sol_str = f"{klc.solarYear}년 {klc.solarMonth:02d}월 {klc.solarDay:02d}일"
            lun_str = f"{klc.lunarYear}년 {klc.lunarMonth:02d}월 {klc.lunarDay:02d}일 ({leap_str})"
            
            true_ym, true_mm, _ = get_true_year_month_pillar(u_y, u_m, u_d, 12, 0)
            ys, yb = true_ym[0], true_ym[1]
            ms, mb = true_mm[0], true_mm[1]
            
            gj = klc.getChineseGapJaString().split()
            ds, db = gj[2][0], gj[2][1]
            hs, hb = get_time_ganji(ds, u_t, base_dt)
            
            gans, jjis = [hs, ds, ms, ys], [hb, db, mb, yb]
            applicant_bazi = [f"{hs}{hb}", f"{ds}{db}", f"{ms}{mb}", f"{ys}{yb}"]

            # 폭포수 연산을 위해 세션에 저장 --> 일진(일운) 연산을 위해 세션에 저장으로 
            st.session_state['global_gans'] = gans
            st.session_state['global_jjis'] = jjis
            st.session_state['global_ds'] = ds
            st.session_state['global_db'] = db

            adj_mins = get_total_time_adjustment(base_dt)
            utc_dt = base_dt - dt_mod.timedelta(hours=9) + dt_mod.timedelta(minutes=adj_mins)
            order = 1 if (GAN.index(ys)%2==0) == (u_gender=='남성') else -1
            calc_d = get_daeun_su_accurate(utc_dt, order)
            current_daewun_age = ((u_age - calc_d) // 10) * 10 + calc_d
            
            base_y_idx = (curr_y - 1984) % 60
            curr_y_ganji = GAN[base_y_idx % 10] + JI[base_y_idx % 12]
            time_str = f" {u_t.split('(')[0].strip()} ({hb})시" if u_t != "시간 모름" else ""
            
            def td(c, size="26px"): 
                # 🚨 [수술 포인트] 밖에서 size를 뭘로 던지든 무시하고, 강제로 font-size: 26px !important; 로 콱 박아버림!
                return f"<td class='color-{get_color(c)}' style='font-size: 26px !important; font-weight: 900 !important; border: 1px solid #444 !important; padding: 5px !important; text-align: center; vertical-align: middle; width: 21.25%; line-height: 1.2 !important;'>{('?' if c in ['?',' ','-'] else c)}</td>"          
            disp_name = u_name if u_name.strip() else "홍길동"
            p_icon = "♂️" if u_gender == "남성" else "♀️"
            p_color = "#1A237E" if u_gender == "남성" else "#D50000"
            today_str = (dt_mod.datetime.utcnow() + dt_mod.timedelta(hours=9)).strftime("%Y년 %m월 %d일")

            # ------------------------------------------------------------------
            # [모드 1] 개인사주 분석: 모든 상품의 기반이 되는 공통 사주풀이 엔진 구동
            # ------------------------------------------------------------------
            if u_product in ["개인사주", "궁합", "타 감명서"]:
                past_months_html = ""

                cover_html = (
                        f"<div class='report-page cover-page' style='padding:0; margin:0; width:100%; height:297mm; display:flex; flex-direction:column; justify-content:center; align-items:center; page-break-after: always; -webkit-print-color-adjust: exact;'>\n"
                        f"    <div style='border: 4px solid #1A237E; padding: 50px 30px; border-radius: 20px; text-align: center; background: white; width: 80%; max-width: 600px; box-shadow: 0 10px 25px rgba(0,0,0,0.1); margin: auto;'>\n"
                        f"        <div style='border-bottom:4px double #1A237E; padding-bottom:20px; margin-bottom:40px;'>\n"
                        
                        # 🚨 [원상복구 & 확대!!] h1 태그와 title-gothic 클래스 부활!! 크기만 56px로 빵빵하게!!
                        f"            <h1 class='title-gothic' style='font-size: 56px !important; margin:0 !important; line-height: 1.3 !important; word-break: keep-all !important;'>초연 시공명리 사주팔자 풀이</h1>\n"
                        
                        f"            <div style='text-align: right; margin-top: 10px;'>\n"
                        f"                <span class='ver-gothic' style='font-size: 14px; letter-spacing: 1px;'>{APP_VERSION}</span>\n"
                        f"            </div>\n"
                        f"        </div>\n"
                        f"        <div style='background:#F8F9FA; border: 1px solid #E8EAF6; padding: 30px 20px; border-radius: 15px;'>\n"
                        f"            <h2 style='font-size: 24px; font-weight: 800; color: {p_color}; margin-bottom: 20px;'>{p_icon} 신청인 : {u_name} 님</h2>\n"
                        f"            <div style='font-size: 15px; font-weight: 600; color: #555; line-height: 1.8;'>\n"
                        f"                <p style='margin: 0; white-space: nowrap;'>[양력] {sol_str} | [음력] {lun_str}</p>\n"
                        f"                <p style='margin: 5px 0 0 0; color: #D50000; white-space: nowrap;'>{time_str}</p>\n"
                        f"            </div>\n"
                        f"        </div>\n"
                        f"        <p style='font-size: 18px; margin-top: 50px; font-weight: 800;'>{today_str}</p>\n"
                        f"        <p style='font-size: 22px; font-weight: 800; color: #1A237E; margin-top: 20px;'>초연 시공명리 연구소</p>\n"
                        f"    </div>\n"
                        f"</div>"
                    )
                st.session_state['saved_report_cover'] = cover_html

                # 🚨 [2. 사주 원국표 생성]
                ji_rel_rows = ""
                for l_idx, r_idx in enumerate([1, 2, 0, 3]):
                    b_bot = "1px solid #444 !important" if l_idx == 3 else "0px solid transparent !important"
                    b_top = "0px solid transparent !important"
                    cells = "".join([f"<td style='color:{('#D50000' if ci==r_idx else ('#000' if get_ji_rel_set(jjis[r_idx], jjis[ci])!='-' else '#BBB'))}; font-weight:900; border-top:{b_top}; border-bottom:{b_bot}; border-left:1px solid #444 !important; border-right:1px solid #444 !important;'>{('←('+jjis[r_idx]+')→' if ci==r_idx else get_ji_rel_set(jjis[r_idx], jjis[ci]))}</td>" for ci in range(4)])
                    lbl = f"<td rowspan='4' class='header-cell-main' style='border-right: 1px solid #444 !important; border-left: 1px solid #444 !important; border-bottom: 1px solid #444 !important; border-top: 0px solid transparent !important; font-size:14px !important;'>합충형파해</td>" if l_idx==0 else ""
                    ji_rel_rows += f"<tr style='border:none;'>{lbl}{cells}</tr>"

                info_h = f"<div style='text-align:center; font-family:\"Malgun Gothic\", sans-serif; margin-bottom:15px; line-height:1.5;'><span style='font-size:18px; font-weight:900; color:{p_color}; white-space:nowrap;'>{p_icon} {disp_name}님 ({u_gender}, {u_marital}, {u_age}세)</span><br><span style='font-size:14px; font-weight:bold; color:#555; white-space:nowrap;'>[양력: {sol_str} | 음력: {lun_str} {time_str}]</span></div>"

                table_html = f"""<div style='text-align:center; margin-bottom:10px;'>{info_h}</div>
<table class='result-table' style='width:100%; border-collapse:collapse; text-align:center;'>
<tr class='top-header-cell'>
<td style='border:1px solid #444; color:#FFFFFF !important; font-weight:900;'>구분</td>
<td style='border:1px solid #444; color:#FFFFFF !important; font-weight:900;'>시주</td>
<td style='border:1px solid #444; color:#FFFFFF !important; font-weight:900;'>일주</td>
<td style='border:1px solid #444; color:#FFFFFF !important; font-weight:900;'>월주</td>
<td style='border:1px solid #444; color:#FFFFFF !important; font-weight:900;'>년주</td>
</tr>
<tr><td class='header-cell-main' style='border:1px solid #444; background:#f5f5f5; font-weight:900; font-size:14px !important;'>천간합충</td>{"".join([f"<td style='border:1px solid #444;'>{get_gan_rel_all(i, gans)}</td>" for i in range(4)])}</tr>
<tr><td class='header-cell-main' style='border:1px solid #444; background:#f5f5f5; font-weight:900; font-size:14px !important;'>천간십성</td><td style='border:1px solid #444;'>{get_ss(ds,hs)}</td><td style='border:1px solid #444;'><span style='color:#D50000; font-weight:900;'>日元</span></td><td style='border:1px solid #444;'>{get_ss(ds,ms)}</td><td style='border:1px solid #444;'>{get_ss(ds,ys)}</td></tr>
<tr><td class='header-cell-main' style='border:1px solid #444; background:#E8EAF6; color:#1A237E; font-weight:900; font-size:24px !important;'>천간</td>{td(hs)}{td(ds)}{td(ms)}{td(ys)}</tr>
<tr><td class='header-cell-main' style='border:1px solid #444; background:#E8EAF6; color:#1A237E; font-weight:900; font-size:24px !important;'>지지</td>{td(hb)}{td(db)}{td(mb)}{td(yb)}</tr>
<tr><td class='header-cell-main' style='border:1px solid #444; background:#f5f5f5; font-weight:900; font-size:14px !important;'>지지십성</td><td style='border:1px solid #444;'>{get_ss(ds,hb)}</td><td style='border:1px solid #444;'>{get_ss(ds,db)}</td><td style='border:1px solid #444;'>{get_ss(ds,mb)}</td><td style='border:1px solid #444;'>{get_ss(ds,yb)}</td></tr>
<tr><td class='header-cell-main' style='padding:0; border:1px solid #444; background:#f5f5f5; font-weight:900; font-size:14px !important;'>지장간</td>{"".join([f"<td style='padding:0; border:1px solid #444;'>{get_jijanggan_full(ds, jjis[i])}</td>" for i in range(4)])}</tr>
{ji_rel_rows}
<tr><td class='header-cell-main' style='border:1px solid #444 !important; background:#f5f5f5; font-weight:900; font-size:14px !important;'>십이운성</td>{"".join([f"<td style='color:#0D47A1; border:1px solid #444 !important;'>{get_unsung(ds, jjis[i])}</td>" for i in range(4)])}</tr>
<tr><td class='header-cell-main' style='border:1px solid #444 !important; background:#f5f5f5; font-weight:900; font-size:14px !important;'>십이신살</td>{"".join([f"<td style='color:#C62828; border:1px solid #444 !important;'>{get_12_shinsal(yb, jjis[i])}</td>" for i in range(4)])}</tr>
<tr><td class='header-cell-main' style='border:1px solid #444 !important; background:#f5f5f5; font-weight:900; font-size:14px !important;'>일반신살</td>{"".join([f"<td style='vertical-align:top; padding:2px; border:1px solid #444 !important;'>{'<br>'.join(get_general_shinsal_filtered(i, gans, jjis, u_gender)) if get_general_shinsal_filtered(i, gans, jjis, u_gender) else '-'}</td>" for i in range(4)])}</tr>
</table>
"""
                calc_gyukgook, gyukgook_detail = get_gyukgook_detailed(ds, ys, ms, hs, mb)

                gen_shinsal_list = []
                for i in range(4):
                    raw_tags = get_general_shinsal_filtered(i, gans, jjis, u_gender)
                    for tag in raw_tags:
                        if ">" in tag and "<" in tag: gen_shinsal_list.append(tag.split('>')[1].split('<')[0])
                shinsal_str = ", ".join(list(dict.fromkeys(gen_shinsal_list))) if gen_shinsal_list else "특이 신살 없음"
                
                s12_list = [get_12_shinsal(yb, j) for j in jjis if get_12_shinsal(yb, j) != "-"]
                s12_str = ", ".join(list(dict.fromkeys(s12_list))) if s12_list else "특이 12신살 없음"
          
                samhyung_warn = ""
                has_in, has_sa, has_shin = '寅' in jjis, '巳' in jjis, '申' in jjis
                if sum([has_in, has_sa, has_shin]) == 2:
                    missing = [x for x, has in zip(['寅','巳','申'], [has_in, has_sa, has_shin]) if not has][0]
                    samhyung_warn += f"원국에 인사신 중 2글자가 있어 가형 상태입니다. 운에서 '{missing}'이 들어올 때 삼형살이 완성되니 주의 요망. "
                has_chuk, has_sul, has_mi = '丑' in jjis, '戌' in jjis, '未' in jjis
                if sum([has_chuk, has_sul, has_mi]) == 2:
                    missing = [x for x, has in zip(['丑','戌','未'], [has_chuk, has_sul, has_mi]) if not has][0]
                    samhyung_warn += f"원국에 축술미 중 2글자가 있어 가형 상태입니다. 운에서 '{missing}'이 들어올 때 삼형살이 완성되니 주의 요망. "
                if not samhyung_warn: samhyung_warn = "해당 없음"

                counts = {"목":0,"화":0,"토":0,"금":0,"수":0}
                for char in gans + jjis:
                    if char != "?": counts[get_color(char)] += 1
                
                guiin_map = {'甲':'丑, 未','乙':'子, 申','丙':'酉, 亥','丁':'酉, 亥','戊':'丑, 未','己':'子, 申','庚':'丑, 未','辛':'寅, 午','壬':'卯, 巳','癸':'卯, 巳'}
                guiin_str = guiin_map.get(ds, '없음')
                    
                direction_str = "순행" if order == 1 else "역행"
                n_gong = calculate_gongmang(ys, yb)
                i_gong = calculate_gongmang(ds, db)
                
                # 🚨 [신규 수술] 파이썬이 미리 원국의 공망 위치를 정확히 계산하여 팩트만 도출!
                gongmang_targets = n_gong.split(',') + i_gong.split(',')
                gongmang_hits = []
                if yb in gongmang_targets: gongmang_hits.append(f"년지({yb})")
                if mb in gongmang_targets: gongmang_hits.append(f"월지({mb})")
                if db in gongmang_targets: gongmang_hits.append(f"일지({db})")
                if hb in gongmang_targets: gongmang_hits.append(f"시지({hb})")
                
                gongmang_actual = ", ".join(gongmang_hits) + "에 공망 작용함" if gongmang_hits else "사주 원국 내 공망 작용 없음"
                
                cur_samjae = get_samjae(yb, curr_y_ganji[1])
                samjae_color = "#C62828" if cur_samjae != "해당 없음" else "#555"
                
                master_bar_html = f"<div style='border:2px solid #3E2723; margin-top:20px; padding:8px; display:flex; justify-content:space-between; font-weight:900; font-size:12px; border-radius:8px; white-space:nowrap;'><div>💥 오행: 木({counts['목']}) 火({counts['화']}) 土({counts['토']}) 金({counts['금']}) 水({counts['수']})</div><div>🌟 천을귀인: {guiin_str}</div><div>🎯 공망: [일] {i_gong}</div><div>🌪️ 삼재: <span style='color:{samjae_color};'>{cur_samjae}</span></div></div>"                
                
                # 🚨 [3. 대운 흐름표 생성]
                daewun_info = []
                un_html = f"<div style='margin-top:5px; margin-bottom:10px; font-size:18px; font-weight:900; color:#1A237E;'>[ 대운의 흐름 (대운수: {calc_d}, {direction_str}) ]</div><div style='display:flex; flex-direction:row-reverse; width:100%; border:2px solid #3E2723; background:white; margin-bottom:5px;'>"
                for i in range(10):
                    val, c, j = i*10+calc_d, GAN[(GAN.index(ms)+(i+1)*order)%10] if ms in GAN else "-", JI[(JI.index(mb)+(i+1)*order)%12] if mb in JI else "-"
                    daewun_info.append(f"{val}세:{c}{j}")
                    is_active = val <= u_age < val+10
                    bg_col = "#FFF9C4" if is_active else "transparent"
                    b_left = "1px solid #ccc" if i != 9 else "none"
                    un_html += f"<div style='flex:1; border-left:{b_left}; text-align:center; padding-bottom:3px; background-color:{bg_col};'><div style='background-color:#3E2723; color:#FFFFFF; font-weight:900; padding:4px 0; font-size:12px; border-bottom:1px solid #ccc;'>{val}세</div><div style='padding:2px; font-size:12px;'>{get_ss(ds,c)}</div><div class='color-{get_color(c)}' style='font-size:16px; font-weight:900;'>{c}</div><div class='color-{get_color(j)}' style='font-size:16px; font-weight:900;'>{j}</div><div style='padding:2px; font-size:12px;'>{get_ss(ds,j)}</div><div style='font-size:11px; border-top:1px solid #ccc;'>{get_unsung(ds,j)}</div><div style='font-size:11px; color:#C62828; border-top:1px solid #ccc;'>{get_12_shinsal(yb, j)}</div></div>"
                un_html += "</div>"

                cur_dw_idx = max(0, (u_age - calc_d) // 10)
                dw_g_cur = GAN[(GAN.index(ms) + (cur_dw_idx+1)*order)%10] if ms in GAN else "-"
                dw_j_cur = JI[(JI.index(mb) + (cur_dw_idx+1)*order)%12] if mb in JI else "-"
                current_daewun_age = cur_dw_idx * 10 + calc_d
                
                # 🚨 [4. 세운 흐름표 생성]
                start_year = u_y + current_daewun_age - 1
                sewun_info = []
                se_html = f"<div style='margin-top:5px; margin-bottom:10px; font-size:18px; font-weight:900; color:#1A237E;'>[ 세운의 흐름 ({dw_g_cur}{dw_j_cur}대운 기준) ]</div><div style='display:flex; flex-direction:row-reverse; width:100%; border:2px solid #3E2723; background:white; margin-bottom:5px;'>"
                for i in range(10):
                    ty = start_year + i
                    tage = current_daewun_age + i
                    base = (ty - 1984) % 60
                    tc, tj = GAN[base % 10], JI[base % 12]
                    sewun_info.append(f"{ty}년({tc}{tj})")
                    is_cur_yr = (ty == curr_y)
                    bg_col = "#E1F5FE" if is_cur_yr else "transparent"
                    b_left = "1px solid #ccc" if i != 9 else "none"
                    se_html += f"<div style='flex:1; border-left:{b_left}; text-align:center; padding-bottom:3px; background-color:{bg_col};'><div style='background-color:#3E2723; color:#FFFFFF; font-weight:900; padding:4px 0; font-size:12px; line-height:1.2; border-bottom:1px solid #ccc;'>{ty}년<br>({tage}세)</div><div style='padding:2px; font-size:12px;'>{get_ss(ds,tc)}</div><div class='color-{get_color(tc)}' style='font-size:16px; font-weight:900;'>{tc}</div><div class='color-{get_color(tj)}' style='font-size:16px; font-weight:900;'>{tj}</div><div style='padding:2px; font-size:12px;'>{get_ss(ds,tj)}</div><div style='font-size:11px; border-top:1px solid #ccc;'>{get_unsung(ds,tj)}</div><div style='font-size:11px; color:#C62828; border-top:1px solid #ccc;'>{get_12_shinsal(yb, tj)}</div></div>"
                se_html += "</div>"

                # 🚨 [5. 월운 흐름표 생성]
                wol_gans = ["己", "庚", "辛", "壬", "癸", "甲", "乙", "丙", "丁", "戊", "己", "庚"]
                wol_jis = ["丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥", "子"]
                cur_wol_g = wol_gans[curr_m - 1]
                cur_wol_j = wol_jis[curr_m - 1]
                
                wol_html = f"<div style='margin-top:5px; margin-bottom:10px; font-size:18px; font-weight:900; color:#1A237E;'>[ 월운의 흐름 ({curr_y}년도 양력기준) ]</div><div style='display:flex; flex-direction:row-reverse; width:100%; border:2px solid #3E2723; background:white; margin-bottom:5px;'>"
                for i in range(12):
                    tm, tc, tj = i + 1, wol_gans[i], wol_jis[i]
                    is_cur_m = (tm == curr_m)
                    bg_col = "#E8F5E9" if is_cur_m else "transparent"
                    b_left = "1px solid #ccc" if i != 11 else "none"
                    wol_html += f"<div style='flex:1; border-left:{b_left}; text-align:center; padding-bottom:3px; background-color:{bg_col};'><div style='background-color:#3E2723; color:#FFFFFF; font-weight:900; padding:4px 0; font-size:12px; border-bottom:1px solid #ccc;'>{tm}월</div><div style='padding:2px; font-size:12px;'>{get_ss(ds,tc)}</div><div class='color-{get_color(tc)}' style='font-size:16px; font-weight:900;'>{tc}</div><div class='color-{get_color(tj)}' style='font-size:16px; font-weight:900;'>{tj}</div><div style='padding:2px; font-size:12px;'>{get_ss(ds,tj)}</div><div style='font-size:11px; border-top:1px solid #ccc;'>{get_unsung(ds,tj)}</div><div style='font-size:11px; color:#C62828; border-top:1px solid #ccc;'>{get_12_shinsal(yb, tj)}</div></div>"
                wol_html += "</div>"
                
                # 🚨 [6. 과거 운세 요약 생성 (AI 프롬프트용)]
                past_daewun_list = []
                for idx in range(cur_dw_idx):
                    val = idx * 10 + calc_d
                    d_gan = GAN[(GAN.index(ms) + (idx + 1) * order) % 10] if ms in GAN else "-"
                    d_ji = JI[(JI.index(mb) + (idx + 1) * order) % 12] if mb in JI else "-"
                    past_daewun_list.append(f"• {val}세~{val+9}세 ({d_gan}{d_ji}대운): ")
                past_daewun_html = "\n".join(past_daewun_list) if past_daewun_list else "• (첫 대운 시기이므로 이전 대운 생략)"

                curr_dw_start_year = u_y + current_daewun_age - 1
                sewun_start_calc = min(curr_dw_start_year, curr_y - 3)
                past_sewun_list = []
                for py in range(sewun_start_calc, curr_y):
                    base = (py - 1984) % 60
                    past_sewun_list.append(f"• {py}년({GAN[base%10]}{JI[base%12]}년): ")
                past_sewun_html = "\n".join(past_sewun_list) if past_sewun_list else "• (분석할 과거 세운 없음)"

                # 🌟 [신규 장착] 24절기 및 중기(하지 등) 동적 연산 엔진
                terms_name = {1:"소한", 2:"입춘", 3:"경칩", 4:"청명", 5:"입하", 6:"망종", 7:"소서", 8:"입추", 9:"백로", 10:"한로", 11:"입동", 12:"대설"}
                
                def get_term_day(y, m):
                    # 해당 월의 절입일(일자) 추출
                    _, p1, _ = get_true_year_month_pillar(y, m, 1, 12, 0)
                    for d in range(2, 12):
                        _, pd, _ = get_true_year_month_pillar(y, m, d, 12, 0)
                        if pd != p1: return d, pd
                    return 5, p1

                # 🌟 과거 월운 (절기 기준 포맷팅)
                past_wol_list = []
                
                # 작년도 간지(예: 2025년 을사년) 자동 계산
                prev_y_idx = (curr_y - 1 - 1984) % 60
                prev_y_ganji = GAN[prev_y_idx % 10] + JI[prev_y_idx % 12]
                
                for pm in range(1, curr_m):
                    tc, tj = wol_gans[pm-1], wol_jis[pm-1]
                    s_day, _ = get_term_day(curr_y, pm)
                    next_m = pm + 1 if pm < 12 else 1
                    next_y = curr_y if pm < 12 else curr_y + 1
                    e_day, _ = get_term_day(next_y, next_m)
                    t_start = terms_name[pm]
                    t_end = terms_name[next_m]
                    
                    # 🚨 1월일 경우에만 앞에 '작년도 간지'를 강제로 붙여줌
                    year_prefix = f"{prev_y_ganji}년 " if pm == 1 else ""
                    
                    past_wol_list.append(f"• {pm}월({tc}{tj}월): ({year_prefix}{pm}월 {s_day}일 {t_start} ~ {next_m}월 {e_day-1}일 {t_end} 전)")
                
                past_months_html = "\n".join(past_wol_list) if past_wol_list else "• (올해 첫 달이므로 작년 하반기 요약): "

                # 🌟 현재 월운 (전반기/후반기 분기 로직)
                curr_term_day, curr_wol_pillar = get_term_day(curr_y, curr_m)
                next_m = curr_m + 1 if curr_m < 12 else 1
                next_y = curr_y if curr_m < 12 else curr_y + 1
                next_term_day, _ = get_term_day(next_y, next_m)
                
                curr_t_name = terms_name[curr_m]
                next_t_name = terms_name[next_m]

                # 하지가 포함된 6월의 특수 처리 (중기 '하지' 동적 연산)
                if curr_m == 6:
                    sun = ephem.Sun()
                    haji_day = 21 # 기본값
                    for d in range(20, 24):
                        dt_utc = dt_mod.datetime(curr_y, 6, d, 12, 0).astimezone(pytz.utc)
                        sun.compute(dt_utc)
                        if math.degrees(ephem.Ecliptic(sun).lon) % 360.0 >= 90.0:
                            haji_day = d
                            break
                    
                    prompt_first_half = f"▶ 이번 달 전반기 ({curr_m}월 {curr_term_day}일 {curr_t_name} ~ {curr_m}월 {haji_day-1}일 하지 전: {curr_wol_pillar})"
                    prompt_second_half = f"▶ 이번 달 후반기 ({curr_m}월 {haji_day}일 하지 ~ {next_m}월 {next_term_day-1}일 {next_t_name} 전: {curr_wol_pillar})"
                else:
                    # 6월이 아닐 경우 일반적인 절기 반분
                    mid_day = curr_term_day + 15
                    prompt_first_half = f"▶ 이번 달 전반기 ({curr_m}월 {curr_term_day}일 {curr_t_name} ~ {curr_m}월 {mid_day-1}일: {curr_wol_pillar})"
                    prompt_second_half = f"▶ 이번 달 후반기 ({curr_m}월 {mid_day}일 ~ {next_m}월 {next_term_day-1}일 {next_t_name} 전: {curr_wol_pillar})"

                # 🚨 [7. 결과 출력 HTML 조립]
                closing_html = f"""<div style='margin-top: 30px;'>
<p style='text-indent: 15px; text-align: justify; line-height: 1.8; margin-bottom: 8px;'>'사주팔자'는 태어날 때 부여받은 변하지 않는 바코드(bar-code)와 같지만, 우리가 살아가며 마주하는 스캐너(scanner)인 '운'은 늘 변화하며 흐릅니다.</p>
<p style='text-indent: 15px; text-align: justify; line-height: 1.8; margin-bottom: 8px;'>따라서 오늘의 '초연 시공명리와의 인연'이 <b>{disp_name}님</b>의 삶이라는 긴 여정에서 길을 잃지 않게 돕는 '나침반'이 되기를 진심으로 기원합니다.</p>
<p style='text-indent: 15px; text-align: justify; line-height: 1.8; margin-bottom: 15px;'>앞으로 미래에 대한 더 깊은 시공명리의 지혜와 궁금증이 있으시면 언제든 <b>'초연 시공명리 연구소'</b>의 문을 두드려 주십시오.</p>
<p style='text-indent: 15px; font-size: 16px; line-height: 1.8; font-weight: bold; margin-bottom: 0px;'>오늘 닿은 귀한 인연에 다시 한 번 감사드립니다.</p>
<div style='text-align: right; margin-top: 30px;'>
<span style='font-weight: 900; font-size: 18px; color: #1A237E;'>- 초연 시공명리 연구소 드림 -</span>
</div>
</div>"""

                # 🚨 첫 페이지의 page-break 방지를 위해 <div> 태그 속성 수정
                report_1_full_html = f"""{cover_html}
<div class='report-page' style='page-break-before: avoid;'>
<div class='vip-inset-frame' style='border:2px solid #1A237E; box-sizing: border-box; padding: 20px; border-radius:15px; margin-top: 0;'>

<h1 style='text-align:center;'>🎯[초연 시공명리 사주풀이]</h1>
{table_html}
{master_bar_html}
<div style='margin-top:20px;'>
{{full_content_clean_placeholder}}
</div>
</div>
</div>"""

                # 🚨 [8. AI 프롬프트 변수 및 조건 세팅]            
                # 🌟 [절입일 동적 계산 엔진 가동]
                jeolip_day = 5
                prev_wol_pillar = ""
                curr_wol_pillar = ""
                _, p1, _ = get_true_year_month_pillar(curr_y, curr_m, 1, 12, 0)
                for d in range(2, 12):
                    _, pd, _ = get_true_year_month_pillar(curr_y, curr_m, d, 12, 0)
                    if pd != p1:
                        jeolip_day = d
                        prev_wol_pillar = p1
                        curr_wol_pillar = pd
                        break
                if not curr_wol_pillar:
                    curr_wol_pillar = p1
                    prev_wol_pillar = p1

                base_gans_list = [hs, ds, ms, ys]
                base_jjis_list = [hb, db, mb, yb]

                won_guk_vaults = []
                for attacker in base_jjis_list:
                    won_guk_vaults.extend(check_vault_status(base_gans_list, base_jjis_list, attacker))
                won_guk_vaults = list(dict.fromkeys(won_guk_vaults)) 
                won_guk_vaults_str = ", ".join(won_guk_vaults) if won_guk_vaults else "해당 없음"

                daewun_vaults = check_vault_status(base_gans_list, base_jjis_list, dw_j_cur)
                sewun_vaults = check_vault_status(base_gans_list, base_jjis_list, curr_y_ganji[1])
                wolwun_vaults = check_vault_status(base_gans_list, base_jjis_list, cur_wol_j)

                hang_un_vaults = list(dict.fromkeys(daewun_vaults + sewun_vaults + wolwun_vaults))
                hang_un_vaults_str = ", ".join(hang_un_vaults) if hang_un_vaults else "해당 없음"

                disp_first_name = disp_name[1:] if len(disp_name) > 2 else disp_name
                
                age_prompt = ""
                if u_age < 20:
                    age_prompt = "내담자는 청소년기(10대)입니다. 학업 진학운과 부모 형제운을 최우선으로 상세히 분석하고 재물 사업운은 축소하십시오."
                elif 20 <= u_age < 40:
                    age_prompt = "내담자는 청년기(20~30대) MZ세대입니다. 고리타분한 명리 용어를 버리고 직업은 '스타트업, 프리랜서, 워라밸, 퍼스널 브랜딩', 연애는 '소개팅, 썸, 연인 간의 소통' 등 2030 청년들이 100% 공감할 수 있는 세련되고 트렌디한 어휘로 통변하십시오."
                elif 40 <= u_age < 60:
                    age_prompt = "내담자는 중장년기(40~50대)입니다. 재성운과 관직 명예운에 집중하여 현실적인 자산 관리와 사회적 성취를 중심으로 서술하십시오."
                else:
                    age_prompt = "내담자는 노년기(60대 이상)입니다. 건강운 및 심리적 평안, 노후 자산 안정을 최우선으로 깊이 다루십시오."

                gender_prompt = ""
                if u_gender == "남성":
                    gender_prompt = "남성 내담자입니다. 배우자운(재성)과 자식운(관성)을 남명 이론에 입각하여 해석하십시오."
                else:
                    gender_prompt = "여성 내담자입니다. 배우자운(관성)과 자식운(식상)을 여명 이론에 입각하여 해석하십시오."

                w_key = f"{ms}{mb}".strip()
                i_key = f"{ds}{db}".strip()

                w_val = choyeon_db.get("wolryeong", {}).get(w_key, f"[{w_key}] 시공간 데이터 없음")
                i_val = choyeon_db.get("ilju", {}).get(i_key, f"[{i_key}] 성품 데이터 없음")
                struct_data = choyeon_db.get("ilju_structure", {}).get(i_key, ["구조 미상", "유형 미상", "성향 미상"])
                s_name, s_type, s_desc = struct_data[0], struct_data[1], struct_data[2]

                choyeon_golden_text = f"""
<div style='font-family: "Nanum Myeongjo", "바탕체", Batang, serif; font-size: 15px; line-height: 1.8; color: #000000; margin-bottom: 20px;'>
    <p style='text-indent: 15px; margin-bottom: 5px;'>
        <b>{disp_name}님</b>은 '{w_val}'의 시공간에서, '{i_val}'의 성품을 가지고 태어나셨습니다.
    </p>
</div>
"""
                dw_start_age = current_daewun_age
                dw_mid_age   = current_daewun_age + 4
                dw_mid2_age  = current_daewun_age + 5
                dw_end_age   = current_daewun_age + 9
                                
                db_header = (
                    f"[시스템 강제 시간 인식: 현재 시점은 {curr_y}년 {curr_m}월 입니다.]\n"
                    "당신은 명리심리상담사 1급 자격을 갖춘 초연 박사입니다. \n"
                    f"- 내담자 성함: {disp_name}\n"
                    f"- 나이 / 성별: {u_age}세 / {u_gender}\n"
                    f"- marital_status: {u_marital}\n"
                    f"- 타고난 심리 구조 팩트: {s_name} ({s_type} - {s_desc})\n"
                    f"- 실제 타격받는 공망 궁위 팩트: {gongmang_actual}\n"
                    f"- 올해({curr_y}년) 삼재 여부: {cur_samjae}\n"  
                    f"- 원국 내부 묘고(입고/개고) 작용: {won_guk_vaults_str}\n"
                    f"- 현재 행운(대/세/월운) 외부 충격에 의한 묘고 작용: {hang_un_vaults_str}\n"
                    f"🚨 [AI 환각 및 UI 파괴 원천 차단 절대 규칙]\n"
                    f"1. 서론 철저 금지: '안녕하십니까', '기쁩니다' 등의 인사말이나 감성적인 도입부를 절대로 작성하지 마십시오.\n"
                    f"2. 호칭 절대 규칙: 각 대목차의 첫 문장은 반드시 '{disp_name}님은~'으로 격식있게 시작하고, 그 이후 본문에서는 친근하게 '{disp_first_name}님은~'으로 부르십시오.\n"
                    f"3. 🚨 공망 소설 금지: 위 '실제 타격받는 공망 궁위 팩트'에 명시된 자리만 공망으로 해석하십시오. 명시되지 않은 자리(예: 일지가 없는데 일지 공망이라고 하는 등)가 비어있다고 소설을 쓰면 즉시 치명적 시스템 오류로 간주합니다!\n"
                    f"4. 괄호 병기 금지: 에세이 작성 시 전문 용어나 한자를 괄호 안에 병기하는 행위를 금지합니다.\n"
                    f"5. HTML 훼손 금지: </div> 태그를 임의로 닫거나 마크다운 기호를 남발하지 마십시오.\n"
                )

                if u_gender == '남성':
                    yukchin_rule = f"""
🚨 [육친 통변 특수부대 절대 규칙 (남성용)]: 
- 본 내담자는 남성(현재 상태: {u_marital})입니다. 아래의 명리학적 육친 생극제화 및 대체 규칙을 100% 엄수하십시오.
1. 👨‍👩‍👦 [핵심 가족]: 
   - 아내(부인) = 정재 (정재가 없으면 편재로 대체)
   - 애인(여친) = 편재 (편재가 없으면 정재로 대체)
   - 자녀 = 관성(정관/편관) 🚨(경고: 남명에서 '식상'을 자녀로 풀이하는 즉시 치명적 오류로 간주함!)
2. 👵👴 [부모 및 조부모]: 
   - 아버지 = 편재 (없으면 정재) / 어머니 = 정인 (없으면 편인)
   - 조부(할아버지) = 편인 / 조모(할머니) = 상관
3. 🏠 [처가 및 형제]: 
   - 장모(처가) = 식상 (아내를 생하는 기운)
   - 동성 형제(형/남동생) = 비견 / 이성 형제(누나/여동생) = 겁재
4. 🚨 [상태별 호칭 맞춤형 타겟팅]: 내담자의 현재 혼인 상태({u_marital})를 반드시 반영하십시오. 
   - 기혼: '현재 아내/배우자'로 칭할 것.
   - 미혼: '미래의 아내/인연'으로 칭할 것.
   - 🚨돌싱(이혼/사별): '과거의 인연(전처)'에 대한 성찰이나 '새로운 인연(재혼운)'으로 변환하여 카운슬링할 것.
"""
                else:
                    yukchin_rule = f"""
🚨 [육친 통변 특수부대 절대 규칙 (여성용)]: 
- 본 내담자는 여성(현재 상태: {u_marital})입니다. 아래의 명리학적 육친 생극제화 및 대체 규칙을 100% 엄수하십시오.
1. 👩‍❤️‍👨 [핵심 가족]: 
   - 남편 = 정관 (정관이 없으면 편관으로 대체)
   - 애인(남친) = 편관 (편관이 없으면 정관으로 대체)
   - 자녀 = 식상(식신/상관) 🚨(경고: 여명에서 '관성'을 자녀로 풀이하는 즉시 치명적 오류로 간주함!)
2. 👵👴 [부모 및 조부모]: 
   - 아버지 = 편재 (없으면 정재) / 어머니 = 정인 (없으면 편인)
   - 조부(외할아버지) = 편인 / 조모(외할머니) = 상관
3. 🏠 [시댁 및 자매]: 
   - 시어머니(시댁) = 재성 (남편을 생하는 기운)
   - 동성 형제(언니/여동생) = 비견 / 이성 형제(오빠/남동생) = 겁재
4. 🚨 [상태별 호칭 맞춤형 타겟팅]: 내담자의 현재 혼인 상태({u_marital})를 반드시 반영하십시오. 
   - 기혼: '현재 남편/배우자'로 칭할 것.
   - 미혼: '미래의 남편/인연'으로 칭할 것.
   - 🚨돌싱(이혼/사별): '과거의 인연(전 남편)'에 대한 성찰이나 '새로운 인연(재혼운)'으로 변환하여 카운슬링할 것.
"""
                che_yong_matrix_text = """
[초연 시공명리 체/용(體/用) 운세 분석 키워드 매트릭스]
- 체(비겁)+용(비겁): 식상발흥, 직무개척, 건강호조, 출산운, 처가와 유정
- 체(비겁)+용(식상): 업무원만, 진취력, 건강호조, 원행, 발표, 여행
- 체(비겁)+용(재성): 손재, 소비, 이성난, 가정불화, 부친반목
- 체(비겁)+용(관성): 설화, 관재, 가족불화, 직장문제, 공명심
- 체(비겁)+용(인성): 의식주안정, 스카우트, 계약, 학업순성, 합격, 가정화목
- 체(식상)+용(비겁): 사업원만, 결과만족, 명진, 의기투합, 긍정심
- 체(식상)+용(식상): 재성발흥, 재적성취, 이성운, 가정원만, 재물입고, 환대
- 체(식상)+용(재성): 이재순성, 사업원만, 인연, 가족화목, 건강, 횡재
- 체(식상)+용(관성): 건강악화, 직업불안, 직주이동, 관재, 설화, 가족불화
- 체(식상)+용(인성): 직업불안, 건강문제, 계약파기, 학문불안, 의식주 불안
- 체(재성)+용(비겁): 일득삼재, 손재, 부부갈등, 과소비, 업무지연
- 체(재성)+용(식상): 여행, 결과만족, 횡재수, 가정화목, 득자운
- 체(재성)+용(재성): 관성발흥, 직업운 상승, 이성운 순성, 가정원만
- 체(재성)+용(관성): 신분상승, 출마, 천거, 장기출장, 가정화목, 이성운
- 체(재성)+용(인성): 매사불성, 소비지출, 가족불화, 계약파기, 손재, 흉사
- 체(관성)+용(비겁): 업무지연, 관재, 설화, 다툼, 허언, 선민의식
- 체(관성)+용(식상): 명예훼손, 직업이동, 질책, 가족불화, 이성난
- 체(관성)+용(재성): 사업운 원만, 이성운 순성, 가정원만, 취업, 명예
- 체(관성)+용(인성): 인성발흥, 승진승급, 계약성사, 자식운 원만
- 체(인성)+용(비겁): 건강호조, 학업원만, 신분상승, 당선, 명예, 안정
- 체(인성)+용(식상): 불안정, 계약파기, 학업불성, 구설, 육친흉사, 자식불효
- 체(인성)+용(재성): 지출, 탈재, 파재, 사기수, 손재, 분주다망, 시성종패
- 체(인성)+용(관성): 업무원활, 학업성취, 승진승급, 영전, 합격, 포상
- 체(인성)+용(인성): 비겁발흥, 명예, 명진, 칭찬, 주체성 확립, 학문성취
"""
                prompt = f"""
{db_header}

[ 🚨종합 특별지시 사항 : 대중을 위한 현대적 통변 원칙]
(※ AI 지시: AI는 전체 에세이 작성 시 아래 원칙을 반드시 뼛속 깊이 새기고 준수하십시오.)
1. 🚨명리 용어의 전략적 노출 및 해제: 격국, 비견, 십이운성, 신살, 형충파해 등 딱딱한 한자어 전문 용어의 단순 남발을 엄격히 금지합니다. 단, 내담자의 직업 적성이나 특이 심리를 분석할 때는 "사회생활에서 조정해야 할 일이 발생하는데, 
이는 명리학적으로 寅·巳 형(刑)의 에너지가 작용하기 때문입니다"와 같이 핵심 용어를 먼저 제시한 후 그 의미를 부드럽게 풀어 설명하여 통변의 전문성과 신뢰도를 높이십시오.
2. 직관적인 쉬운 해설: 부득이하게 명리 용어를 언급해야 할 경우, 반드시 일반인이 단번에 이해할 수 있는 일상적인 비유와 현대적 구어체로 부드럽게 풀어서 설명하십시오. 
3. 따뜻한 상담가 마인드: 명리학 강의를 하듯 가르치려 들지 말고, 내담자의 삶을 깊이 이해하고 어루만져 주는 친절하고 세련된 카운슬러의 어조(현대적 구어체)로 모든 글을 전개하십시오.
4. 🚨[절대 성역]: 단, 2. 사주팔자 구조 분석에 주입되는 '[CHOYEON_GOLDEN_TEXT_HERE]' 문장은 초연 박사의 고유 선언문입니다. 부연 설명이나 인사말 없이 원문 그대로 출력하십시오.
5. 🚨 초연 시공명리 3대 관점의 입체적 풀이: 사주를 단편적으로 해석하지 마십시오. 모든 통변을 전개할 때는 반드시 1) 육친적, 2) 심리적, 3) 사회적 관점이라는 세 가지 차원을 유기적으로 융합하십시오.
6. 🚨 [모순 요소의 변증법적 통합]: 사주 내에 상충되는 기운(예: '무관성'의 자유로움과 '정재격'의 통제력)이 발견될 경우, 이를 분리하여 서술하지 말고 모순을 입체적인 하나의 서사로 융합하여 서술하십시오. 또한, 천간에 드러나지 않았으나 지장간에 중요한 역할을 하는 육친(예: 숨겨진 정관)의 작용력을 반드시 찾아내어 내담자의 무의식적 욕구와 현실의 괴리를 깊이 있게 분석하십시오.
7. 🚨 [공망(空亡)의 양가적 심리 분석 강화]: 공망을 해석할 때, '기존의 틀을 깨는 독특한 방식의 성공'이라는 긍정적 측면뿐만 아니라, 그 이면에 필연적으로 수반되는 '심리적 공허감'과 '인간관계에서의 거리감' 등 내담자가 겪어왔을 부정적 감정까지 깊이 있게 다루어 복합적인 내면을 따뜻하게 어루만지십시오.
8. 🚨 [조후(調候)의 입체적 해석]: 조후(온도와 습도)의 불균형을 설명할 때, '우울감, 무기력, 신체 냉증, 조급함' 등 고전 명리에서 지적하는 원초적이고 생리적인 현상을 먼저 명확히 짚어주십시오. 그 후, 이를 '에너지 소모 관리'나 '심리적 재충전' 같은 현대적 개운법으로 부드럽게 전환하여 서술함으로써 통변의 깊이와 권위를 더하십시오.
9. 🚨 [고전적 숙명론의 현대적 치환]: '남편 복(덕)', '부모 덕', '자식 운' 등 내담자가 내심 궁금해하지만 상처받기 쉬운 고전적·숙명론적 주제를 무조건 회피하지 마십시오. 반드시 "과거 전통 명리에서는 이를 ~라고 단편적으로 해석했으나, 현대 사회에서는 오히려 이를 ~한 강력한 독립심이나 특수한 사회적 관계로 발현되는 것으로 봅니다"라는 '비교 재해석 프레임'을 사용하여 내담자의 궁금증을 해소함과 동시에 주체성을 극대화하십시오.
10. 🚨 [궁성(宮星) 이론 기반의 현실적 고충 직면]: 사주의 구조적 갈등(예: 형충파해)을 단순히 '성장의 동력'이나 '창조적 파괴' 등 추상적이고 긍정적인 심리 용어로만 포장하지 마십시오. 반드시 충돌이 일어난 '궁(자리: 부모궁, 배우자궁 등)'을 팩트로 짚어, "부모의 경제적 지원 부족으로 인한 이른 독립"이나 "배우자와의 관계 설정 어려움" 등 내담자가 겪었을 '뼈아픈 현실적 고충과 사건'을 먼저 구체적으로 묘사하여 깊은 현실 공감대를 형성한 후, 이를 성장의 동력으로 승화시키십시오.
11. 🚨 [결핍 오행(無字)의 대체 생존 전략 명시]: 사주 원국에 특정 오행이나 십성(예: 식상, 관성 등)이 아예 없는 결핍 상태인 경우, 단순히 '~가 없다'고 단정 짓거나 뭉뚱그리지 마십시오. 해당 기운의 부재가 행동 패턴에 미치는 영향을 명시하고, "식상이 없기 때문에 외부로 자신을 표출하기보다는, 본인 사주의 가장 강한 인성(印星)을 무기 삼아 끈기와 성실함으로 성취를 이루는 전략을 쓴다"는 식으로 결핍을 극복하기 위한 '대체 생존 전략'을 논리적으로 서술하십시오.
12. 🚨 [전통 신살 및 12운성의 전략적 앵커링]: 내담자의 특수한 성향(종교적, 예술적, 특정 직업군 등)이나 현상을 설명할 때, 막연한 심리 분석으로 바로 들어가지 마십시오. 원국에 존재하는 '천문성(天文星)', '목욕지(沐浴地)', '백호살' 등의 구체적인 고전 명리 키워드를 먼저 '앵커(닻)'처럼 명시하십시오. 그 후 "이는 현대 심리학적 관점에서 ~한 에너지로 발현됩니다"라고 재해석하여, 전문적 지식과 심리적 깊이를 동시에 충족시키십시오.
13. 🚨 [단편적 해석과 구조적 해석의 비교 화법]: 특정 흉사나 삶의 갈등(예: 배우자 불화, 금전 손실 등)을 분석할 때, "전통 명리에서는 이를 단순히 ~살이나 ~지의 작용으로 보기도 하나, 시공명리의 관점에서는 보다 근본적인 원인을 ~한 구조적 공망과 시공간의 역동성에서 찾습니다"라는 화법을 구사하십시오. 이를 통해 단편적인 현상 위주의 해석을 넘어, 내담자에게 삶의 근본적인 원인과 구조적 맥락을 객관적이고 담담하게 설명하십시오.
14. 🚨 [앵무새 반복 서술 절대 금지]: '월지 공망'이나 특정 '형충파해' 같은 명리적 원인을 매 문단마다 기계적으로 반복해서 언급하지 마십시오. 원인은 초반에 한두 번만 짚어주고, 이후에는 그로 인해 파생되는 현상과 현실적 조언 위주로 문장을 다채롭게 전개하십시오.
15. 🚨 [HTML 오타 엄중 경고]: HTML 태그 작성 시 절대로 오타(예: classt)를 내지 마십시오. 제공된 <span class='sub-title'...> 양식을 토씨 하나 틀리지 말고 그대로 복사해서 사용하십시오.

[문단 통제 명령 ]
1. 모든 통변 에세이 문장은 반드시 <p style='text-indent: 1em;'> 태그로 감싸십시오.
2. 🚨 [계층별 글자 크기 및 상하 간격 강제 규격화] 토씨 하나 틀리지 말고 적용하십시오!
   [지시 3-1] '1), 2)' 형태의 부목차는 20px 크기 적용:
   <span class='sub-title' style='display: block; font-size: 20px; font-weight: 900; color: #111; line-height: 1.4; margin-top: 35px; margin-bottom: 5px;'>1) 겉으로 드러난 성격</span>
   [지시 3-2] '▶, ▷, ◈, •' 형태의 세부 소목차는 18px 크기 적용:
   <span class='sub-title' style='display: block; font-size: 18px; font-weight: 900; color: #111; line-height: 1.4; margin-top: 25px; margin-bottom: 5px;'>▶ 현재 대운 상세 분석 ({dw_mid2_age}세~{dw_end_age}세)</span>
3. 표(Table) 생성 절대 금지. 운의 흐름 연도별 분석은 반드시 도트 기호(•)를 사용한 텍스트로 작성하십시오.
4. 🚨 [출력 레이아웃 절대 규칙] 각 분석(전반기, 후반기 등) 내용 작성 시, 문단이 바뀌더라도 문단과 문단 사이에 '빈 줄(공백 줄)'을 절대 넣지 마십시오. 엔터키(줄바꿈)는 단 한 번만 사용하여 글이 빈틈없이 빽빽하게 이어지도록 출력하십시오. (HTML 태그 사용 시 <br><br> 금지, <br>만 단일 사용)

🚨 [AI 환각(Hallucination) 방지 및 가독성 극대화 절대 규칙] (※ 신규 추가 구역)
1. 🚨 [근묘화실 위치 조작 절대 금지]: 내담자의 사주 원국(년주, 월주, 일주, 시주)에 배속된 천간과 지지의 위치를 절대로 뒤섞거나 혼동하지 마십시오. 
   (예: 시지에 있는 글자를 년지에 있다고 하거나, 원국에 없는 글자를 끌어와 합충파해를 조작하는 행위). 
   반드시 시스템이 제공한 위치 팩트 그대로만 철저하게 통변하십시오.
2. 🚨 없는 기운 창조 금지: 사주 원국에 없는 기운(예: 팩트에 없는 공망 등)을 임의로 지어내어 통변하는 것을 엄격히 금지합니다.
3. 🚨 명리 용어 시각적 강조: 통변 중 핵심 명리 용어(십성, 운성, 신살 등)를 기재할 때는 반드시 단일 인용부호(' ')나 괄호( )를 사용하여 가독성을 높이십시오.
4. 🚨 답답한 문단 해소 및 기본 들여쓰기 엄수: 하나의 거대한 문단으로 뭉쳐서 출력하지 마십시오. 
   문맥이 전환될 때는 적절히 줄바꿈을 하여 문단을 분리하고, 새로운 문단이 시작될 때는 초등학교 원고지 쓰기의 기본 원칙처럼 예외 없이 첫 줄을 들여쓰기 하십시오.

[내담자 맞춤형 정밀 타겟팅]
- {age_prompt}
- {gender_prompt}
- {yukchin_rule}

[통변 지시]
- 간지 표기 시 반드시 한자로 표기하십시오.
- 격국 팩트: {gyukgook_detail}
- 공망 팩트: {gongmang_actual} (🚨명시되지 않은 위치의 공망 환각 절대 금지)
- 일반신살: {shinsal_str} / 12신살: {s12_str}
- 입고/개고 팩트: 사주팔자의 역동적 관계 분석에 반드시 묘고 작용을 포함하십시오.

<h3 style='color:#1A237E; font-size: 24px; font-weight: 900;'>1. 성격</h3>
<div class='content-box-loose'>
<span class='sub-title' style='font-size: 18px; font-weight: 900; color: #111;'>1) 겉으로 드러난 성격</span>
(※ 🚨AI 절대 준수 규칙: 일간과 일지의 십성(十星), 십이운성(十二運星), 그리고 배정된 십이신살의 에너지 강약을 바탕으로 표면적인 성격과 기질을 구체적이고 현대적인 구어체 에세이로 작성하십시오. 통변 전개 시 다음의 2대 조건을 반드시 결합하여 서술해야 합니다.

1. [일지 지장간 좌법(座法) 해부]: 일지 지장간 내부에 내장된 천간 성분들이 해당 왕궁(王宮) 내부에서 가지는 십이운성 리듬, 즉 **좌법(座法)**을 기준으로 분석하십시오. 이를 통해 내담자가 외부 사회와 상호작용할 때 꺼내 쓰는 페르소나와 현실적 행동 메커니즘을 냉철한 팩트 기반으로 도출하십시오.
2. [배우자궁(일지)의 3대 관점 풀이]: 일지는 내담자의 가장 내밀한 안방이자 배우자 영역입니다. 이곳의 기운이 실제 사생활에서 어떻게 발현되는지 1) 육친적 관점, 2) 심리적 관점, 3) 사회적 관점이라는 3대 입체적 시각을 유기적으로 융합하여 상세히 풀어내십시오.
🚨 [용어 표기 절대 규칙]: 모든 전문 명리 용어(예: 간여지동, 음인, 장성살 등)는 절대로 전면에 노출하지 마십시오. 현대적인 구어체로 현실 현상을 먼저 쉽게 풀이한 뒤, 문장 끝에 간단한 설명과 함께 괄호 `()` 안에만 기재해야 합니다.)
   
<span class='sub-title' style='font-size: 18px; font-weight: 900; color: #111;'>2) 감추어진 내 속마음</span>
(※ 🚨AI 절대 연산 규칙: 감상적인 위로나 뜬구름 잡는 문학적 묘사를 엄격히 금지하며, 철저히 **인종법(引從法)**과 **육친·오행 공망의 현실적 조건**이라는 2대 명리적 팩트 연산에만 기반하여 내담자의 무의식 세계를 타격하십시오.

1. [인종법(引從法)을 통한 무의식 추적]: 사주 원국 지장간에 드러나지 않은 천간 오행들을 일지로 인종(引從)하여 포태법 상태를 계산하십시오. 겉으로 드러나지 않았기에 내담자가 무의식 깊은 곳에서 갈망하거나 심리적으로 취약할 수 있는 본질적 정신 영역을 현대 심리학 관점의 구어체로 분석하십시오.
2. [공망(空亡)의 물리적 제약 타격]: 공망을 단순한 심리적 쓸쓸함이나 외로움으로 뭉개지 마십시오. 공망이 걸린 오행과 육친이 실제 생활 환경에서 어떤 구체적인 공백, 결핍, 궤도 수정을 유발하는지 환경적 한계 조건을 날카로운 팩트로 기술하십시오. (예: 비겁 공망에 따른 자력갱생 노선, 관성 공망에 따른 규격화된 조직 이탈 및 특수 전문 영역 추구 등))
</div>

<h3 style='color:#1A237E; font-size: 24px; font-weight: 900;'>2. 사주팔자 구조 분석</h3>
<div class='content-box-loose'>
[CHOYEON_GOLDEN_TEXT_HERE]

<span class='sub-title' style='font-size: 18px; font-weight: 900; color: #111;'>1) 내 삶의 무대와 타고난 기본 성향</span>
(※ AI 지시: 내담자의 사주구조(격국: {gyukgook_detail})를 반드시 핵심 뼈대로 삼아 에세이를 작성하십시오. 이 격국의 특성이 어떤 시기에, 어느 정도 규모의 무대에서 어떻게 발현되는지 구체적으로 조언하십시오.)

<span class='sub-title' style='font-size: 18px; font-weight: 900; color: #111;'>2) 내 삶의 리듬과 에너지 균형</span>
(※ AI 지시: 사주팔자 오행의 분포와 계절적 조후, 억부의 균형 상태를 분석하고 삶에서 어떤 에너지를 추구해야 하는지 상세한 에세이를 작성하십시오.)

<span class='sub-title' style='font-size: 18px; font-weight: 900; color: #111;'>3) 내 삶의 역동성과 상호작용</span>
(※ 🚨AI 절대 가중치 지시: 이 구역은 전체 감명서의 성패를 가르는 가장 중요한 심장부입니다. 기계적인 용어 나열이나 단순한 길흉 판단을 엄격히 금지하며, 다음의 4대 연산 규칙을 바탕으로 타 영역보다 최소 1.5배 이상의 압도적인 분량과 밀도로 서술하십시오.
1. [천간·지지의 역동적 연쇄 반응]: 원국 내 천간의 합(合)과 충(沖), 지지의 형(刑)·충(沖)·파(破)·해(害) 및 삼합·방합·육합의 관계를 유기적으로 엮어내십시오. 단순히 '충이 있어서 나쁘다'가 아니라, 한 글자의 움직임이 다른 글자를 어떻게 자극하고, 그것이 내담자의 내면과 현실 삶에 어떤 나비효과를 불러일으키는지 서사적으로 추적해야 합니다.
2. [묘고(墓庫) 작용의 현미경 분석]: 박사님의 시공명리 정수인 '입고(入庫)'와 '개고(開庫)' 현상을 철저히 분석하십시오. 지지의 형충(刑沖)으로 인해 지장간 속에 숨겨져 있던 에너지가 개고되어 세상 밖으로 강력하게 튀어나오는 타이밍과 잠재력, 반대로 활성화되어 있던 글자가 창고 속으로 거두어져 수렴하는 입고의 시기를 명확히 짚어내고, 이것이 가져오는 삶의 극적인 반전과 궤도 수정을 설명하십시오.
3. [격각(隔角)의 시공간적 이탈 분석]: 지지가 한 칸을 건너뛰어 에너지가 어긋나는 격각(隔角) 구조를 정밀하게 포착하십시오. 정면충돌인 충(沖)과는 다르게, 조용히 가야 할 궤도를 이탈하면서 발생하는 물리적 이동과 분리(이사, 유학, 이직, 독립, 주말부부 등)의 역동성뿐만 아니라, 한 공간에 있으도 마음의 방향이 달라 생기는 심리적 소외감(동상이몽, 고독)까지 입체적으로 엮어 따뜻하게 풀어내야 합니다.
4. [드라마틱한 상담학적 에세이]: 차갑고 딱딱한 감정서 느낌을 배제하고, 내담자의 삶이라는 무대 위에서 간지(干支)들이 벌이는 치열한 상호작용을 한 편의 몰입감 넘치는 드라마처럼 구어체 심리상담 에세이로 풀어내십시오. 위기와 갈등의 원인을 정확히 인지시키되, 이를 지혜롭게 우회하고 다스릴 수 있는 개운(開運)의 힌트를 반드시 함께 제공하십시오.)

<span class='sub-title' style='font-size: 18px; font-weight: 900; color: #111;'>4) 내 삶의 숨겨진 강점과 잠재적 에너지</span>
(※ AI 지시: 제공된 12신살({s12_str})과 일반신살({shinsal_str}), 그리고 삼재 정보({cur_samjae}) 등을 유기적으로 분석하여 내담자가 가진 고유한 강점과 주의해야 할 타이밍을 설명하십시오. 🚨단, 전통 명리의 길흉화복이나 살(煞)의 공포를 조장하지 말고, 현대 심리상담 관점에서 부드러운 에세이로 풀어내십시오.)
</div>

<h3 style='color:#1A237E; font-size: 24px; font-weight: 900;'>3. 부모·형제운</h3><div class='content-box-loose'>
(※ AI 지시: 사주 원국의 연주·월주 및 인성과 비겁의 상태를 분석하여 에세이를 작성하십시오. 
1) 육친적으로 부모·형제와의 정서적 유대감과 덕의 유무를 살피고, 
2) 심리적으로 이들이 내담자 내면의 자양분 혹은 결핍에 미친 영향을 진단하며, 
3) 사회적으로 유년기 환경이 삶의 기반에 어떤 작용을 했는지 현대적 구어체로 친절하게 풀어내십시오.)
</div>

<h3 style='color:#1A237E; font-size: 24px; font-weight: 900;'>4. 학업·진학운</h3><div class='content-box-loose'>
(※ AI 지시: 인성과 식상의 관계, 관성의 통제력을 바탕으로 에세이를 작성하십시오. 
1) 심리적으로 지적 호기심과 집중력의 방향성을 파악하고, 
2) 육친적으로 학업 과정에서 주변 환경의 지지나 방해 요소를 보며, 
3) 사회적으로 최종 학위나 전공이 현실적인 커리어와 어떻게 연결되는지 그 성패를 이해하기 쉽게 조언하십시오.)
</div>

<h3 style='color:#1A237E; font-size: 24px; font-weight: 900;'>5. 적성·직업운</h3><div class='content-box-loose'>
(※ AI 지시: 원국의 구조와 주력 에너지를 바탕으로 에세이를 작성하십시오. 
1) 심리적으로 어떤 직무나 환경에서 가장 큰 성취감과 동기를 얻는지, 
2) 사회적으로 탄탄한 조직(직장)형 기질인지 개인 독립(전문직/사업)형 기질인지를 짚어 구체적인 직업적 방향성을 제안하고, 
3) 육친적인 대인관계 협업 스타일까지 종합하여 세련된 구어체로 작성하십시오.)
4) 🚨 [구체적 직업 물상(物象) 핀셋 도출]: 단순히 '사업', '전문직', '사무직' 등 피상적인 카테고리에 머물지 마십시오. 
원국 내 특정 글자의 충(沖), 형(刑) 또는 십성의 특이 조합(예: 巳亥충=운송/해외/유통, 형(刑) 맞은 상관=특수 교정/수리/의료 기술 등)을 근거로 삼아, 내담자가 머릿속에 구체적으로 그릴 수 있는 매우 독특하고 실질적인 직업군 예시를 핀셋처럼 짚어 제시하십시오.)
</div>

<h3 style='color:#1A237E; font-size: 24px; font-weight: 900;'>6. 결혼·자녀운</h3><div class='content-box-loose'>
(※ AI 지시: 일지와 시주, 재성/관성 및 식상의 동태를 분석하여 에세이를 작성하십시오. 
1) 육친적으로 배우자 및 자녀 인연의 깊이와 형태를 살피되, 배우자 성(별)이 시주에 있다고 해서 무조건 '늦게 만난다'고 한정 짓지 말고 평생을 함께하는 든든한 동반자의 관점에서 유연하게 서술하십시오. 
2) 심리적으로 내담자가 내면에서 바라는 이상적인 가정상과 정서적 정착 과정을 진단하며, 
3) 사회적으로 가정을 꾸리는 것이 현실적 삶의 안정도에 미치는 변화를 카운슬러의 어조로 따뜻하게 서술하십시오.)
</div>

<h3 style='color:#1A237E; font-size: 24px; font-weight: 900;'>7. 재성운</h3><div class='content-box-loose'>
(※ AI 지시: 재성의 유무와 상태, 식상의 생조 여부를 파악하여 에세이를 작성하십시오. 
1) 심리적으로 돈과 물질을 대하는 가치관과 집착도를 진단하여 내담자 성향에 맞는 '재물 관리 스타일(투자형 vs 저축형)'을 정립해 주고, 
2) 사회적으로 평생의 자산 규모와 경제적 성패의 흐름을 예측하며, 
3) 육친적으로 재물로 인해 주변 사람들과 상생하거나 갈등하는 역동성을 조언하십시오.)
</div>

<h3 style='color:#1A237E; font-size: 24px; font-weight: 900;'>8. 사업운</h3><div class='content-box-loose'>
(※ AI 지시: 식상생재의 흐름과 편재, 비겁의 조력 여부를 분석하여 에세이를 작성하십시오. 
1) 심리적으로 위험을 감수하는 도전 정신과 시장을 읽는 직관력을 진단하고, 
2) 사회적으로 독자적인 창업이나 사업체 운영의 적합성 및 규모 확장성을 예측하며, 
3) 육친적으로 동업자, 직원, 고객을 끌어당기는 대인관계 리더십의 강점과 약점을 조언하십시오.)
</div>

<h3 style='color:#1A237E; font-size: 24px; font-weight: 900;'>9. 관직·명예운</h3><div class='content-box-loose'>
(※ AI 지시: 관인상생 및 정관/편관의 상태를 바탕으로 에세이를 작성하십시오. 
1) 사회적으로 조직 내에서의 승진, 명예, 라이선스(자격증) 취득 및 감투운을 평가하고, 
2) 심리적으로 권력이나 자존심을 추구하는 욕구와 책임감의 크기를 분석하며, 
3) 육친적으로 윗사람이나 대중, 사회적 시스템으로부터 인정받는 흐름을 매끄러운 구어체로 서술하십시오.)
</div>

<h3 style='color:#1A237E; font-size: 24px; font-weight: 900;'>10. 건강운</h3><div class='content-box-loose'>
(※ AI 지시: 오행의 분포와 과다/과소, 그리고 계절적 조후의 균형 상태를 분석하여 에세이를 작성하십시오. 
1) 심리적 스트레스나 과로가 취약한 신체 기관(질환)으로 발현되는 원리를 명리적 물상과 연결하여 경고하고, 
2) 사회 활동을 건강하게 지속하기 위한 현실적인 에너지 관리법을 제시하며, 
3) 육친적 환경이 내담자의 정서적 안정과 건강에 미치는 영향까지 고려하여 친절하게 서술하십시오.)
</div>

<h3 style='color:#1A237E; font-size: 24px; font-weight: 900;'>11. 운의 흐름</h3>
<div class='content-box-loose'>
(※ 🚨AI 특수 지시: 아래의 모든 대운, 세운, 월운 분석 시 단순 십성 나열이나 학술적 명리 용어(체운, 용운, 상위십성 등) 사용을 엄격히 금지합니다. 반드시 다음 두 가지 포맷을 각각 독립된 박스(div) 안에 분리하여 풀이하십시오. AI 임의의 탭(Tab)이나 들여쓰기 공백을 절대 넣지 마십시오.)

<span class='sub-title' style='font-size: 18px; font-weight: 900; color: #111;'>1) 대운의 흐름</span>
[DAEWUN_TABLE_HERE]
(※ 🚨AI 절대 지시: 위 마커 자리에 마크다운 표(Table/Grid)를 직접 그리거나, 대운 간지를 일렬로 나열하는 행위를 엄격히 금지합니다. 마커 원문만 100% 그대로 남겨두고 즉시 아래 과거 대운 분석으로 넘어가십시오.)

<span class='sub-title' style='font-size: 18px; font-weight: 900; color: #111;'>▷ 지나온 과거 각 대운 분석</span>
{past_daewun_html}
(※ 🚨AI 절대 지시: 지나온 과거 각 대운 분석은 생략하거나 변형하지 말고 낱낱이 순서대로 나열하여 에세이로 분석하십시오. 탭(Tab)키 사용 절대 금지.)
[지나온 과거 각 대운 출력 템플릿]
• <b>OO세~OO세 (OO대운):</b> 
<div style='padding-left: 20px; margin-top: 5px;'>
    <div style='margin-bottom: 5px;'><b>1) 일반 명리 풀이:</b> (내용 상세 작성)</div>
    <div><b>2) 시공 명리 풀이:</b> (내용 상세 작성)</div>
</div>

<span class='sub-title' style='font-size: 18px; font-weight: 900; color: #111;'>▶ 현재 대운 전반기 상세 분석 ({dw_start_age}세~{dw_mid_age}세)</span>
<div style='padding-left: 20px; margin-top: 5px;'>
    <div style='margin-bottom: 5px;'><b>1) 일반 명리 풀이:</b> (내용 상세 작성)</div>
    <div><b>2) 시공 명리 풀이:</b> (내용 상세 작성)</div>
</div>

<span class='sub-title' style='font-size: 18px; font-weight: 900; color: #111;'>▶ 현재 대운 후반기 상세 분석 ({dw_mid2_age}세~{dw_end_age}세)</span>
<div style='padding-left: 20px; margin-top: 5px;'>
    <div style='margin-bottom: 5px;'><b>1) 일반 명리 풀이:</b> (내용 상세 작성)</div>
    <div><b>2) 시공 명리 풀이:</b> (내용 상세 작성)</div>
</div>

<span class='sub-title' style='font-size: 18px; font-weight: 900; color: #111;'>2) 세운의 흐름</span>
[SEWUN_TABLE_HERE]
(※ 🚨AI 절대 지시: 마크다운 표(Table) 및 간지 나열 텍스트를 직접 생성하는 것을 절대 금지합니다.)

<span class='sub-title' style='font-size: 18px; font-weight: 900; color: #111;'>▷ 지나온 과거 각 세운 분석</span>
{past_sewun_html}
[지나온 과거 각 세운 출력 템플릿]
• <b>OOOO년(OO년):</b> 
<div style='padding-left: 20px; margin-top: 5px;'>
    <div style='margin-bottom: 5px;'><b>1) 일반 명리 풀이:</b> (내용 상세 작성)</div>
    <div><b>2) 시공 명리 풀이:</b> (내용 상세 작성)</div>
</div>

<span class='sub-title' style='font-size: 18px; font-weight: 900; color: #111;'>▶ 올해 세운 전반기 상세 분석</span>
<div style='padding-left: 20px; margin-top: 5px;'>
    <div style='margin-bottom: 5px;'><b>1) 일반 명리 풀이:</b> (내용 상세 작성)</div>
    <div><b>2) 시공 명리 풀이:</b> (내용 상세 작성)</div>
</div>

<span class='sub-title' style='font-size: 18px; font-weight: 900; color: #111;'>▶ 올해 세운 후반기 상세 분석</span>
<div style='padding-left: 20px; margin-top: 5px;'>
    <div style='margin-bottom: 5px;'><b>1) 일반 명리 풀이:</b> (내용 상세 작성)</div>
    <div><b>2) 시공 명리 풀이:</b> (내용 상세 작성)</div>
</div>

<span class='sub-title' style='font-size: 18px; font-weight: 900; color: #111;'>3) 월운의 흐름</span>
[WOLWUN_TABLE_HERE]
(※ 🚨AI 절대 지시: 마크다운 표(Table) 및 간지 나열 텍스트 직접 생성 절대 금지. 마커 원문만 남기십시오.)

<span class='sub-title' style='font-size: 18px; font-weight: 900; color: #111;'>▷ 지나온 과거 각 월운 분석</span>
{past_months_html}
(※ 🚨AI 절대 지시: 파이썬 시스템이 계산하여 위에 제공한 '지나온 과거 각 월운 분석'의 월, 간지, 날짜, 절기 텍스트를 AI가 임의로 판단하여 수정하는 것을 엄격히 금지합니다! 제공된 텍스트 그대로 100% 복사하여 출력하십시오. 들여쓰기(Tab) 절대 금지.)
[지나온 과거 각 월운 출력 템플릿]
• <b>(파이썬이 제공한 월과 간지): (파이썬이 제공한 연도/날짜/절기 그대로 복사)</b> 
<div style='padding-left: 20px; margin-top: 5px;'>
    <div style='margin-bottom: 5px;'><b>1) 일반 명리 풀이:</b> (내용 상세 작성)</div>
    <div><b>2) 시공 명리 풀이:</b> (내용 상세 작성)</div>
</div>

<span class='sub-title' style='font-size: 18px; font-weight: 900; color: #111;'>{prompt_first_half}</span>
<div style='padding-left: 20px; margin-top: 5px;'>
    <div style='margin-bottom: 5px;'><b>1) 일반 명리 풀이:</b> (내용 상세 작성)</div>
    <div><b>2) 시공 명리 풀이:</b> (내용 상세 작성)</div>
</div>

<span class='sub-title' style='font-size: 18px; font-weight: 900; color: #111;'>{prompt_second_half}</span>
<div style='padding-left: 20px; margin-top: 5px;'>
    <div style='margin-bottom: 5px;'><b>1) 일반 명리 풀이:</b> (내용 상세 작성)</div>
    <div><b>2) 시공 명리 풀이:</b> (내용 상세 작성)</div>
</div>
</div>

<h3 style='color:#1A237E; font-size: 24px; font-weight: 900;'>12. 삶을 바꾸는 지혜로운 조언</h3>
<div class='content-box-loose'>
<span class='sub-title' style='font-size: 18px; font-weight: 900; color: #111;'>◈ 나를 돕는 에너지와 색상:</span>
(작성)
<span class='sub-title' style='font-size: 18px; font-weight: 900; color: #111;'>◈ 신체 밸런스와 에너지 관리:</span>
(작성)
<span class='sub-title' style='font-size: 18px; font-weight: 900; color: #111;'>◈ 공간의 흐름과 방위의 지혜:</span>
(작성)
<span class='sub-title' style='font-size: 18px; font-weight: 900; color: #111;'>◈ 재능 효율을 높이는 직업적 지혜:</span>
(작성)
<span class='sub-title' style='font-size: 18px; font-weight: 900; color: #111;'>◈ 더 나은 내일을 위한 절제의 미학:</span>
(작성)
</div>

<h3 style='color:#1A237E; font-size: 24px; font-weight: 900;'> 🎯 초연 시공명리 특별 개운 비법</h3>
<div class='content-box-loose'>
<span class='sub-title' style='font-size: 18px; font-weight: 900; color: #111;'>◈ 수호 천사의 기운 조언:</span>
(※ AI 지시: 사주원국 및 운(시간)의 흐름에 따른 천을귀인과 길신 등의 작용에 대한 상세한 에세이를 작성하시오.)

<span class='sub-title' style='font-size: 18px; font-weight: 900; color: #111;'>◈ 백년해로의 기운 조언:</span>
(※ AI 지시: 오행의 치우침, 원진, 고란살, 고신(남명), 과숙(여명) 등 이성 관계에 영향을 미치는 사주원국 및 운의 흐름을 분석하되, 전문 용어는 철저히 숨기십시오. 
이곳에서는 오직 '부부 및 연인 관계에서 발생할 수 있는 성격적/상황적 갈등 요소'와 이를 슬기롭게 극복하고 백년해로하기 위한 
'실질적이고 따뜻한 개운 비법(마음가짐, 소통 방식, 행동 요령 등)'에만 100% 초점을 맞추어 카운슬러의 어조로 작성하십시오.)

<span class='sub-title' style='font-size: 18px; font-weight: 900; color: #111;'>◈ 행운에 따른 기운 조언:</span>
(※ AI 지시: 운의 흐름에 따른 합형충파해와 진술축미의 입고와 개고, 도화(연살)/망신/역마살 작용에 따른 역동성과 재물과 대인관계 등 주의할 점에 대한 상세한 에세이를 작성하시오.)
</div>
"""
                try:
                    res = model.generate_content(prompt)
                    ai_text = "\n".join([line.lstrip() for line in res.text.split("\n")])
                    
                    # 🚨 [AI 오지랖 완벽 절단 수술] 
                    if "[CHOYEON_GOLDEN_TEXT_HERE]" in ai_text:
                        ai_text = ai_text.replace("[CHOYEON_GOLDEN_TEXT_HERE]", choyeon_golden_text)

                    un_html_clean = un_html.replace("\n", " ").replace("\r", "")
                    se_html_clean = se_html.replace("\n", " ").replace("\r", "")
                    wol_html_clean = wol_html.replace("\n", " ").replace("\r", "")

                    clean_ai_text = ai_text

                    daeoun_target = f"<div style='margin: 15px 0; overflow-x: auto;'>{un_html_clean}</div>"
                    sewun_target = f"<div style='margin: 15px 0; overflow-x: auto;'>{se_html_clean}</div>"
                    wolwun_target = f"<div style='margin: 15px 0; overflow-x: auto;'>{wol_html_clean}</div>"

                    clean_ai_text, count_d = re.subn(r'[\#\*\_\s]*\[\s*DAEWUN_TABLE_HERE\s*\][\#\*\_\s]*', daeoun_target, clean_ai_text, flags=re.IGNORECASE)
                    clean_ai_text, count_s = re.subn(r'[\#\*\_\s]*\[\s*SEWUN_TABLE_HERE\s*\][\#\*\_\s]*', sewun_target, clean_ai_text, flags=re.IGNORECASE)
                    clean_ai_text, count_w = re.subn(r'[\#\*\_\s]*\[\s*WOLWUN_TABLE_HERE\s*\][\#\*\_\s]*', wolwun_target, clean_ai_text, flags=re.IGNORECASE)

                    if count_d == 0 and "table" not in clean_ai_text.lower():
                        clean_ai_text = clean_ai_text + f"<br><br><span style='color:red; font-weight:bold;'>⚠️ (AI 표 마커 누락으로 비상 출력된 운의 흐름표)</span><br>{un_html_clean}{se_html_clean}{wol_html_clean}"

                    full_content_clean = f"<div style='font-family: \"Nanum Myeongjo\", \"바탕체\", Batang, serif; font-size: 15px; line-height: 1.8; color: #000000;'>{clean_ai_text}<br><br>{closing_html}</div>"

                    report_1_full_html = report_1_full_html.replace("{full_content_clean_placeholder}", full_content_clean)
                    
                    # 🚨 [수술 1] 생성된 최종 결과물을 세션 메모리에 영구 저장 (증발 완벽 차단!)
                    st.session_state['saved_report_html'] = report_1_full_html
                    # (st.markdown 직접 출력은 '6. 화면 출력부'가 알아서 안전하게 처리하므로 여기선 삭제합니다)
                    
                except Exception as e: 
                    st.error(f"AI 연산 오류: {e}")

            # ------------------------------------------------------------------
            # [2단계] 타 감명서 비교분석 (ver 34.1 핵심 로직 완벽 이식)
            # ------------------------------------------------------------------
            if u_product == "타 감명서":
                try:
                    # 1. 타 감명서 원본 렌더링 (ver 34.1 스타일 복원)
                    report_2_html = f"<div class='page-break-before'></div><div class='report-page'><div class='vip-inset-frame' style='border-color:#555;'><h2 style='text-align:center; color:#555; font-family:\"Malgun Gothic\", sans-serif; font-weight:900; margin-bottom:20px;'>📜 타 감명서 원문</h2><div style='font-family: \"Nanum Myeongjo\", \"바탕체\", Batang, serif; font-size: 15px; line-height: 1.8; color: #111; text-align: justify; word-break: keep-all;'>{other_reading_text.replace(chr(10), '<br>')}</div></div></div>"

                    # 2. 1:1 비교 리포트 생성 프롬프트 (ver 34.1 핵심 논리 파악 및 개선점 도출 복원)
                    comp_prompt = f"""
    당신은 명리심리상담사 '초연 박사'를 보조하는 수석 분석관입니다.
    아래 [1. 초연 사주풀이]와 [2. 타 감명서]를 엄격하게 1:1 대조 분석하십시오.

    🚨 [디자인 및 서식 절대 규칙]
    0. 🚨 [인사말 원천 차단]: 출력의 첫 글자는 반드시 <h3 style=...> 태그로 시작해야 합니다. "안녕하십니까", "보고서를 올립니다" 등의 어떠한 서론이나 인사말도 절대 허용하지 않습니다.
    1. AI 임의의 목차 서식 생성을 절대 금지합니다.
    2. 목차 제목 출력 시, 반드시 크기 22px와 하단 색상 선이 조립된 아래 명시된 태그 서식을 그대로 출력하십시오.
    3. 모든 본문 문단 작성 시, HTML 태그인 <p style='font-family: "Nanum Myeongjo", "바탕체", Batang, serif; font-size: 15px; line-height: 1.8; color: #000; text-indent: 1em; text-align: justify;'> 를 사용하여 모든 단락을 감싸십시오.

    🚨 [내용 집중 대조 규칙]
    - 타 감명서 원문을 분석하여, 타 감명서에서 '실제로 다루고 있는 내용(주제)'이 무엇인지 파악하십시오.
    - 타 감명서 원문이 초연 명리의 전체 흐름과 다를 때는, 타 감명서에서 집중적으로 다룬 **'해당 내용'**에 대해서만 초연 명리의 분석과 1:1로 깊이 있게 대조 분석하십시오.
    - 타 감명서에 언급조차 없는 내용은 억지로 분량을 채우려 하지 말고 과감히 생략하십시오.
    - 단, 비교 분석이 끝난 후 가장 마지막의 <13. 총평 및 향후 개선점> 목차는 무슨 일이 있어도 반드시 작성해야 합니다.

    [출력 목차 서식 정의]
    <h3 style='color:#1A237E; font-size: 22px; font-weight: 900; border-bottom: 2px solid #1A237E; padding-bottom: 5px; margin-top: 25px; margin-bottom: 8px; display:block;'>1. 사주팔자 구조 및 성격 대조 분석</h3>
    (타 감명서의 핵심 논리 기준, 해당 주제에 대한 초연 명리와의 1:1 대조 서술)
    
    ... (타 감명서가 다룬 핵심 내용들에 대해서만 이 형식의 h3 목차를 활용하여 순서대로 전개) ...
    
    <h3 style='color:#D50000; font-size: 22px; font-weight: 900; border-bottom: 2px solid #D50000; padding-bottom: 5px; margin-top: 35px; margin-bottom: 8px; display:block;'>13. 총평 및 향후 개선점</h3>
    <span class='sub-title' style='display: block; font-size: 18px; font-weight: 900; color: #111; margin-top: 15px; margin-bottom: 8px;'>1) 두 감명서의 장점과 단점</span>
    <p style='font-family: "Nanum Myeongjo", "바탕체", Batang, serif; font-size: 15px; line-height: 1.8; color: #000; text-indent: 1em; text-align: justify;'>[양측의 통변 기술, 논리적 근거, 내담자 공감력 등을 객관적으로 비교 서술]</p>
    <span class='sub-title' style='display: block; font-size: 18px; font-weight: 900; color: #111; margin-top: 15px; margin-bottom: 8px;'>2) 초연 시공명리의 누락 및 개선점 (AI 학습 피드백)</span>
    <p style='font-family: "Nanum Myeongjo", "바탕체", Batang, serif; font-size: 15px; line-height: 1.8; color: #000; text-indent: 1em; text-align: justify;'>[타 감명서를 통해 초연 명리가 벤치마킹하거나 보완해야 할 통변 기법, 누락된 내용, 관점의 차이 등을 날카롭게 분석하여 향후 AI 엔진 업그레이드에 활용할 수 있도록 명확히 제시]</p>

    [데이터]
    1. 초연 사주풀이: {full_content_clean}
    2. 타 감명서: {other_reading_text}
    """
                    c_res = call_claude_api(comp_prompt, max_tokens=10000)
                    
                    other_cover_html = (
                            f"<div class='page-break-before'></div>\n"
                            f"<div class='report-page cover-page' style='padding:0; margin:0; width:100%; height:297mm; display:flex; flex-direction:column; justify-content:center; align-items:center; page-break-after: always; -webkit-print-color-adjust: exact;'>\n"
                            f"    <div style='border: 4px solid #2E7D32; padding: 50px 30px; border-radius: 20px; text-align: center; background: white; width: 80%; max-width: 600px; box-shadow: 0 10px 25px rgba(0,0,0,0.1); margin: auto;'>\n"
                            f"        <div style='border-bottom:4px double #2E7D32; padding-bottom:20px; margin-bottom:40px;'>\n"
                            
                            # 🚨 [비교 감명서 간판 56px 웅장하게 확대!!]
                            f"            <h1 class='title-gothic' style='font-size: 56px !important; margin:0 !important; line-height: 1.3 !important; word-break: keep-all !important;'>초연 시공명리 타 감명서 비교</h1>\n"
                            
                            f"            <div style='text-align: right; margin-top: 10px;'>\n"
                            f"                <span class='ver-gothic' style='font-size: 14px; letter-spacing: 1px;'>{APP_VERSION}</span>\n"
                            f"            </div>\n"
                            f"        </div>\n"
                            f"        <div style='background:#F8F9FA; border: 1px solid #E8EAF6; padding: 30px 20px; border-radius: 15px;'>\n"
                            f"            <h2 style='font-size: 24px; font-weight: 800; color: #2E7D32; margin-bottom: 20px;'>👤 신청인 : {u_name} 님</h2>\n"
                            f"            <div style='font-size: 15px; font-weight: 600; color: #555; line-height: 1.8;'>\n"
                            f"                <p style='margin: 0; white-space: nowrap;'>[양력] {sol_str} | [음력] {lun_str}</p>\n"
                            f"            </div>\n"
                            f"        </div>\n"
                            f"        <p style='font-size: 18px; margin-top: 50px; font-weight: 800;'>{today_str}</p>\n"
                            f"        <p style='font-size: 22px; font-weight: 800; color: #2E7D32; margin-top: 20px;'>초연 시공명리 연구소</p>\n"
                            f"    </div>\n"
                            f"</div>"
                    )
                    
                    st.session_state['saved_report_2'] = other_cover_html + report_2_html + f"<div class='page-break-before'></div><div class='report-page'><div class='vip-inset-frame' style='border-color:#2E7D32;'><h1 style='text-align:center; color:#2E7D32; font-size: 26px; font-weight: 800; border-bottom:2px solid #2E7D32; padding-bottom:15px;'>⚖️ 1:1 상세비교 본문 리포트</h1><div style='margin-top:20px;'>{c_res}</div></div></div>"

                except Exception as e:
                    st.error(f"2단계 비교 분석 중 오류 발생: {e}")

            # ==================================================================
            # 💕 [3단계] 궁합 풀이)
            # ==================================================================
            if u_product == "궁합":
                try:
                    # 3-1. 상대방(여명 또는 파트너) 정밀 역산 연산 시스템 가동
                    p_klc = KoreanLunarCalendar()
                    if p_cal == "양력": p_klc.setSolarDate(p_y, p_m, p_d)
                    elif p_cal == "음력(평달)": p_klc.setLunarDate(p_y, p_m, p_d, False)
                    else: p_klc.setLunarDate(p_y, p_m, p_d, True)
                    
                    p_is_leap = getattr(p_klc, 'isIntercalary', False)
                    p_leap_str = "윤달" if p_is_leap else "평달"
                    p_sol_str = f"{p_klc.solarYear}년 {p_klc.solarMonth:02d}월 {p_klc.solarDay:02d}일"
                    p_lun_str = f"{p_klc.lunarYear}년 {p_klc.lunarMonth:02d}월 {p_klc.lunarDay:02d}일 ({p_leap_str})"
                    p_age = curr_y - p_y + 1
                    
                    p_base_dt = dt_mod.datetime(p_y, p_m, p_d, 12, 0)
                    p_gj = p_klc.getChineseGapJaString().split()
                    p_ys, p_yb, p_ms, p_mb, p_ds, p_db = p_gj[0][0], p_gj[0][1], p_gj[1][0], p_gj[1][1], p_gj[2][0], p_gj[2][1]
                    p_hs, p_hb = get_time_ganji(p_ds, p_t, p_base_dt)
                    partner_bazi = [f"{p_hs}{p_hb}", f"{p_ds}{p_db}", f"{p_ms}{p_mb}", f"{p_ys}{p_yb}"]

                    # 3-2. 남명/여명 데이터 대칭 배정 (모든 변수 완벽 맵핑)
                    if u_gender == "남성":
                        m_name, m_sol, m_lun, m_time, m_age = u_name, sol_str, lun_str, time_str, u_age
                        m_gans, m_jjis = gans, jjis
                        m_ys, m_yb, m_ms, m_mb, m_ds, m_db, m_hs, m_hb = ys, yb, ms, mb, ds, db, hs, hb
                        m_calc_d, m_order = calc_d, order
                        
                        f_name, f_sol, f_lun, f_time, f_age = p_name, p_sol_str, p_lun_str, f" {p_t.split('(')[0].strip()} ({p_hb})시" if p_t != "시간 모름" else "", p_age
                        f_gans, f_jjis = [p_hs, p_ds, p_ms, p_ys], [p_hb, p_db, p_mb, p_yb]
                        f_ys, f_yb, f_ms, f_mb, f_ds, f_db, f_hs, f_hb = p_ys, p_yb, p_ms, p_mb, p_ds, p_db, p_hs, p_hb
                        p_utc_dt = p_base_dt - dt_mod.timedelta(hours=9) + dt_mod.timedelta(minutes=get_total_time_adjustment(p_base_dt))
                        p_order = 1 if (GAN.index(p_ys)%2==0) == (p_gender=='남성') else -1
                        f_calc_d, f_order = get_daeun_su_accurate(p_utc_dt, p_order), p_order
                        
                        male_data_pack, female_data_pack = applicant_bazi, partner_bazi
                    else:
                        m_name, m_sol, m_lun, m_time, m_age = p_name, p_sol_str, p_lun_str, f" {p_t.split('(')[0].strip()} ({p_hb})시" if p_t != "시간 모름" else "", p_age
                        m_gans, m_jjis = [p_hs, p_ds, p_ms, p_ys], [p_hb, p_db, p_mb, p_yb]
                        m_ys, m_yb, m_ms, m_mb, m_ds, m_db, m_hs, m_hb = p_ys, p_yb, p_ms, p_mb, p_ds, p_db, p_hs, p_hb
                        p_utc_dt = p_base_dt - dt_mod.timedelta(hours=9) + dt_mod.timedelta(minutes=get_total_time_adjustment(p_base_dt))
                        p_order = 1 if (GAN.index(p_ys)%2==0) == (p_gender=='남성') else -1
                        m_calc_d, m_order = get_daeun_su_accurate(p_utc_dt, p_order), p_order
                        
                        f_name, f_sol, f_lun, f_time, f_age = u_name, sol_str, lun_str, time_str, u_age
                        f_gans, f_jjis = gans, jjis
                        f_ys, f_yb, f_ms, f_mb, f_ds, f_db, f_hs, f_hb = ys, yb, ms, mb, ds, db, hs, hb
                        f_calc_d, f_order = calc_d, order
                        
                        male_data_pack, female_data_pack = partner_bazi, applicant_bazi

                    # 3-3. 올해 간지 공통 변수
                    curr_j = JI[((curr_y - 1984) % 60) % 12]

                    def get_counts(t_gans, t_jjis):
                        c = {"목":0,"화":0,"토":0,"금":0,"수":0}
                        for x in t_gans + t_jjis:
                            if x != "?": c[get_color(x)] += 1
                        return c

                    m_cnt, f_cnt = get_counts(m_gans, m_jjis), get_counts(f_gans, f_jjis)

                    # 3-4. 사주표 생성 함수 (이름 '+' 기호 원천 제거 및 마스터 바 한 줄 정렬)
                    m_name = m_name.replace("+", "").strip()
                    f_name = f_name.replace("+", "").strip()

                    def build_bazi_table(gender_icon, name, gender_str, marital_str, age, sol, lun, time, t_gans, t_jjis, t_ds, t_yb, counts, guiin, y_gong, d_gong, samjae, daeun_su, color):
                        ji_rel_rows = ""
                        for l_idx, r_idx in enumerate([1, 2, 0, 3]):
                            b_bot = "1px solid #444 !important" if l_idx == 3 else "none !important"
                            cells = "".join([f"<td style='color:{('#D50000' if ci==r_idx else ('#000' if get_ji_rel_set(t_jjis[r_idx], t_jjis[ci])!='-' else '#BBB'))}; font-weight:900; border-top:none !important; border-bottom:{b_bot}; border-left:1px solid #444 !important; border-right:1px solid #444 !important;'>{('←('+t_jjis[r_idx]+')→' if ci==r_idx else get_ji_rel_set(t_jjis[r_idx], t_jjis[ci]))}</td>" for ci in range(4)])
                            lbl = f"<td rowspan='4' class='header-cell-main' style='border:1px solid #444 !important;'>합충형파해</td>" if l_idx==0 else ""
                            ji_rel_rows += f"<tr>{lbl}{cells}</tr>"

                        # 🚨 이름은 무조건 남색(#1A237E) 고정
                        info_str = f"<div style='text-align:center; margin-bottom:15px; font-family:\"Malgun Gothic\", sans-serif;'><span style='font-size:18px; font-weight:900; color:#1A237E;'>{gender_icon} {name}님 ({gender_str}, {marital_str}, {age}세)</span><br><span style='font-size:14px; font-weight:900; color:#222;'>[양력] {sol} | [음력] {lun}{time}</span></div>"
                        
                        def td(c): return f"<td class='color-{get_color(c)}' style='font-size:20px; font-weight:900; border:1px solid #444 !important;'>{('?' if c in ['?',' ','-'] else c)}</td>"
                            
                        return (
                            f"{info_str}\n"
                            f"<table class='result-table' style='width:100%; border-collapse:collapse; text-align:center;'>\n"
                            f"<tr class='top-header-cell'>\n"
                            f"<td style='border:1px solid #444; font-size:15px !important; white-space:nowrap;'>구분</td>\n"
                            f"<td style='border:1px solid #444; font-size:15px !important; white-space:nowrap;'>시주</td>\n"
                            f"<td style='border:1px solid #444; font-size:15px !important; white-space:nowrap;'>일주</td>\n"
                            f"<td style='border:1px solid #444; font-size:15px !important; white-space:nowrap;'>월주</td>\n"
                            f"<td style='border:1px solid #444; font-size:15px !important; white-space:nowrap;'>년주</td>\n"
                            f"</tr>\n"
                            f"<tr><td class='header-cell-main' style='border:1px solid #444; font-size:15px !important; white-space:nowrap;'>천간십성</td><td style='border:1px solid #444;'>{get_ss(t_ds,t_gans[0])}</td><td style='border:1px solid #444;'><span style='color:#D50000; font-weight:900;'>日元</span></td><td style='border:1px solid #444;'>{get_ss(t_ds,t_gans[2])}</td><td style='border:1px solid #444;'>{get_ss(t_ds,t_gans[3])}</td></tr>\n"
                            f"<tr><td class='header-cell-main' style='border:1px solid #444; font-size:15px !important; white-space:nowrap;'>천간</td>{td(t_gans[0])}{td(t_gans[1])}{td(t_gans[2])}{td(t_gans[3])}</tr>\n"
                            f"<tr><td class='header-cell-main' style='border:1px solid #444; font-size:15px !important; white-space:nowrap;'>지지</td>{td(t_jjis[0])}{td(t_jjis[1])}{td(t_jjis[2])}{td(t_jjis[3])}</tr>\n"
                            f"<tr><td class='header-cell-main' style='border:1px solid #444; font-size:15px !important; white-space:nowrap;'>지지십성</td><td style='border:1px solid #444;'>{get_ss(t_ds,t_jjis[0])}</td><td style='border:1px solid #444;'>{get_ss(t_ds,t_jjis[1])}</td><td style='border:1px solid #444;'>{get_ss(t_ds,t_jjis[2])}</td><td style='border:1px solid #444;'>{get_ss(t_ds,t_jjis[3])}</td></tr>\n"
                            f"<tr><td class='header-cell-main' style='border:1px solid #444; padding:0; font-size:15px !important; white-space:nowrap;'>지장간</td>{''.join([f'<td style=\"border:1px solid #444; padding:0;\">{get_jijanggan_full(t_ds, t_jjis[i])}</td>' for i in range(4)])}</tr>\n"
                            f"{ji_rel_rows}\n"
                            f"<tr><td class='header-cell-main' style='border:1px solid #444; font-size:15px !important; white-space:nowrap;'>십이운성</td>{''.join([f'<td style=\"border:1px solid #444; color:#0D47A1; font-weight:bold;\">{get_unsung(t_ds, t_jjis[i])}</td>' for i in range(4)])}</tr>\n"
                            f"<tr><td class='header-cell-main' style='border:1px solid #444; font-size:15px !important; white-space:nowrap;'>십이신살</td>{''.join([f'<td style=\"border:1px solid #444; color:#C62828; font-weight:bold;\">{get_12_shinsal(t_yb, t_jjis[i])}</td>' for i in range(4)])}</tr>\n"
                            f"</table>\n"
                            f"<div style='border:2px solid {color}; margin-top:10px; margin-bottom:20px; padding:6px 8px; display:flex; justify-content:space-between; align-items:center; font-weight:900; font-size:11px; letter-spacing:-0.5px; border-radius:8px; background-color:#FAFAFA;'><div style='white-space:nowrap;'>🔢 대운수: {daeun_su}</div><div style='white-space:nowrap;'>💥 오행: 木({counts['목']}) 火({counts['화']}) 土({counts['토']}) 金({counts['금']}) 水({counts['수']})</div><div style='white-space:nowrap;'>🌟 천을귀인: <span style='color:{color};'>{guiin}</span></div><div style='white-space:nowrap;'>🎯 공망: [년] <span style='color:#C62828;'>{y_gong}</span> [일] <span style='color:#C62828;'>{d_gong}</span></div><div style='white-space:nowrap;'>🌪️ 삼재: {samjae}</div></div>"
                        )

                    m_marital = u_marital if u_gender == "남성" else p_marital
                    f_marital = p_marital if u_gender == "남성" else u_marital
                    
                    guiin_map = {'甲':'丑, 未','乙':'子, 申','丙':'酉, 亥','丁':'酉, 亥','戊':'丑, 未','己':'子, 申','庚':'丑, 未','辛':'寅, 午','壬':'卯, 巳','癸':'卯, 巳'}
                    
                    m_tbl = build_bazi_table("♂️", m_name, "남명", m_marital, m_age, m_sol, m_lun, m_time, m_gans, m_jjis, m_ds, m_yb, m_cnt, guiin_map.get(m_ds, '-'), calculate_gongmang(m_ys, m_yb), calculate_gongmang(m_ds, m_db), get_samjae(m_yb, curr_j), m_calc_d, "#1A237E")
                    f_tbl = build_bazi_table("♀️", f_name, "여명", f_marital, f_age, f_sol, f_lun, f_time, f_gans, f_jjis, f_ds, f_yb, f_cnt, guiin_map.get(f_ds, '-'), calculate_gongmang(f_ys, f_yb), calculate_gongmang(f_ds, f_db), get_samjae(f_yb, curr_j), f_calc_d, "#D50000")
                    
                    # 🚨 대운수(m_calc_d, f_calc_d) 및 년 공망(calculate_gongmang(m_ys, m_yb)) 변수 완벽 주입
                    m_tbl = build_bazi_table("♂️", m_name, "남명", m_marital, m_age, m_sol, m_lun, m_time, m_gans, m_jjis, m_ds, m_yb, m_cnt, guiin_map.get(m_ds, '-'), calculate_gongmang(m_ys, m_yb), calculate_gongmang(m_ds, m_db), get_samjae(m_yb, curr_j), m_calc_d, "#1A237E")
                    f_tbl = build_bazi_table("♀️", f_name, "여명", f_marital, f_age, f_sol, f_lun, f_time, f_gans, f_jjis, f_ds, f_yb, f_cnt, guiin_map.get(f_ds, '-'), calculate_gongmang(f_ys, f_yb), calculate_gongmang(f_ds, f_db), get_samjae(f_yb, curr_j), f_calc_d, "#D50000")
                    # 3-5. 궁합 페이지용 상하 대운표 생성기
                    def build_daewun_html(name, t_ds, t_ms, t_mb, t_yb, t_calc_d, t_order, age, color):
                        d_str = "순행" if t_order == 1 else "역행"
                        # 🚨 [핵심수술] 대운표 제목 색상도 무조건 진한 남색(#1A237E)으로 강제 고정!
                        html = f"<div style='margin-bottom:10px;'><div style='font-size:15px; font-weight:900; color:#1A237E; margin-bottom:5px;'>[ {name}님 대운 흐름표 (대운수: {t_calc_d}), {d_str} ]</div>"
                        html += f"<div style='display:flex; flex-direction:row-reverse; width:100%; border:2px solid #3E2723; background:white;'>"
                        for i in range(10):
                            val = i*10 + t_calc_d
                            tc = GAN[(GAN.index(t_ms)+(i+1)*t_order)%10]
                            tj = JI[(JI.index(t_mb)+(i+1)*t_order)%12]
                            bg = "#FFF9C4" if val <= age < val+10 else "transparent"
                            brd = "1px solid #ccc" if i != 9 else "none"
                            html += f"<div style='flex:1; border-left:{brd}; text-align:center; padding-bottom:3px; background-color:{bg};'><div style='background-color:#3E2723; color:#FFFFFF; font-weight:900; padding:4px 0; font-size:11px; border-bottom:1px solid #ccc;'>{val}세</div><div style='padding:2px; font-size:11px;'>{get_ss(t_ds,tc)}</div><div class='color-{get_color(tc)}' style='font-size:15px; font-weight:900;'>{tc}</div><div class='color-{get_color(tj)}' style='font-size:15px; font-weight:900;'>{tj}</div><div style='padding:2px; font-size:11px;'>{get_ss(t_ds,tj)}</div><div style='font-size:10px; border-top:1px solid #eee;'>{get_unsung(t_ds,tj)}</div><div style='font-size:10px; color:#C62828; border-top:1px solid #eee;'>{get_12_shinsal(t_yb, tj)}</div></div>"
                        return html + "</div></div>"

                    # (여성 대운표에도 무조건 #1A237E 남색을 던져서 빨간색 발현 원천 차단)
                    m_page_un_html = build_daewun_html(m_name, m_ds, m_ms, m_mb, m_yb, m_calc_d, m_order, m_age, "#1A237E")
                    f_page_un_html = build_daewun_html(f_name, f_ds, f_ms, f_mb, f_yb, f_calc_d, f_order, f_age, "#1A237E")
                    
                    couple_daewun_tables = f"<div style='margin-bottom: 25px;'>{m_page_un_html}<div style='height:20px;'></div>{f_page_un_html}</div>"

                    # 3-6. AI 에세이 가동
                    m_w_val = choyeon_db.get("wolryeong", {}).get(m_ms+m_mb, "시공간 데이터 없음")
                    m_i_val = choyeon_db.get("ilju", {}).get(m_ds+m_db, "성품 데이터 없음")
                    m_golden = f"<p style='font-family: \"Nanum Myeongjo\", serif; font-size: 15px; line-height: 1.8; color: #000; text-indent: 1em;'><b>{m_name}님</b>은 '{m_w_val}'의 시공간에서, '{m_i_val}'의 성품을 지녔습니다.</p>"

                    f_w_val = choyeon_db.get("wolryeong", {}).get(f_ms+f_mb, "시공간 데이터 없음")
                    f_i_val = choyeon_db.get("ilju", {}).get(f_ds+f_db, "성품 데이터 없음")
                    f_golden = f"<p style='font-family: \"Nanum Myeongjo\", serif; font-size: 15px; line-height: 1.8; color: #000; text-indent: 1em;'><b>{f_name}님</b>은 '{f_w_val}'의 시공간에서, '{f_i_val}'의 성품을 지녔습니다.</p>"
                    
                    gh_engine = UniversalPrintableGunghap(u_name, p_name, male_data_pack, female_data_pack, 10)
                    gh_engine.run_universal_logic()
                    
                    essay_prompt = f"""[SYSTEM ROLE: CHOYEON SIGONG MASTER]
당신은 명리심리상담사 '초연 박사'입니다.

🚨 [출력 절대 형식 및 내용 생성 규칙 - 매우 중요!]
1. 각 소제목 아래에 절대로 '(축약 에세이)', '(에세이)' 등의 안내 문구를 그대로 복사해서 출력하지 마십시오!
2. 반드시 내담자의 명리적 특징을 분석하여 3~4문장 분량의 **실제 통변 내용(해석)**을 직접 글로 작성해야 합니다.
3. 모든 통변 문장은 HTML 태그 <p style='font-family: "Nanum Myeongjo", serif; font-size: 15px; line-height: 1.8; color: #000; text-indent: 1em; text-align: justify;'> 로 감싸십시오.

[MALE_START]
<h3 style='color:#1A237E; font-size: 22px; font-weight: 900; margin-top: 15px;'>1. 사주팔자의 요약</h3>
{m_golden}
<span class='sub-title' style='display: block; font-size: 18px; font-weight: 900; color: #111; margin-top: 15px; margin-bottom: 5px;'>1) 타고난 삶의 무대와 기본 성향</span>
(이곳에 남성의 명리적 성향을 분석한 실제 에세이 작성)
<span class='sub-title' style='display: block; font-size: 18px; font-weight: 900; color: #111; margin-top: 25px; margin-bottom: 5px;'>2) 내 삶의 리듬과 에너지 균형</span>
(이곳에 남성의 오행 및 조후 에너지를 분석한 실제 에세이 작성)

<h3 style='color:#1A237E; font-size: 22px; font-weight: 900; margin-top: 35px;'>2. 성격 및 가치관</h3>
<span class='sub-title' style='display: block; font-size: 18px; font-weight: 900; color: #111; margin-top: 15px; margin-bottom: 5px;'>1) 겉으로 드러난 성격</span>
(이곳에 남성의 사회적 표면 성격을 분석한 실제 에세이 작성)
<span class='sub-title' style='display: block; font-size: 18px; font-weight: 900; color: #111; margin-top: 25px; margin-bottom: 5px;'>2) 감추어진 내 속마음</span>
(이곳에 남성의 내면과 무의식을 분석한 실제 에세이 작성)
<span class='sub-title' style='display: block; font-size: 18px; font-weight: 900; color: #111; margin-top: 25px; margin-bottom: 5px;'>3) 무의식이 갈망하는 반려자의 상</span>
(일지의 십성과 십이운성, 지장간의 포태법을 바탕으로 육친적, 심리적, 사회적 관점을 살려 남성의 연애 및 결혼관을 실제 에세이로 작성)
[MALE_END]

[FEMALE_START]
<h3 style='color:#D50000; font-size: 22px; font-weight: 900; margin-top: 15px;'>1. 사주팔자의 요약</h3>
{f_golden}
<span class='sub-title' style='display: block; font-size: 18px; font-weight: 900; color: #111; margin-top: 15px; margin-bottom: 5px;'>1) 타고난 삶의 무대와 기본 성향</span>
(이곳에 여성의 명리적 성향을 분석한 실제 에세이 작성)
<span class='sub-title' style='display: block; font-size: 18px; font-weight: 900; color: #111; margin-top: 25px; margin-bottom: 5px;'>2) 내 삶의 리듬과 에너지 균형</span>
(이곳에 여성의 오행 및 조후 에너지를 분석한 실제 에세이 작성)

<h3 style='color:#D50000; font-size: 22px; font-weight: 900; margin-top: 35px;'>2. 성격 및 가치관</h3>
<span class='sub-title' style='display: block; font-size: 18px; font-weight: 900; color: #111; margin-top: 15px; margin-bottom: 5px;'>1) 겉으로 드러난 성격</span>
(이곳에 여성의 사회적 표면 성격을 분석한 실제 에세이 작성)
<span class='sub-title' style='display: block; font-size: 18px; font-weight: 900; color: #111; margin-top: 25px; margin-bottom: 5px;'>2) 감추어진 내 속마음</span>
(이곳에 여성의 내면과 무의식을 분석한 실제 에세이 작성)
<span class='sub-title' style='display: block; font-size: 18px; font-weight: 900; color: #111; margin-top: 25px; margin-bottom: 5px;'>3) 무의식이 갈망하는 반려자의 상</span>
(일지의 십성과 십이운성, 지장간의 포태법을 바탕으로 육친적, 심리적, 사회적 관점을 살려 여성의 연애 및 결혼관을 실제 에세이로 작성)
[FEMALE_END]

[GUNGHAP_START]
<h3 style='color: #1B5E20; font-size: 22px; font-weight: 900; margin-top: 10px;'>🍀 두 사람의 운명적 만남에 대하여</h3>
(이곳에 두 사람의 인연 총평을 깊이 있게 통변한 실제 에세이 작성)

<h3 style='color: #1A237E; font-size: 22px; font-weight: 900; margin-top: 35px;'>🌈 커플의 인생 기상도 분석</h3>
[COUPLE_DAEWUN_TABLES_HERE]
(이곳에 상하 대운 교차점에 따른 상생/보완을 분석한 실제 에세이 작성)

<h4 style='color: #1A237E; font-size: 18px; font-weight: 900; margin-top: 35px;'>💞 커플의 상생과 조화 궁합 분석</h4>
(이곳에 속궁합, 겉궁합, 오행 궁합을 통합 분석한 실제 에세이 작성)

<h4 style='color: #1A237E; font-size: 18px; font-weight: 900; margin-top: 35px;'>⚓ 조율의 지혜</h4>
(이곳에 갈등 극복 및 개운 처방을 담은 실제 에세이 작성)
[GUNGHAP_END]
"""
                    res_text = call_claude_api(essay_prompt, max_tokens=12000)
                    ai_clean = "\n".join([line.lstrip() for line in res_text.split("\n")])
                    
                    # 3-7. 마커 파싱 시스템
                    import re
                    m_ess, f_ess, g_ess = "", "", ai_clean
                    
                    m_match = re.search(r'\[MALE_START\](.*?)\[MALE_END\]', ai_clean, re.DOTALL)
                    if m_match: m_ess = m_match.group(1).strip()
                    
                    f_match = re.search(r'\[FEMALE_START\](.*?)\[FEMALE_END\]', ai_clean, re.DOTALL)
                    if f_match: f_ess = f_match.group(1).strip()
                    
                    g_match = re.search(r'\[GUNGHAP_START\](.*?)\[GUNGHAP_END\]', ai_clean, re.DOTALL)
                    if g_match: 
                        g_ess = g_match.group(1).strip()
                    else:
                        g_ess = ai_clean.replace(m_ess, "").replace(f_ess, "").replace("[MALE_START]", "").replace("[MALE_END]", "").replace("[FEMALE_START]", "").replace("[FEMALE_END]", "")
                    
                    # [수술] AI가 마커를 훼손하거나 누락해도 강제로 대운표를 소제목 아래에 박아넣는 무적 로직
                    import re
                    g_ess, count = re.subn(r'\[\s*COUPLE_DAEWUN_TABLES_HERE\s*\]', couple_daewun_tables, g_ess, flags=re.IGNORECASE)
                    if count == 0:  # 마커가 없으면 강제로 제목 밑에 삽입
                        g_ess = re.sub(r'(<h3[^>]*>🌈 커플의 인생 기상도 분석</h3>)', r'\1\n<div style="margin-top:15px;">' + couple_daewun_tables + '</div>', g_ess)

                    # 3-8. A4 규격 컨테이너 래퍼 
                    def wrap_a4(content, title_color="#1A237E", title="[ 초연 시공명리 사주풀이 {APP_VERSION} ]"):
                        return (
                            f"<div class='report-page'>\n"
                            f"<div class='vip-inset-frame' style='border-color:{title_color}; padding:20px;'>\n"
                            f"<h1 style='text-align:center; color:{title_color}; font-family:\"Malgun Gothic\", sans-serif; font-weight:900; border-bottom:2px solid {title_color}; padding-bottom:15px; margin-bottom:30px;'>{title}</h1>\n"
                            f"{content}\n"
                            f"</div>\n"
                            f"</div>"
                        )

                    # 3-9. 클로징 멘트 오리지널 복원 및 스코어 바
                    t_col = "#3498db" if gh_engine.final_score >= 70 else ("#f39c12" if gh_engine.final_score >= 60 else "#e74c3c")
                    bars = "".join([f"<div style='display:flex; align-items:center; margin-bottom:12px;'><div style='width:130px; font-size:13px; font-weight:bold; color:#555;'>{d['label']}</div><div style='flex:1; height:12px; margin:0 10px;'><svg width='100%' height='12'><rect width='100%' height='12' rx='6' ry='6' fill='#eee' /><rect width='{d['pct']}%' height='12' rx='6' ry='6' fill='{d['color']}' /></svg></div><div style='width:35px; font-size:12px; font-weight:bold;'>{d['pct']}%</div></div>" for d in gh_engine.details])
                    
                    closing_original = (
                        f"<div style='margin-top: 40px; padding-top: 30px; page-break-inside: avoid;'>\n"
                        f"<p style='font-family: \"Nanum Myeongjo\", serif; font-size: 15px; line-height: 1.8; color: #333;'>&nbsp;&nbsp;&nbsp;&nbsp;두 분의 <b style='color:#1A237E;'>'만남'</b>은 결코 우연이 아닌, <b style='color:#1A237E;'>'셀 수 없이 많은 시간 속에서 기적처럼 찾아온 귀한 인연'</b>입니다. 사주팔자는 각자의 바코드지만, <b style='color:#1A237E;'>'궁합(宮合)'</b>은 두 바코드가 만나 그려내는 새로운 <b style='color:#1A237E;'>'하모니(harmonie)'</b>입니다.</p>\n"
                        f"<p style='font-family: \"Nanum Myeongjo\", serif; font-size: 15px; line-height: 1.8; color: #333; margin-top: 10px;'>&nbsp;&nbsp;&nbsp;&nbsp;서로의 다름을 이해하고 채워주는 든든한 <b style='color:#1A237E;'>'동반자'</b>가 되시기를 진심으로 기원하며, 두 분의 앞날에 늘 시공간의 축복이 가득하시길 소망합니다. </p>\n"
                        f"<div style='text-align: right; margin-top: 25px;'><span style='font-weight: 900; font-size: 16px; color: #1A237E; font-family: \"Nanum Myeongjo\", serif;'>- 초연 시공명리 연구소 드림 -</span></div>\n"
                        f"</div>"
                    )

                    # 🚨 [버그 원천 차단] 모든 HTML 문자열을 소괄호 묶음으로 처리 (들여쓰기 에러 및 화면 깨짐 영구 방지)
                    g_full_content = (
                        f"<div class='choyeon-premium-report'>\n{g_ess}\n</div>\n"
                        f"<h2 style='text-align:center; margin-top:40px; font-size:22px; font-weight:900;'>📊 최종 궁합 점수</h2>\n"
                        f"<div style='display:flex; justify-content:center; align-items:center; margin:20px 0;'>\n"
                        f"<div style='width:130px; height:130px; border-radius:50%; background:conic-gradient({t_col} {gh_engine.final_score}%, #eee 0); display:flex; justify-content:center; align-items:center; -webkit-print-color-adjust: exact;'>\n"
                        f"<div style='width:98px; height:98px; background:#fff; border-radius:50%; display:flex; flex-direction:column; justify-content:center; align-items:center;'>\n"
                        f"<span style='font-size:32px; font-weight:900; color:{t_col};'>{gh_engine.final_score}</span>\n"
                        f"<span style='font-size:10px; color:#888; font-weight:bold;'>SCORE</span>\n"
                        f"</div>\n"
                        f"</div>\n"
                        f"</div>\n"
                        f"<div style='text-align:center; margin-bottom:20px;'><span style='font-size:16px; font-weight:bold; color:#fff; background:{t_col}; padding:8px 32px; border-radius:30px; -webkit-print-color-adjust: exact;'>{gh_engine.grade}</span></div>\n"
                        f"<div style='max-width:500px; margin:0 auto;'>\n{bars}\n</div>\n"
                        f"{closing_original}"
                    )

                    cover_html = (
                        f"<div class='report-page cover-page' style='padding:0; margin:0; width:100%; height:297mm; display:flex; flex-direction:column; justify-content:center; align-items:center; page-break-after: always; -webkit-print-color-adjust: exact;'>\n"
                        f"    <div style='border: 4px solid #1A237E; padding: 50px 30px; border-radius: 20px; text-align: center; background: white; width: 80%; max-width: 600px; box-shadow: 0 10px 25px rgba(0,0,0,0.1); margin: auto;'>\n"
                        f"        <div style='border-bottom:4px double #1A237E; padding-bottom:20px; margin-bottom:40px;'>\n"
                        
                        # 🚨 [궁합풀이 간판 56px 웅장하게 확대!!]
                        f"            <h1 class='title-gothic' style='font-size: 56px !important; margin:0 !important; line-height: 1.3 !important; word-break: keep-all !important;'>초연 시공명리 궁합풀이</h1>\n"
                        
                        f"            <div style='text-align: right; margin-top: 10px;'>\n"
                        f"                <span class='ver-gothic' style='font-size: 14px; letter-spacing: 1px;'>{APP_VERSION}</span>\n"
                        f"            </div>\n"
                        f"        </div>\n"
                        f"        <div style='background:#F8F9FA; border: 1px solid #E8EAF6; padding: 25px 20px; border-radius: 15px; margin-bottom: 20px;'>\n"
                        f"            <h2 style='font-size: 24px; font-weight: 800; color: #1A237E; margin-bottom: 15px;'>♂️ 남명 : {m_name} 님 <span style='font-size:16px; color:#555;'>( {m_age}세 )</span></h2>\n"
                        f"            <div style='font-size: 15px; font-weight: 600; color: #555; line-height: 1.8;'>\n"
                        f"                <p style='margin: 0; white-space: nowrap;'>[양력] {m_sol} | [음력] {m_lun}</p>\n"
                        f"            </div>\n"
                        f"        </div>\n"
                        f"        <div style='background:#F8F9FA; border: 1px solid #E8EAF6; padding: 25px 20px; border-radius: 15px;'>\n"
                        f"            <h2 style='font-size: 24px; font-weight: 800; color: #D50000; margin-bottom: 15px;'>♀️ 여명 : {f_name} 님 <span style='font-size:16px; color:#555;'>( {f_age}세 )</span></h2>\n"
                        f"            <div style='font-size: 15px; font-weight: 600; color: #555; line-height: 1.8;'>\n"
                        f"                <p style='margin: 0; white-space: nowrap;'>[양력] {f_sol} | [음력] {f_lun}</p>\n"
                        f"            </div>\n"
                        f"        </div>\n"
                        f"        <p style='font-size: 18px; margin-top: 40px; font-weight: 800;'>{today_str}</p>\n"
                        f"        <p style='font-size: 22px; font-weight: 800; color: #1A237E; margin-top: 15px;'>초연 시공명리 연구소</p>\n"
                        f"    </div>\n"
                        f"</div>"
                    )
                    st.session_state['saved_report_gh_cover'] = cover_html

                    # 3-11. 원국표 + 요약 결합 (페이지 단위로 저장)
                    m_page_content = f"{m_tbl}\n<div class='choyeon-premium-report' style='margin-top:20px;'>\n{m_ess}\n</div>"
                    f_page_content = f"{f_tbl}\n<div class='choyeon-premium-report' style='margin-top:20px;'>\n{f_ess}\n</div>"
                    
                    st.session_state['saved_report_gh_m'] = wrap_a4(m_page_content, "#1A237E", "[ 남명 사주팔자표 및 요약 ]")
                    st.session_state['saved_report_gh_f'] = wrap_a4(f_page_content, "#D50000", "[ 여명 사주팔자표 및 요약 ]")
                    st.session_state['saved_report_gh_g'] = wrap_a4(g_full_content, "#1B5E20", "[ 초연 시공명리 종합 궁합풀이 ]")
                    
                except Exception as e:
                    st.error(f"3단계 궁합 종합 분석 가동 장애: {e}")

            # 🚨 연산 종료 (스위치 끄기)
            st.session_state['need_calc'] = False

        except Exception as e: 
            st.error(f"시스템 연산 중 치명적 오류 발생: {e}")
            st.session_state['need_calc'] = False
            st.stop()

# ==============================================================================
# 🌊 7. [독립 모듈] 일진 시공간 분석 (결과 출력부)
# ==============================================================================
import datetime as dt_mod

if st.session_state.get('app_running', False) and st.session_state.get('run_waterfall', False) and 'global_gans' in st.session_state:
    
    # 🚨 [수술 1] 이미 연산된 일진 리포트가 없을 때만 가동! (토큰 중복 소모 완벽 차단)
    if not st.session_state.get('saved_report_iljin'):
        
        # 🚨 [수술 2] 연산(스피너)이 돌기 전에, 메인 사주풀이를 화면에 먼저 깔아줍니다.
        if st.session_state.get('saved_report_html'):
            st.markdown(st.session_state.get('saved_report_html', ''), unsafe_allow_html=True)
            
        t_date = st.session_state['target_date']
        
        gans_list = st.session_state['global_gans']
        jjis_list = st.session_state['global_jjis']
        m_ilgan = st.session_state['global_ds']
        m_ilji = st.session_state['global_db']
            
        def get_execution_yong(upper_group, lower_group):
            matrix = {'비겁': {'비겁':'비겁', '식상':'식상', '재성':'재성', '관성':'관성', '인성':'인성'}, '식상': {'비겁':'인성', '식상':'비겁', '재성':'식상', '관성':'재성', '인성':'관성'}, '재성': {'비겁':'관성', '식상':'인성', '재성':'비겁', '관성':'식상', '인성':'재성'}, '관성': {'비겁':'재성', '식상':'관성', '재성':'인성', '관성':'비겁', '인성':'식상'}, '인성': {'비겁':'식상', '식상':'재성', '재성':'관성', '관성':'인성', '인성':'비겁'} }
            return matrix.get(upper_group, {}).get(lower_group, '비겁')

        def get_gan_rel_simple(g1, g2):
            if not g1 or not g2 or g1=="?" or g2=="?": return "-"
            s = {g1, g2}
            if s in [{'甲','己'}, {'乙','庚'}, {'丙','辛'}, {'丁','壬'}, {'戊','癸'}]: return "합(合)"
            if s in [{'甲','庚'}, {'乙','辛'}, {'丙','壬'}, {'丁','癸'}]: return "충(沖)"
            극_dict = {'甲':'戊', '乙':'己', '丙':'庚', '丁':'辛', '戊':'壬', '己':'癸', '庚':'甲', '辛':'乙', '壬':'丙', '癸':'丁'}
            if 극_dict.get(g1) == g2 or 극_dict.get(g2) == g1: return "극(剋)"
            return "-"
            
        def get_ji_rel_set_simple(j1, j2):
            if not j1 or not j2 or j1 == "?" or j2 == "?": return "-"
            s = {j1, j2}
            if s in [{'子','丑'}, {'寅','亥'}, {'卯','戌'}, {'辰','酉'}, {'巳','申'}, {'午','未'}]: return "육합"
            if s in [{'子','午'}, {'丑','未'}, {'寅','申'}, {'卯','酉'}, {'辰','戌'}, {'巳','亥'}]: return "충"
            if s in [{'子','未'}, {'丑','午'}, {'寅','酉'}, {'卯','申'}, {'辰','亥'}, {'巳','戌'}]: return "원진"
            if s in [{'寅','巳'}, {'巳','申'}, {'寅','申'}, {'丑','戌'}, {'戌','未'}, {'丑','未'}, {'子','卯'}]: return "형"
            return "-"

        from korean_lunar_calendar import KoreanLunarCalendar
        dklc = KoreanLunarCalendar()
        dklc.setSolarDate(t_date.year, t_date.month, t_date.day)
        gj_str = dklc.getChineseGapJaString()
        
        if gj_str:
            parts = gj_str.split()
            
            target_year = parts[0][:2]
            target_wol = parts[1][:2]
            target_il = parts[2][:2]
            
            ilju_lower_group = get_group_ss(get_ss(m_ilgan, m_ilji))
            
            m_che_first = get_group_ss(get_ss(m_ilgan, target_wol[0]))
            d_gan_ss = get_group_ss(get_ss(m_ilgan, target_il[0]))      
            am_yong = get_execution_yong(d_gan_ss, ilju_lower_group)
            
            m_che_second = get_group_ss(get_ss(m_ilgan, target_wol[1]))
            d_ji_ss = get_group_ss(get_ss(m_ilgan, target_il[1]))        
            pm_yong = get_execution_yong(d_ji_ss, ilju_lower_group)

            gan_desc = {"합(合)": "생각과 뜻이 맞고 긍정적 결속력이 생기는 하루입니다.", "충(沖)": "정신적인 대립이나 스트레스가 발생할 수 있습니다.", "극(剋)": "상황을 통제하느라 피로감이 따를 수 있습니다."}
            gan_res = []
            labels_gan = ["년간", "월간", "일간", "시간"]
            for idx, label in enumerate(labels_gan):
                rel = get_gan_rel_simple(gans_list[idx], target_il[0])
                if rel != "-":
                    gan_res.append(f"☁️ <b>{label}({gans_list[idx]})</b> → <span style='color:#1976D2; font-weight:bold;'>천간 {rel}</span> <span style='color:#555; font-size:13px;'>( {gans_list[idx]}{target_il[0]}{rel}하여 {gan_desc.get(rel)} )</span>")
            gan_res_html = '<br>'.join(gan_res) if gan_res else '특이 천간 파동 없음'

            ji_desc = {"충": "역동적인 변동이나 이동수가 발생하기 쉽습니다.", "원진": "심리적인 갈등이 생길 수 있으니 주의하십시오.", "육합": "일이 순조롭게 풀리고 화합하는 기운입니다.", "형": "조정하는 과정에서 시비가 따를 수 있으니 조심하십시오."}
            r_res = []
            labels_ji = ["년지", "월지", "일지", "시지"]
            
            for idx, label in enumerate(labels_ji):
                rel_full = get_ji_rel_set_simple(jjis_list[idx], target_il[1])
                if rel_full != "-":
                    main_rel = rel_full.split(',')[0].strip()
                    r_res.append(f"🌊 <b>{label}({jjis_list[idx]})</b> → <span style='color:#D50000; font-weight:bold;'>{rel_full}</span> <span style='color:#555; font-size:13px;'>( {jjis_list[idx]}{target_il[1]}{main_rel}하여 {ji_desc.get(main_rel, '변화 감지')} )</span>")

            r_res_html = '<br>'.join(r_res) if r_res else '특이 지지 파동 없음'

            def get_wunseong_simple(gan, ji):
                ws_map = {
                    '甲': {'亥':'장생', '卯':'제왕', '未':'묘', '申':'절'},
                    '乙': {'午':'장생', '寅':'제왕', '戌':'묘', '酉':'절'},
                    '丙': {'寅':'장생', '午':'제왕', '戌':'묘', '亥':'절'},
                    '丁': {'酉':'장생', '巳':'제왕', '丑':'묘', '子':'절'},
                    '戊': {'寅':'장생', '午':'제왕', '戌':'묘', '亥':'절'},
                    '己': {'酉':'장생', '巳':'제왕', '丑':'묘', '子':'절'},
                    '庚': {'巳':'장생', '酉':'제왕', '丑':'묘', '寅':'절'},
                    '辛': {'子':'장생', '申':'제왕', '辰':'묘', '卯':'절'},
                    '壬': {'申':'장생', '子':'제왕', '辰':'묘', '巳':'절'},
                    '癸': {'卯':'장생', '亥':'제왕', '未':'묘', '午':'절'}
                }
                return ws_map.get(gan, {}).get(ji, "평운(平運)")

            def get_core_shinsal_simple(m_gan, t_gan, t_ji):
                res_shinsal = []
                cheoneul = {
                    '甲':['丑','未'], '戊':['丑','未'], '庚':['丑','未'],
                    '乙':['子','申'], '己':['子','申'],
                    '丙':['亥','酉'], '丁':['亥','酉'],
                    '辛':['寅','午'],
                    '壬':['巳','卯'], '癸':['巳','卯']
                }
                if t_ji in cheoneul.get(m_gan, []):
                    res_shinsal.append("🌟천을귀인")

                daily_pillar = f"{t_gan}{t_ji}"
                if daily_pillar in ['甲辰', '乙未', '丙戌', '丁丑', '戊辰', '壬戌', '癸丑']:
                    res_shinsal.append("⚡백호살")
                if daily_pillar in ['戊戌', '庚辰', '庚戌', '壬辰']:
                    res_shinsal.append("🔥괴강살")

                yangin = {'甲':'卯', '丙':'午', '戊':'午', '庚':'酉', '壬':'子'}
                if yangin.get(m_gan) == t_ji:
                    res_shinsal.append("⚔️양인살")

                return ", ".join(res_shinsal) if res_shinsal else "특이 흉살/귀인 없음"

            day_wunseong = get_wunseong_simple(m_ilgan, target_il[1])
            day_shinsal = get_core_shinsal_simple(m_ilgan, target_il[0], target_il[1])
            s_res_html = f"✨ <b>오늘의 핵심 에너지:</b> 십이운성[{day_wunseong}] / 특수기운[{day_shinsal}]"

            iljin_prompt = f"""
당신은 명리심리상담사 초연 박사입니다. 아래의 정밀 연산된 시공간 파동 팩트를 바탕으로 오늘 하루(일진)의 흐름을 날카롭게 분석하십시오.

[내담자 및 환경 정보]
- 내담자 일주: {m_ilgan}{m_ilji}
- 일진(오늘) 날짜: {t_date.year}년 {t_date.month}월 {t_date.day}일 ({target_year}년 {target_wol}월 {target_il}일)
- 현재 월운(환경): {target_wol}월

[오늘의 사주 원국 상호작용 파동 데이터]
- 천간 파동 현황: {gan_res_html}
- 지지 형충파해 파동 현황: {r_res_html}

🚨 [AI 출력 포맷 절대 규칙]
1. 오지랖 절대 금지: 서론 인사말 불가.
2. 마크다운 기호 금지: 오직 HTML <b> 태그만 사용.
3. 빈 줄 생성 금지: 모든 줄바꿈은 <br> 태그 1회.

[출력 템플릿]
<br><b>🌅 전반부 (자시~오시, 00:30~13:29):</b>
<b>1) 일반 명리 풀이:</b> (내용)
<b>2) 시공 명리 풀이:</b> (내용)
<br><b>🌃 후반부 (미시~야자시, 13:30~익일 00:29):</b>
<b>1) 일반 명리 풀이:</b> (내용)
<b>2) 시공 명리 풀이:</b> (내용)
"""
            # 🚨 [수술 3] 스피너 문구를 센스있게 교체!
            with st.spinner("⏳ 메인 사주풀이 보존 완료! 하단에 [일진 시공간 분석]을 추가 가동 중입니다..."):
                try:
                    res = model.generate_content(iljin_prompt)
                    ai_iljin_html = res.text.strip().replace("\n", "<br>")
                except Exception as e:
                    ai_iljin_html = f"<div style='color:red; font-weight:bold; padding:10px;'>🚨 AI 일진 분석 장애: {e}</div>"

            # 🚨 [버그 원천 차단] 괄호 문자열 처리로 들여쓰기 에러 완벽 해결
            html_output = (
                f"<div class='page-break-before'></div>\n"
                f"<div class='report-page'>\n"
                f"<div class='vip-inset-frame' style='border: 3px solid #1A237E;'>\n"
                f"<h1 style='text-align: center; color: #1A237E;'>🔮 일진 시공간 정밀 분석서 {APP_VERSION}</h1>\n"
                f"<div style='text-align: center; font-size: 16px; font-weight: bold; color: #555; margin-bottom: 20px;'>\n"
                f"대상일자: {t_date.year}년 {t_date.month}월 {t_date.day}일 ({target_year}년 {target_wol}월 {target_il}일)\n"
                f"</div>\n"
                f"<div style='margin-bottom: 25px; background: #FFF8E1; padding: 15px; border-radius: 8px; font-size: 14px; line-height: 1.6;'>\n"
                f"{gan_res_html}<br>{r_res_html}\n"
                f"</div>\n"
                f"<div class='content-box-loose' style='font-size: 15px; line-height: 1.8;'>\n"
                f"{ai_iljin_html}\n"
                f"</div>\n"
                f"</div>\n"
                f"</div>"
            )
            
            # 🚨 [수술 4] 7번 모듈에서 강제 출력 금지! 메모리에 저장만 하고 깔끔하게 새로고침
            st.session_state['saved_report_iljin'] = html_output
            st.rerun() # 연산 완료 즉시 9번 출력부로 토스하여 예쁘게 합침!
# ==============================================================================
# 👶 8. [독립 모듈] 출산택일 정밀 분석 (기존 궁합 보존 가동)
# ==============================================================================
if st.session_state.get('app_running', False) and st.session_state.get('run_delivery_only', False) and 'global_gans' in st.session_state:
    with st.spinner("⏳ [출산택일 분석실] 최적의 길일 연산 및 AI 통변 중... (기존 궁합풀이는 안전하게 보존 중입니다)"):
        try:
            gans = st.session_state['global_gans']
            jjis = st.session_state['global_jjis']
            p_bazi_context = st.session_state.get('partner_bazi', ["?", "?", "?", "?"])
            
            if u_gender == "남성":
                m_jjis = jjis
                f_jjis = [b[1] if len(b)>1 else "?" for b in p_bazi_context]
            else:
                m_jjis = [b[1] if len(b)>1 else "?" for b in p_bazi_context]
                f_jjis = jjis

            FORBIDDEN_LIST = ['병오', '임자', '계해', '신유', '경신']
            delivery_days = get_optimized_delivery_days(
                start_date, 
                end_date, 
                m_jjis, f_jjis, FORBIDDEN_LIST
            )
            
            del_content = (
                f"<h2 style='text-align:center;'>👶 새 생명 마중 길일 추천</h2>\n"
                f"<p>부모님의 사주와 조화를 이루는 길일입니다.</p>\n"
            )
            for day_info in delivery_days:
                del_content += f"<div>✅ {day_info['date']} (합 점수: {day_info['score']})</div>\n"
            
            del_content += (
                f"<br><hr>\n"
                f"<p style='font-size:14px; line-height:1.6; color:#333;'>\n"
                f"<b>💡 부부를 위한 임신 계획 가이드:</b><br>\n"
                f"위의 출산 길일은 아이의 사주 기운을 우선으로 선정한 것입니다. \n"
                f"의학적 평균 임신 기간(약 280일)을 고려할 때, <b>합궁 시기는 출산 예정일로부터 약 9개월 10일 전후</b>가 됩니다. \n"
                f"부인분의 생리 주기와 배란일을 면밀히 고려하시어, 부부께서 상의하에 가장 건강한 시기를 계획하시길 바랍니다.\n"
                f"</p>"
            )
            
            delivery_prompt = f"""
당신은 명리심리상담사 및 출산택일 최고 권위자인 초연 박사입니다. 아래 제공된 부모의 사주 기운을 바탕으로, 요청된 탐색 기간 내에서 태어날 아이의 선천적 명식과 부모간의 오행 상생 조화가 가장 극대화되는 '최고의 프리미엄 출산 희망일 및 시간'을 선정하여 전통 명리 에세이로 풀어내십시오.

[부모의 사주 정보]
- 신청인(어머니/아버지): {u_gender} / 원국: {gans}{jjis}
- 상대방(배우자): 원국 데이터: {p_bazi_context}
- 탐색 지정 기간: {start_date} ~ {end_date}
- 선호 태아 성별: {baby_gender}

🚨 [출력 및 통변 포맷 절대 규칙]
선정된 상위 추천 일자별로 반드시 박사님이 지정하신 아래의 규격화된 분리 통변 포맷을 100% 준수하여 작성하십시오. (마크다운 기호 금지, 오직 지정된 HTML 구조 사수)

<span class='sub-title' style='font-size: 18px; font-weight: 900; color: #111;'>▶ 추천 일자: OOOO년 OO월 OO일 (OO시)</span>
<br><b>1) 일반 명리 풀이:</b> (선정된 날짜와 시간의 오행 분포, 아이가 가질 선천적 격국의 강점 및 부모 사주와의 끈끈한 육친적 정서 조화 상태를 구어체로 상세 기술)
<br><b>2) 시공 명리 풀이:</b> (해당 시공간의 기운이 아이의 성장기 학업, 향후 성인이 되었을 때의 직업적/사회적 성취 및 자산 안정성에 미치는 장기적 운명의 궤도를 세련된 에세이로 기술)
"""
            del_res = model.generate_content(delivery_prompt)
            ai_delivery_html = del_res.text.strip().replace("\n", "<br>")
            
            del_content += f"<div class='content-box-loose' style='font-size:15px; line-height:1.8; margin-top:20px;'>\n{ai_delivery_html}\n</div>"

            def wrap_a4(content, title_color="#1A237E", title="[ 초연 시공명리 사주풀이 ]"):
                return (
                    f"<div class='report-page'>\n"
                    f"<div class='vip-inset-frame' style='border-color:{title_color}; padding:20px;'>\n"
                    f"<h1 style='text-align:center; color:{title_color}; font-family:\"Malgun Gothic\", sans-serif; font-weight:900; border-bottom:2px solid {title_color}; padding-bottom:15px; margin-bottom:30px;'>{title}</h1>\n"
                    f"{content}\n"
                    f"</div>\n"
                    f"</div>"
                )

            st.session_state['saved_report_del'] = wrap_a4(del_content, "#4A148C", "[ 초연 시공명리 출산택일 ]")
            st.session_state['run_delivery_only'] = False # 실행 완료 후 스위치 끄기
        except Exception as e:
            st.error(f"출산택일 연산 장애: {e}")
            st.session_state['run_delivery_only'] = False

# ==============================================================================
# 9. 화면 출력부
# ==============================================================================
if st.session_state.get('app_running', False):
    
    if u_product == "개인사주":
        # 🚨 [수술] 메인 리포트(사주풀이)를 먼저 웅장하게 출력하고, 
        st.markdown(st.session_state.get('saved_report_html', ''), unsafe_allow_html=True)
        # 일진 리포트 연산 결과가 있다면 그 바로 밑에 찰싹 붙여서 순서대로 출력!
        if st.session_state.get('saved_report_iljin'):
            st.markdown(st.session_state.get('saved_report_iljin', ''), unsafe_allow_html=True)
    
    if u_product == "타 감명서":
        st.markdown(st.session_state.get('saved_report_html', ''), unsafe_allow_html=True)
        st.markdown(st.session_state.get('saved_report_2', ''), unsafe_allow_html=True)
        
    if u_product == "궁합":
        # 🚨 [1단계] 저장된 궁합 리포트를 무조건 먼저 화면에 출력! (화면 유지 효과)
        if st.session_state.get('saved_report_gh_cover'):
            st.markdown(st.session_state.get('saved_report_gh_cover', ''), unsafe_allow_html=True)
            st.markdown("<div class='page-break-before'></div>", unsafe_allow_html=True)
            
        st.markdown(st.session_state.get('saved_report_gh_m', ''), unsafe_allow_html=True)
        st.markdown("<div class='page-break-before'></div>", unsafe_allow_html=True)
        st.markdown(st.session_state.get('saved_report_gh_f', ''), unsafe_allow_html=True)
        st.markdown("<div class='page-break-before'></div>", unsafe_allow_html=True)
        st.markdown(st.session_state.get('saved_report_gh_g', ''), unsafe_allow_html=True)

        # 🚨 [2단계] 택일 체크됨 & 연산 전일 경우 -> 하단에 독립 스피너 가동!
        if run_delivery_calc and start_date and end_date and not st.session_state.get('saved_report_del') and st.session_state.get('saved_report_gh_g'):
            with st.spinner("⏳ 출산 택일 확정 중...."):
                try:
                    gans = st.session_state.get('global_gans', ["?", "?", "?", "?"])
                    jjis = st.session_state.get('global_jjis', ["?", "?", "?", "?"])
                    p_bazi_context = st.session_state.get('partner_bazi', ["?", "?", "?", "?"])
                    
                    if u_gender == "남성":
                        m_jjis = jjis
                        f_jjis = [b[1] if len(b)>1 else "?" for b in p_bazi_context]
                        m_gans_str = "".join(gans)
                        f_gans_str = "".join([b[0] if len(b)>0 else "?" for b in p_bazi_context])
                    else:
                        m_jjis = [b[1] if len(b)>1 else "?" for b in p_bazi_context]
                        f_jjis = jjis
                        m_gans_str = "".join([b[0] if len(b)>0 else "?" for b in p_bazi_context])
                        f_gans_str = "".join(gans)

                    FORBIDDEN_LIST = ['병오', '임자', '계해', '신유', '경신']
                    delivery_days = get_optimized_delivery_days(start_date, end_date, m_jjis, f_jjis, FORBIDDEN_LIST)
                    
                    del_content = f"<h2 style='text-align:center;'>👶 새 생명 마중 길일 추천</h2>\n<p>부모님의 사주와 조화를 이루는 길일입니다.</p>\n"
                    for day_info in delivery_days:
                        del_content += f"<div>✅ {day_info['date']} (합 점수: {day_info['score']})</div>\n"
                    
                    del_content += f"<br><hr>\n<p style='font-size:14px; line-height:1.6; color:#333;'><b>💡 부부를 위한 임신 계획 가이드:</b><br>위의 출산 길일은 아이의 사주 기운을 우선으로 선정한 것입니다. 의학적 평균 임신 기간(약 280일)을 고려할 때, <b>합궁 시기는 출산 예정일로부터 약 9개월 10일 전후</b>가 됩니다. 부인분의 생리 주기와 배란일을 면밀히 고려하시어, 부부께서 상의하에 가장 건강한 시기를 계획하시길 바랍니다.</p>"
                    
                    delivery_prompt = f"""
당신은 명리심리상담사 및 출산택일 최고 권위자인 초연 박사입니다. 아래 제공된 부모의 사주 기운을 바탕으로, 요청된 탐색 기간 내에서 태어날 아이의 선천적 명식과 부모간의 오행 상생 조화가 가장 극대화되는 '최고의 프리미엄 출산 희망일 및 시간'을 선정하여 전통 명리 에세이로 풀어내십시오.

[부모의 사주 정보]
- 신청인: {u_gender} / 원국: {m_gans_str}{"".join(m_jjis)}
- 상대방: 원국: {f_gans_str}{"".join(f_jjis)}
- 탐색 지정 기간: {start_date} ~ {end_date} / 선호 태아 성별: {baby_gender}

🚨 [출력 절대 규칙]
선정된 상위 추천 일자별로 반드시 아래 규격화된 분리 통변 포맷을 100% 준수하여 작성하십시오.
<span class='sub-title' style='font-size: 18px; font-weight: 900; color: #111;'>▶ 추천 일자: OOOO년 OO월 OO일 (OO시)</span>
<br><b>1) 일반 명리 풀이:</b> (선정된 날짜와 시간의 오행 분포, 아이가 가질 선천적 격국의 강점 및 부모 사주와의 끈끈한 육친적 정서 조화 상태를 구어체로 상세 기술)
<br><b>2) 시공 명리 풀이:</b> (해당 시공간의 기운이 아이의 성장기 학업, 향후 성인이 되었을 때의 직업적/사회적 성취 및 자산 안정성에 미치는 장기적 운명의 궤도를 세련된 에세이로 기술)
"""
                    del_res = model.generate_content(delivery_prompt)
                    ai_delivery_html = del_res.text.strip().replace("\n", "<br>")
                    del_content += f"<div class='content-box-loose' style='font-size:15px; line-height:1.8; margin-top:20px;'>\n{ai_delivery_html}\n</div>"

                    # 🚨 [수술] 보라색(#4A148C) 유지하되, 맑은 고딕 32px & 이중선 양식 강제 통일
                    def wrap_a4_del(content, title_color="#4A148C", title="초연 시공명리 출산택일"):
                        return f"<div class='report-page'>\n<div class='vip-inset-frame' style='border-color:{title_color}; padding:20px;'>\n<div style='border-bottom:4px double {title_color}; padding-bottom:20px; margin-bottom:40px;'>\n<h1 style='text-align:center; font-size: 32px; color:{title_color}; font-weight: 900; margin:0; font-family:\"Malgun Gothic\", sans-serif;'>👶 {title}</h1>\n</div>\n{content}\n</div>\n</div>"

                    st.session_state['saved_report_del'] = wrap_a4_del(del_content, "#4A148C", "초연 시공명리 출산택일")
                    st.rerun() # 🚨 연산 완료 즉시 화면을 갱신하여 결과 리포트를 찰싹 붙임!
                except Exception as e:
                    st.error(f"출산택일 연산 장애: {e}")

        # 🚨 [3단계] 연산이 완료되어 세션에 저장된 택일 리포트가 있으면 궁합 밑에 최종 출력
        if st.session_state.get('saved_report_del'):
            st.markdown("<div class='page-break-before'></div>", unsafe_allow_html=True)
            st.markdown(st.session_state.get('saved_report_del', ''), unsafe_allow_html=True)
# ==============================================================================
# app.py (ver 50.5 Master - 초연 전통명리 완결판)
# ====================================================================
import streamlit as st
import pandas as pd
import json
import os
import math
import calendar
import time  
import datetime as dt_mod
from datetime import datetime
from korean_lunar_calendar import KoreanLunarCalendar
import ephem
from google import genai
import pytz
import streamlit.components.v1 as components
import re

# ==============================================================================
# 🎯 [버전 컨트롤 타워]
# ==============================================================================
APP_VERSION = "Ver 50.5 (Master Complete restoration & 14종 세분화 완결본)"

# ==============================================================================
# 0. VIP 인셋 프레임 및 초강력 프린트 CSS (ver 48.1 원형 100% 보존)
# ==============================================================================
st.set_page_config(page_title=f"초연 전통 명리 {APP_VERSION}", layout="wide")

st.markdown("""<style>
    @import url("https://fonts.googleapis.com/css2?family=Noto+Serif+KR:wght@400;600;900&display=swap");
    @import url('https://fonts.googleapis.com/css2?family=Nanum+Gothic:wght@400;700;800;900&display=swap');

    .stApp { background-color: #E8F5E9 !important; }
    
    [data-testid="stSidebar"] label,
    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3,
    [data-testid="stSidebar"] span[data-testid="stMarkdownContainer"] { 
        font-family: 'Nanum Gothic', sans-serif !important; 
    }

    div[data-testid="stSidebar"] * { font-size: 14px !important; }
    div[data-testid="stRadio"] label p { font-size: 14px !important; }
    div[data-testid="stCheckbox"] label p { font-size: 14px !important; }

    .report-page, .report-page *, .cover-page, div.cover-page *, .choyeon-premium-report, .result-table td { 
        font-family: 'Noto Serif KR', serif !important; 
    }

    .b-text { font-weight: 900 !important; color: #000000 !important; display: inline-block; }
    .b-text-red { font-weight: 900 !important; color: #D50000 !important; display: inline-block; }

    div.stButton > button { 
        font-family: 'Nanum Gothic', sans-serif !important; 
        font-weight: 900 !important; 
        font-size: 16px !important;
        border-radius: 8px !important;
        width: 100% !important;
    }

    /* Primary 버튼 (빨간색) */
    div.stButton > button[kind="primary"] { 
        background-color: #D50000 !important; 
        color: #FFFFFF !important; 
        border: none !important; 
        height: 50px !important; 
        font-weight: 900 !important;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1) !important;
    }
    div.stButton > button[kind="primary"]:hover {
        background-color: #B71C1C !important;
        color: #FFFFFF !important;
    }

    /* Secondary 버튼 (인쇄/저장 - 초록색 #00A843) */
    div.stButton > button[kind="secondary"] { 
        background-color: #00A843 !important; 
        color: #FFFFFF !important; 
        border: none !important; 
        height: 50px !important;
        font-weight: 900 !important;
        box-shadow: 0 4px 6px rgba(0,0,0,0.08) !important;
    }
    div.stButton > button[kind="secondary"]:hover {
        background-color: #008937 !important;
        color: #FFFFFF !important;
    }

    .ai-title-l1 { font-size: 22px !important; font-weight: 900 !important; color: #000000 !important; margin-top: 35px !important; margin-bottom: 15px !important; border-bottom: 2px solid #000000 !important; padding-bottom: 5px !important; line-height: 1.4 !important; font-family: sans-serif !important; display: block !important; }
    .ai-title-l2 { font-size: 18px !important; font-weight: 900 !important; color: #000000 !important; margin-top: 22px !important; margin-bottom: 10px !important; line-height: 1.4 !important; font-family: sans-serif !important; display: block !important; }
    .vip-inset-frame { border: 2px solid #3E2723 !important; border-radius: 12px !important; padding: 30px 25px !important; background-color: #FFFFFF !important; box-shadow: 0 4px 10px rgba(0,0,0,0.05); }
    .ai-body-p { font-size: 16px !important; font-weight: 400 !important; line-height: 1.85 !important; color: #222222 !important; text-align: justify !important; text-justify: inter-character !important; text-indent: 1.0em !important; margin-bottom: 12px !important; word-break: break-all !important; }

    .color-목 { background: #2E7D32 !important; color: #FFF !important; }
    .color-화 { background: #C62828 !important; color: #FFF !important; }
    .color-토 { background: #F9A825 !important; color: #000 !important; }
    .color-금 { background: #9E9E9E !important; color: #FFF !important; }
    .color-수 { background: #212121 !important; color: #FFF !important; }

    .result-table { width: 100%; border-collapse: collapse !important; border: 3px solid #3E2723 !important; margin-bottom: 15px; table-layout: fixed; }
    .result-table td { border: 1px solid #444 !important; padding: 1px 0 !important; text-align: center; vertical-align: middle; font-weight: 900 !important; font-size: 13px; line-height: 1.2 !important; }
    .ganji-cell-24 { font-size: 24px !important; font-weight: 900 !important; }

    .top-header-cell { background-color: #1A237E !important; height: 30px !important; }
    .top-header-cell td { background-color: #1A237E !important; color: #FFFFFF !important; font-weight: 900 !important; font-size: 16px !important; border: 1px solid #444 !important; }
    .header-cell-main, .header-cell-sub { background-color: #E8EAF6 !important; color: #000000 !important; font-weight: 900 !important; font-size: 14px !important; }

    .report-page { width: 210mm; max-width: 100%; margin: 20px auto; background-color: #FFF !important; padding: 12mm 10mm; box-sizing: border-box; color: #000; }

    @media print { 
        @page { size: A4 portrait; margin: 10mm; }
        .stSidebar, button, iframe, .print-hide, header { display: none !important; }
        body, .stApp { background-color: white !important; -webkit-print-color-adjust: exact !important; }
        .report-page { box-shadow: none; margin: 0 auto; page-break-after: always; width: 100%; padding: 0; }
    }
</style>""", unsafe_allow_html=True)

# ==============================================================================
# 0.5 [외부 choyeon_db.json 완벽 동적 연계]
# ==============================================================================
@st.cache_data
def load_choyeon_db():
    file_path = 'choyeon_db.json'
    if not os.path.exists(file_path):
        return {"wolryeong": {}, "ilju": {}, "ilju_structure": {}, "ilju_secret": {}, "ilju_full_master": {}}
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        st.error(f"🚨 choyeon_db.json 파일 로드 오류: {e}")
        return {"wolryeong": {}, "ilju": {}, "ilju_structure": {}, "ilju_secret": {}, "ilju_full_master": {}}

choyeon_db = load_choyeon_db()

# ==============================================================================
# 1. 시스템 변수 세팅 및 써머타임 엔진
# ==============================================================================
def get_total_time_adjustment(dt):
    adj = -30
    if dt_mod.datetime(1954, 3, 21) <= dt <= dt_mod.datetime(1961, 8, 9, 23, 59): adj = 0
    si = [(dt_mod.datetime(1948,5,31), dt_mod.datetime(1948,9,22)), (dt_mod.datetime(1949,3,31), dt_mod.datetime(1949,9,30)), (dt_mod.datetime(1950,4,1), dt_mod.datetime(1950,9,10)), (dt_mod.datetime(1951,5,6), dt_mod.datetime(1951,9,9)), (dt_mod.datetime(1954,3,21), dt_mod.datetime(1954,5,5)), (dt_mod.datetime(1955,4,6), dt_mod.datetime(1955,9,22)), (dt_mod.datetime(1956,5,20), dt_mod.datetime(1956,9,30)), (dt_mod.datetime(1957,5,5), dt_mod.datetime(1957,9,22)), (dt_mod.datetime(1958,5,4), dt_mod.datetime(1958,9,21)), (dt_mod.datetime(1959,5,4), dt_mod.datetime(1959,9,20)), (dt_mod.datetime(1960,5,1), dt_mod.datetime(1960,9,18)), (dt_mod.datetime(1987,5,10,2), dt_mod.datetime(1987,10,11,3)), (dt_mod.datetime(1988,5,8,2), dt_mod.datetime(1988,10,9,3))]
    for s, e in si:
        if s <= dt <= e: adj -= 60; break
    return adj

GAN = ["甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"]
JI = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]

def extract_ganji(text):
    g = [c for c in text if c in "甲乙丙丁戊己庚辛壬癸갑을병정무기경신임계"]
    j = [c for c in text if c in "子丑寅卯辰巳午未申酉戌亥자축인묘진사오미신유술해"]
    return (g[0] if g else "?") + (j[0] if j else "?")

def get_true_year_month_pillar(year, month, day, hour, minute):
    kst = pytz.timezone('Asia/Seoul')
    dt_kst = kst.localize(datetime(year, month, day, hour, minute))
    dt_utc = dt_kst.astimezone(pytz.utc)
    
    sun = ephem.Sun()
    sun.compute(dt_utc)
    lon = math.degrees(ephem.Ecliptic(sun).lon) % 360.0
    
    actual_year = year
    if month <= 2 and lon < 315.0: actual_year -= 1
        
    year_idx = (actual_year - 1984) % 60
    y_gan = GAN[year_idx % 10]
    y_ji = JI[year_idx % 12]
    
    if 315 <= lon < 345: m_ji_idx = 2
    elif 345 <= lon or lon < 15: m_ji_idx = 3
    elif 15 <= lon < 45: m_ji_idx = 4
    elif 45 <= lon < 75: m_ji_idx = 5
    elif 75 <= lon < 105: m_ji_idx = 6
    elif 105 <= lon < 135: m_ji_idx = 7
    elif 135 <= lon < 165: m_ji_idx = 8
    elif 165 <= lon < 195: m_ji_idx = 9
    elif 195 <= lon < 225: m_ji_idx = 10
    elif 225 <= lon < 255: m_ji_idx = 11
    elif 255 <= lon < 285: m_ji_idx = 0
    elif 285 <= lon < 315: m_ji_idx = 1
    
    y_gan_idx = year_idx % 10
    start_month_gan_idx = ((y_gan_idx % 5) * 2 + 2) % 10
    m_offset = (m_ji_idx - 2) % 12
    m_gan = GAN[(start_month_gan_idx + m_offset) % 10]
    
    return f"{y_gan}{y_ji}", f"{m_gan}{JI[m_ji_idx]}", lon

components.html("""
<script>
    const doc = window.parent.document;
    doc.addEventListener('keyup', function(e) {
        if (e.target.tagName !== 'INPUT' || e.target.type !== 'text') return;
        let label = e.target.getAttribute('aria-label') || "";
        if (label.includes('년주') || label.includes('월주') || label.includes('일주')) {
            if (e.isComposing) return;
            let val = e.target.value.trim();
            if (e.key === ' ' || e.key === 'Enter' || val.length >= 2) {
                let inputs = Array.from(doc.querySelectorAll('input[type="text"]'));
                let idx = inputs.indexOf(e.target);
                if (idx > -1 && idx < inputs.length - 1) inputs[idx + 1].focus();
            }
        }
    });
</script>
""", height=0, width=0)

# ==============================================================================
# 2. AI 및 명리 연산 엔진
# ==============================================================================
try:
    client = genai.Client(api_key=st.secrets["GOOGLE_API_KEY"])
    class GeminiModelCompat:
        def __init__(self, genai_client): self.client = genai_client
        def generate_content(self, contents, **kwargs):
            return self.client.models.generate_content(model="gemini-2.5-flash", contents=contents)
    model = GeminiModelCompat(client)
except Exception as _api_e:
    st.error(f"🚨 Gemini API 키 오류: {_api_e}")
    client, model = None, None

def call_claude_api(prompt_text, max_tokens=8000):
    if client is None: return "<div style='color:red;'>🚨 Gemini 모델이 초기화되지 않았습니다.</div>"
    try:
        response = client.models.generate_content(model="gemini-2.5-flash", contents=prompt_text)
        return response.text.strip()
    except Exception as e:
        return f"<div style='color:red;'>🚨 Gemini AI 서버 통신 장애: {e}</div>"

JIJANGGAN = {'子': ['壬', '-', '癸'], '丑': ['癸', '辛', '己'], '寅': ['戊', '丙', '甲'], '卯': ['甲', '-', '乙'], '辰': ['乙', '癸', '戊'], '巳': ['戊', '庚', '丙'], '午': ['丙', '己', '丁'], '未': ['丁', '乙', '己'], '申': ['戊', '壬', '庚'], '酉': ['庚', '-', '辛'], '戌': ['辛', '丁', '戊'], '亥': ['戊', '甲', '壬'] }

def get_color(c):
    if c in "甲乙寅卯": return "목"
    if c in "丙丁巳午": return "화"
    if c in "戊己辰戌丑未": return "토"
    if c in "庚辛申酉": return "금"
    if c in "壬癸亥子": return "수"
    return "토"

def get_ss(dg, tc):
    if tc in ["?", " ", "-"]: return "-"
    rels = {
        '甲':{'甲':'비견','乙':'겁재','丙':'식신','丁':'상관','戊':'편재','己':'정재','庚':'편관','辛':'정관','壬':'편인','癸':'정인','寅':'비견','卯':'겁재','巳':'식신','午':'상관','辰':'편재','戌':'편재','丑':'정재','未':'정재','申':'편관','酉':'정관','亥':'편인','子':'정인'},
        '乙':{'乙':'비견','甲':'겁재','丁':'식신','丙':'상관','己':'편재','戊':'정재','辛':'편관','庚':'정관','癸':'편인','壬':'정인','卯':'비견','寅':'겁재','午':'식신','巳':'상관','丑':'편재','未':'편재','辰':'정재','戌':'정재','酉':'편관','申':'정관','子':'편인','亥':'정인'},
        '丙':{'丙':'비견','丁':'겁재','戊':'식신','己':'상관','庚':'편재','辛':'정재','壬':'편관','癸':'정관','甲':'편인','乙':'정인','巳':'비견','午':'겁재','辰':'식신','戌':'식신','未':'상관','丑':'상관','申':'편재','酉':'정재','亥':'편관','子':'정관','寅':'편인','卯':'정인'},
        '丁':{'丁':'비견','丙':'겁재','己':'식신','戊':'상관','辛':'편재','庚':'정재','癸':'편관','壬':'정관','乙':'편인','甲':'정인','午':'비견','巳':'겁재','未':'식신','丑':'식신','辰':'상관','戌':'상관','酉':'편재','申':'정재','子':'편관','亥':'정관','卯':'편인','寅':'정인'},
        '戊':{'戊':'비견','己':'겁재','庚':'식신','辛':'상관','壬':'편재','癸':'정재','甲':'편관','乙':'정관','丙':'편인','丁':'정인','辰':'비견','戌':'비견','丑':'겁재','未':'겁재','申':'식신','酉':'상관','亥':'편재','子':'정재','寅':'편관','卯':'정관','巳':'편인','午':'정인'},
        '己':{'己':'비견','戊':'겁재','辛':'식신','庚':'상관','癸':'편재','壬':'정재','乙':'편관','甲':'정관','丁':'편인','丙':'정인','丑':'비견','未':'비견','辰':'겁재','戌':'겁재','酉':'식신','申':'상관','子':'편재','亥':'정재','卯':'편관','寅':'정관','午':'편인','巳':'정인'},
        '庚':{'庚':'비견','辛':'겁재','壬':'식신','癸':'상관','甲':'편재','乙':'정재','丙':'편관','丁':'정관','戊':'편인','己':'정인','申':'비견','酉':'겁재','亥':'식신','子':'상관','寅':'편재','卯':'정재','巳':'편관','午':'정관','辰':'편인','戌':'편인','丑':'정인','未':'정인'},
        '辛':{'辛':'비견','庚':'겁재','癸':'식신','壬':'상관','乙':'편재','甲':'정재','丁':'편관','丙':'정관','己':'편인','戊':'정인','酉':'비견','申':'겁재','子':'식신','亥':'상관','卯':'편재','寅':'정재','午':'편관','巳':'정관','未':'편인','丑':'편인','辰':'정인','戌':'정인'},
        '壬':{'壬':'비견','癸':'겁재','甲':'식신','乙':'상관','丙':'편재','丁':'정재','戊':'편관','己':'정관','庚':'편인','辛':'정인','亥':'비견','子':'겁재','寅':'식신','卯':'상관','巳':'편재','午':'정재','辰':'편관','戌':'편관','丑':'정관','未':'정관','申':'편인','酉':'정인'},
        '癸':{'癸':'비견','壬':'겁재','乙':'식신','甲':'상관','丁':'편재','丙':'정재','己':'편관','戊':'정관','辛':'편인','庚':'정인','子':'비견','亥':'겁재','卯':'식신','寅':'상관','午':'편재','巳':'정재','未':'편관','丑':'편관','戌':'정관','辰':'정관','酉':'편인','申':'정인'}
    }
    return rels.get(dg, {}).get(tc, "-")

def get_group_ss(ss_str):
    return {'비견':'비겁', '겁재':'비겁', '식신':'식상', '상관':'식상', '편재':'재성', '정재':'재성', '편관':'관성', '정관':'관성', '편인':'인성', '정인':'인성'}.get(ss_str, '비겁')

def get_unsung(dg, ji):
    if ji in ["?", " ", "-"]: return "-"
    table = {'甲':"亥子丑寅卯辰巳午未申酉戌",'丙':"寅卯辰巳午未申酉戌亥子丑",'戊':"寅卯辰巳午未申酉戌亥子丑",'庚':"巳午未申酉戌亥子丑寅卯辰",'壬':"申酉戌亥子丑寅卯辰巳午未",'乙':"午巳辰卯寅丑子亥戌酉申未",'丁':"酉申未午巳辰卯寅丑子亥戌",'己':"酉申未午巳辰卯寅丑子亥戌",'辛':"子亥戌酉申未午巳辰卯寅丑",'癸':"卯寅丑子亥戌酉申未午巳辰"}
    idx = table.get(dg, "").find(ji)
    return ["장생","목욕","관대","건록","제왕","쇠","병","사","묘","절","태","양"][idx] if idx != -1 else "-"

def get_12_shinsal(year_ji, target_ji):
    if target_ji in ["?", " ", "-"] or not year_ji or year_ji == "?": return "-"
    s_map = {"申":"巳","子":"巳","辰":"巳", "寅":"亥","午":"亥","戌":"亥", "巳":"寅","酉":"寅","丑":"寅", "亥":"申","卯":"申","未":"申"}
    s_idx = (list(JI).index(target_ji) - list(JI).index(s_map.get(year_ji, "巳")) + 12) % 12
    return ["겁살","재살","천살","지살","년살","월살","망신살","장성살","반안살","역마살","육해살","화개살"][s_idx]

def get_samjae(year_ji, target_ji):
    if year_ji in ["?", " ", "-"] or target_ji in ["?", " ", "-"]: return "해당 없음"
    s_map = {'申':['寅','卯','辰'],'子':['寅','卯','辰'],'辰':['寅','卯','辰'],'亥':['巳','午','未'],'卯':['巳','午','未'],'未':['巳','午','未'],'寅':['申','酉','戌'],'午':['申','酉','戌'],'戌':['申','酉','戌'],'巳':['亥','子','丑'],'酉':['亥','子','丑'],'丑':['亥','子','丑']}
    sj_list = s_map.get(year_ji, [])
    if not sj_list: return "해당 없음"
    if target_ji == sj_list[0]: return "들삼재"
    elif target_ji == sj_list[1]: return "눌삼재"
    elif target_ji == sj_list[2]: return "날삼재"
    return "해당 없음"

def get_gan_rel_all(idx, gans):
    me = gans[idx]; res = []
    if me in ["-", "?", " "]: return "-"
    for i, other in enumerate(gans):
        if i == idx or other in ["-", "?", " "]: continue
        s = {me, other}
        if s in [{'甲','己'}, {'乙','庚'}, {'丙','辛'}, {'丁','壬'}, {'戊','癸'}]: res.append("합")
        if s in [{'甲','庚'}, {'乙','辛'}, {'丙','壬'}, {'丁','癸'}, {'戊','甲'}, {'己','乙'}]: res.append("충")
    return "".join(list(set(res))) if res else "-"

def get_ji_rel_set(me, target):
    if not me or not target or me == "?" or target == "?" or me == target: return "자형" if me == target and me in "辰午酉亥" else "-"
    s, r = {me, target}, []
    if s in [{'寅','卯'}, {'卯','辰'}, {'寅','辰'}, {'巳','午'}, {'午','未'}, {'巳','未'}, {'申','酉'}, {'酉','戌'}, {'申','戌'}, {'亥','子'}, {'子','丑'}, {'亥','丑'}]: r.append("방합")
    if s in [{'申','子'}, {'子','辰'}, {'申','辰'}, {'寅','午'}, {'午','戌'}, {'寅','戌'}, {'亥','卯'}, {'卯','未'}, {'亥','未'}, {'巳','酉'}, {'酉','丑'}, {'巳','丑'}]: r.append("반합")
    if s in [{'子','丑'}, {'寅','亥'}, {'卯','戌'}, {'辰','酉'}, {'巳','申'}, {'午','未'}]: r.append("육합")
    if s in [{'午','亥'}, {'子','戌'}, {'丑','寅'}, {'寅','未'}, {'卯','申'}]: r.append("암합")
    if s in [{'子','午'}, {'丑','未'}, {'寅','申'}, {'卯','酉'}, {'辰','戌'}, {'巳','亥'}]: r.append("충")
    if s in [{'寅','巳'}, {'巳','申'}, {'寅','申'}, {'丑','戌'}, {'戌','未'}, {'丑','未'}, {'子','卯'}]: r.append("형")
    if s in [{'子','未'}, {'丑','午'}, {'寅','巳'}, {'卯','辰'}, {'申','亥'}, {'酉','戌'}]: r.append("해")
    if s in [{'子','酉'}, {'丑','辰'}, {'寅','亥'}, {'卯','午'}, {'巳','申'}, {'未','戌'}]: r.append("파")
    if s in [{'丑','午'}, {'卯','申'}, {'辰','亥'}, {'巳','戌'}]: r.extend(["원진", "귀문"])
    elif s in [{'子','酉'}, {'寅','未'}]: r.append("귀문")
    elif s in [{'寅','酉'}, {'子','未'}]: r.append("원진")
    return ", ".join(list(dict.fromkeys(r))) if r else "-"

def get_general_shinsal_filtered(idx, gans, jjis, gender="남성"):
    dc, mc, yc = gans[1], gans[2], gans[3]
    cur_g, cur_j = gans[idx], jjis[idx]
    if cur_g in ["?", "-", " "] or cur_j in ["?", "-", " "]: return []
    gj = cur_g + cur_j
    noble, ausp, evil = [], [], []
    
    if cur_j in {'甲':'未丑','乙':'申子','丙':'酉亥','丁':'酉亥','戊':'未丑','己':'申子','庚':'未丑','辛':'午寅','壬':'卯巳','癸':'卯巳'}.get(dc,""): noble.append("천을귀인") 
    if cur_j == jjis[2]: noble.append("월덕귀인") 
    if gj in ["甲辰","乙未","丙戌","丁丑","戊辰","壬戌","癸丑"]: evil.append("백호대살")
    if gj in ["庚辰","庚戌","壬辰","壬戌","戊戌"]: evil.append("괴강살")
    if cur_j in {'甲':'卯','丙':'午','戊':'午','庚':'酉','壬':'子'}.get(dc,""): evil.append("양인살")

    result = []
    for n in list(dict.fromkeys(noble)): result.append(f"<span style='color:#0D47A1;'>{n}</span>")
    for a in list(dict.fromkeys(ausp)): result.append(f"<span style='color:#2E7D32;'>{a}</span>")
    for e in list(dict.fromkeys(evil)): result.append(f"<span style='color:#C62828;'>{e}</span>")
    return result

def get_jijanggan_full(dg, ji):
    if ji in ["?", " ", "-"]: return "-"
    raw = JIJANGGAN.get(ji, ['-','-','-'])
    res = "<div style='display:flex; flex-direction:column; height:100%; min-height:65px; gap:2px; padding:2px 0; margin:0;'>"
    for j in raw:
        if j != '-':
            ss_label = get_ss(dg, j)[:2]; color_key = get_color(j)
            bg = {'목':'#2E7D32','화':'#C62828','토':'#F9A825','금':'#9E9E9E','수':'#212121'}.get(color_key, '#888')
            tc = 'white' if color_key != '토' else 'black'
            res += f"<div style='flex-grow:1; display:flex; align-items:center; justify-content:center; background:{bg}; color:{tc}; width:95%; margin:0 auto; font-size:12px; font-weight:900; border-radius:3px;'>{j} ({ss_label})</div>"
        else: res += "<div style='flex-grow:1; display:flex; align-items:center; justify-content:center; background:#f9f9f9; width:95%; margin:0 auto; color:#bbb; border-radius:3px; border:1px dashed #ddd;'>-</div>"
    return res + "</div>"

def check_vault_status(base_gans, base_jjis, attacker_ji):
    vaults = ['辰', '戌', '丑', '未']
    clash_map = {'辰':'戌', '戌':'辰', '丑':'未', '未':'丑'}
    hyung_sets = [{'丑','戌'}, {'戌','未'}, {'丑','未'}]
    core_gans = {'辰':['壬','癸'], '戌':['丙','丁'], '丑':['庚','辛'], '未':['甲','乙']}
    
    results = []
    for i, ji in enumerate(base_jjis):
        if ji in vaults:
            if clash_map.get(ji) == attacker_ji or {ji, attacker_ji} in hyung_sets:
                targets = core_gans.get(ji, [])
                is_trapped = any(g in targets for g in base_gans)
                if is_trapped:
                    trapped_chars = [g for g in targets if g in base_gans]
                    results.append(f"🚨 <b style='color:#C62828;'>[입고(入庫) 주의]</b> {ji} 무덤이 열려 천간의 {','.join(trapped_chars)} 기운이 빨려 들어갑니다.")
                else:
                    results.append(f"💎 <b style='color:#2E7D32;'>[개고(開庫) 발현]</b> {ji} 금고가 열려 지장간의 숨은 보물이 세상에 드러납니다.")
    return results

def get_gyukgook_detailed(ds, ys, ms, hs, mb):
    jg = JIJANGGAN.get(mb, [])
    if not jg: return "알수없음격", "지장간 정보가 없습니다."

    def safe_get_ss(day_gan, target_char):
        if not target_char or target_char == "?": return "무명"
        return get_ss(day_gan, target_char)

    if ds in ['甲', '丙', '戊', '庚', '壬']:
        if mb == '卯' and ds == '甲': return "양인격", "월지 겁재 및 제왕으로 폭발적 에너지인 양인격입니다."
        if mb == '午' and ds == '丙': return "양인격", "월지 겁재 및 제왕으로 폭발적 에너지인 양인격입니다."
        if mb == '酉' and ds == '庚': return "양인격", "월지 겁재 및 제왕으로 폭발적 에너지인 양인격입니다."
        if mb == '子' and ds == '壬': return "양인격", "월지 겁재 및 제왕으로 폭발적 에너지인 양인격입니다."
        if mb == {'甲':'寅', '丙':'巳', '戊':'巳', '庚':'申', '壬':'亥'}.get(ds, ""): return "건록격", f"월지 {mb}가 일간 {ds}의 건록에 해당하여 건록격으로 정합니다."

    if mb in ["子", "午", "卯", "酉"]:
        core_ss = safe_get_ss(ds, mb)
        if core_ss in ["비견", "겁재"]: return "건록(월겁)격", f"월지 {mb}가 일간 {ds}와 같은 기운이므로 건록격으로 삼습니다."
        return core_ss + "격", f"월지 {mb}의 순수한 기운인 {core_ss}을 그대로 격으로 삼습니다."
    
    main_qi = jg[-1]
    fallback_ss = safe_get_ss(ds, main_qi)
    return fallback_ss + "격", f"월지 {mb}의 본기인 {main_qi}를 기준으로 {fallback_ss}격으로 정합니다."

def calculate_gongmang(ilgan, ilji):
    if ilgan in ["?"," ","-"] or ilji in ["?"," ","-"]: return "-"
    try:
        base = (list(JI).index(ilji) - list(GAN).index(ilgan) - 2) % 12
        return list(JI)[base] + "," + list(JI)[(base+1)%12]
    except: return "-"

def get_time_ganji(day_gan, time_str, dt_obj=None):
    if "시간 모름" in time_str: return "?", "?"
    if dt_obj:
        adj_mins = get_total_time_adjustment(dt_obj)
        dt_obj += dt_mod.timedelta(minutes=adj_mins)
    target_ji, t_idx = "子", 0
    if "朝子" in time_str or "夜子" in time_str: target_ji, t_idx = "子", 0
    else:
        for j in list(JI):
            if j in time_str: target_ji, t_idx = j, list(JI).index(j); break
    start_gan_idx = {"甲":0,"己":0,"乙":2,"庚":2,"丙":4,"辛":4,"丁":6,"壬":6,"戊":8,"癸":8}.get(day_gan, 0)
    return list(GAN)[(start_gan_idx + t_idx) % 10], target_ji

def get_daeun_su_accurate(utc_dt, order):
    try:
        sun = ephem.Sun()
        def get_lon(dt):
            sun.compute(dt)
            return math.degrees(ephem.Ecliptic(sun).lon) % 360.0
        start_lon = get_lon(utc_dt)
        jeol_lons = [315, 345, 15, 45, 75, 105, 135, 165, 195, 225, 255, 285]
        if order == 1: t_lon_unwrapped = min([l for l in jeol_lons if l > start_lon] + [l + 360 for l in jeol_lons if l <= start_lon])
        else: t_lon_unwrapped = max([l for l in jeol_lons if l <= start_lon] + [l - 360 for l in jeol_lons if l > start_lon])
        search_dt = utc_dt
        step = dt_mod.timedelta(minutes=10) if order == 1 else dt_mod.timedelta(minutes=-10)
        for _ in range(6000):
            search_dt += step
            curr_lon = get_lon(search_dt)
            if order == 1 and curr_lon < start_lon and (start_lon - curr_lon) > 180: curr_lon += 360
            elif order == -1 and curr_lon > start_lon and (curr_lon - start_lon) > 180: curr_lon -= 360
            if (order == 1 and curr_lon >= t_lon_unwrapped) or (order == -1 and curr_lon <= t_lon_unwrapped): break
        total_days = abs((search_dt - utc_dt).total_seconds()) / 86400.0
        d_su = int(round(total_days / 3.0))
        return max(1, min(10, d_su))
    except: return 1

def get_optimized_delivery_days(start_date, end_date, m_jjis, f_jjis, forbidden_list):
    results = []
    curr_date = start_date
    while curr_date <= end_date:
        results.append({'date': curr_date.strftime('%Y-%m-%d'), 'score': 85})
        curr_date += dt_mod.timedelta(days=1)
    return sorted(results, key=lambda x: x['score'], reverse=True)[:5]

# ==============================================================================
# 3. 프리미엄 궁합 분석 엔진 클래스 (ver 48.3 원형 100% 보존 및 조후/묘고 메서드 포함)
# ==============================================================================
class UniversalPrintableGunghap:
    def __init__(self, applicant, partner_name, male, female, daeun_score=10):
        self.app, self.p_name, self.daeun_score = applicant, partner_name, daeun_score
        male = [m if m and len(m) >= 2 else "  " for m in (list(male) + ["  ", "  ", "  ", "  "])][:4]
        female = [f if f and len(f) >= 2 else "  " for f in (list(female) + ["  ", "  ", "  ", "  "])][:4]
        self.m_g = [male[3][0], male[2][0], male[1][0], male[0][0]]
        self.m_j = [male[3][1], male[2][1], male[1][1], male[0][1]]
        self.f_g = [female[3][0], female[2][0], female[1][0], female[0][0]]
        self.f_j = [female[3][1], female[2][1], female[1][1], female[0][1]]
        self.logic_flags, self.details = {}, []

    def get_ji_rel(self, j1, j2):
        if not j1 or not j2 or j1=="?" or j2=="?": return "무"
        s = {j1, j2}
        if s in [{'子','丑'}, {'寅','亥'}, {'卯','戌'}, {'辰','酉'}, {'巳','申'}, {'午','未'}]: return "육합"
        if s in [{'寅','卯'}, {'卯','辰'}, {'寅','辰'}, {'巳','午'}, {'午','未'}, {'巳','未'}, {'申','酉'}, {'酉','戌'}, {'申','戌'}, {'亥','子'}, {'子','丑'}, {'亥','丑'}]: return "방합"
        if s in [{'申','子'}, {'子','辰'}, {'申','辰'}, {'寅','午'}, {'午','戌'}, {'寅','戌'}, {'亥','卯'}, {'卯','未'}, {'亥','未'}, {'巳','酉'}, {'酉','丑'}, {'巳','丑'}]: return "반합"
        if s in [{'子','午'}, {'丑','未'}, {'寅','申'}, {'卯','酉'}, {'辰','戌'}, {'巳','亥'}]: return "충"
        if s in [{'子','未'}, {'丑','午'}, {'寅','酉'}, {'卯','申'}, {'辰','亥'}, {'巳','戌'}]: return "원진"
        if s in [{'寅','巳'}, {'巳','申'}, {'寅','申'}, {'丑','戌'}, {'戌','未'}, {'丑','未'}, {'子','卯'}]: return "형"
        if s in [{'子','酉'}, {'丑','辰'}, {'寅','亥'}, {'卯','午'}, {'巳','申'}, {'未','戌'}]: return "파"
        if s in [{'子','未'}, {'丑','午'}, {'寅','巳'}, {'卯','辰'}, {'申','亥'}, {'酉','戌'}]: return "해"
        return "무"

    def count_elements(self, gans, jjis):
        counts = {'목':0, '화':0, '토':0, '금':0, '수':0}
        for c in gans + jjis:
            if c in "甲乙寅卯": counts['목'] += 1
            elif c in "丙丁巳午": counts['화'] += 1
            elif c in "戊己辰戌丑未": counts['토'] += 1
            elif c in "庚辛申酉": counts['금'] += 1
            elif c in "壬癸亥子": counts['수'] += 1
        return counts

    def get_vault_harmony(self, base_gans, base_jjis, partner_jjis):
        results = []
        for p_ji in partner_jjis:
            results.extend(check_vault_status(base_gans, base_jjis, p_ji))
        return results

    def get_johoo_harmony(self, m_ilgan, m_ec, f_ec):
        score = 0
        if m_ilgan in "丙丁":
            if f_ec['수'] >= 2: score += 5
        elif m_ilgan in "壬癸":
            if f_ec['화'] >= 2: score += 5
        return score

    def run_universal_logic(self):
        m_g, m_j, f_g, f_j = self.m_g, self.m_j, self.f_g, self.f_j
        il_rel = self.get_ji_rel(m_j[2], f_j[2])
        if il_rel == "육합": s1 = 25
        elif il_rel in ["방합", "반합"]: s1 = 21
        elif il_rel == "무": s1 = 17
        elif il_rel in ["파", "해"]: s1 = 12
        elif il_rel in ["형", "원진"]: s1 = 8
        elif il_rel == "충": s1 = 5
        else: s1 = 17
        p1 = int((s1 / 25) * 100)
        s2 = 5 
        n_rel, w_rel, si_rel = self.get_ji_rel(m_j[0], f_j[0]), self.get_ji_rel(m_j[1], f_j[1]), self.get_ji_rel(m_j[3], f_j[3]) 
        if n_rel in ["육합", "방합", "반합"]: s2 += 2
        elif n_rel == "충": s2 -= 1
        if w_rel in ["육합", "방합", "반합"]: s2 += 2
        elif w_rel == "충": s2 -= 1
        if si_rel in ["육합", "방합", "반합"]: s2 += 1
        s2 = max(0, min(10, s2))
        p2 = int((s2 / 10) * 100)
        m_ec, f_ec = self.count_elements(m_g, m_j), self.count_elements(f_g, f_j)
        s3 = 5
        for e in ['목','화','토','금','수']:
            if m_ec[e] == 0 and f_ec[e] >= 2: s3 += 2 
            if f_ec[e] == 0 and m_ec[e] >= 2: s3 += 2 
            if m_ec[e] >= 4 and f_ec[e] >= 4: s3 -= 2 
        s3 = max(0, min(10, s3))
        p3 = int((s3 / 10) * 100)
        s4 = 5
        bad_iljus, goran, nache = ["甲寅", "乙卯", "庚申", "辛酉", "戊辰", "戊戌"], ["甲寅", "乙巳", "丁巳", "戊申", "辛亥"], ["甲子", "乙巳", "丁卯", "庚午", "辛亥", "癸酉"] 
        m_ilju, f_ilju = m_g[2] + m_j[2], f_g[2] + f_j[2]
        if m_ilju in bad_iljus or m_ilju in goran or m_ilju in nache: s4 -= 1
        if f_ilju in bad_iljus or f_ilju in goran or f_ilju in nache: s4 -= 1
        s4 = max(0, min(5, s4))
        p4 = int((s4 / 5) * 100)
        s5 = min(10, self.daeun_score)
        p5 = int((s5 / 10) * 100)
        risk = 0.0
        if il_rel == "충": risk += 0.10 
        elif il_rel in ["형", "원진"]: risk += 0.05 
        def count_ss_groups(dc, chars):
            res = {'비겁':0, '식상':0, '재성':0, '관성':0, '인성':0}
            for c in chars:
                if c and c not in ["?", " ", "-"]:
                    try:
                        ss = get_group_ss(get_ss(dc, c))
                        if ss in res: res[ss] += 1
                    except: pass
            return res
        m_ss, f_ss = count_ss_groups(m_g[2], m_g + m_j), count_ss_groups(f_g[2], f_g + f_j)
        if m_ss['비겁'] >= 4: risk += 0.05 
        if m_ss['재성'] == 0: risk += 0.05 
        if f_ss['식상'] >= 4: risk += 0.05 
        if f_ss['관성'] >= 4 or f_ss['관성'] == 0: risk += 0.05 
        risk = min(0.20, risk) 
        p6_safety = int((1.0 - risk) * 100)
        base_bonus = 40 
        sub_total = base_bonus + s1 + s2 + s3 + s4 + s5
        self.final_score = max(40, min(100, int(sub_total * (1.0 - risk))))
        if self.final_score >= 90: self.grade = "천생연분 (최고의 인연)"
        elif self.final_score >= 85: self.grade = "상생연분 (함께하면 좋은 인연)"
        elif self.final_score >= 80: self.grade = "동행연분 (편안하고 안정적인 인연)"
        elif self.final_score >= 70: self.grade = "보완연분 (서로를 채워주는 인연)"
        elif self.final_score >= 60: self.grade = "성장연분 (이해하며 맞춰가는 인연)"
        else: self.grade = "조율연분 (인내와 배려가 필요한 인연)"
        self.details = [
            {"label": "내면의 유대감", "pct": p1, "color": "#9b59b6"},
            {"label": "환경 조화", "pct": p2, "color": "#2ecc71"},
            {"label": "기운 상호보완", "pct": p3, "color": "#3498db"},
            {"label": "특수 기운", "pct": p4, "color": "#f1c40f"},
            {"label": "대운 기상도 조화", "pct": p5, "color": "#8e44ad"},
            {"label": "리스크 방어력", "pct": p6_safety, "color": "#e74c3c"}
        ]

# ==============================================================================
# 4. 사이드바 UI (14종 상세 분석 항목 완벽 분기)
# ==============================================================================
with st.sidebar:
    st.title("🏮초연 전통명리 연구소")
    st.caption(f"{APP_VERSION}")
    st.markdown("---")

    main_category = st.selectbox(
        "📋 상담 분야 선택", 
        [
            "1. 개인 사주팔자 풀이 (종합)", 
            "2. 테마별 특성화 상담", 
            "3. 커플 연애/결혼운 (궁합) 풀이", 
            "4. 타 감명서 비교"
        ], 
        key="main_category"
    )

    u_product = "1-1. 사주팔자 및 대운 분석"

    if main_category == "1. 개인 사주팔자 풀이 (종합)":
        u_product = st.radio("상세 분석 항목:", ["1-1. 사주팔자와 운세풀이", "1-2. 올해 및 특정연도 운세 상세분석", "1-3. 이번달 및 특정월 운세 상세분석", "1-4. 특정 주간 및 특정일운 상세분석"], key="sub_cat_1")
        
        if u_product == "1-2. 올해 및 특정연도 운세 상세분석":
            curr_yr_val = dt_mod.datetime.now(pytz.timezone('Asia/Seoul')).year
            st.number_input("📅 분석할 특정 연도 (기본값: 올해)", min_value=1900, max_value=2050, value=curr_yr_val, key="target_year_input")
    elif main_category == "2. 테마별 특성화 상담":
        u_product = st.radio("특성화 상품 선택:", [
            "2-1. 재물운 특화 분석", 
            "2-2. 연애/결혼운 특화 분석",
            "2-3. 진학/입시운 특화 분석",
            "2-4. 직업/커리어운 특화 분석",
            "2-5. 건강운 특화 분석", 
            "2-6. 이사 택일",
            "2-7. 개업 택일"
        ], key="sub_cat_2")
    elif main_category == "3. 커플 연애/결혼운 (궁합) 풀이":
        u_product = st.radio("상세 분석 항목:", [
            "3-1. 연애/결혼운 (궁합) 풀이", 
            "3-2. 결혼 택일", 
            "3-3. 출산 택일"
        ], key="sub_cat_3")
    else:
        u_product = st.radio("비교 분석 대상:", [
            "4-1. 타 감명서 비교 (사주)",  
            "4-2. 타 감명서 비교 (궁합)"
        ], key="sub_cat_4")

    st.markdown("---")

    with st.expander("🔍 사주팔자 역산 검색", expanded=False):
        col_g1, col_g2 = st.columns(2)
        with col_g1: ry = st.text_input("년주", value="", key="u_ry_rev")
        with col_g2: rm = st.text_input("월주", value="", key="u_rm_rev")
        col_g3, col_g4 = st.columns(2)
        with col_g3: rd = st.text_input("일주", value="", key="u_rd_rev")
        with col_g4: rt = st.text_input("시주", value="", key="u_rt_rev")
        
        K2H_GAN = {'갑':'甲','을':'乙','병':'丙','정':'丁','무':'戊','기':'己','경':'庚','신':'辛','임':'壬','계':'癸'}
        K2H_JI = {'자':'子','축':'丑','인':'寅','묘':'卯','진':'辰','사':'巳','오':'午','미':'未','신':'申','유':'酉','술':'戌','해':'亥'}
        
        if st.button("🔍 생년월일 자동입력", use_container_width=True, key="btn_user_rev"):
            _ry, _rm, _rd = ry.replace("년","").replace(" ","")[:2], rm.replace("월","").replace(" ","")[:2], rd.replace("일","").replace(" ","")[:2]
            if len(_ry)==2 and len(_rm)==2 and len(_rd)==2:
                ry_h = K2H_GAN.get(_ry[0], _ry[0]) + K2H_JI.get(_ry[1], _ry[1])
                rm_h = K2H_GAN.get(_rm[0], _rm[0]) + K2H_JI.get(_rm[1], _rm[1])
                rd_h = K2H_GAN.get(_rd[0], _rd[0]) + K2H_JI.get(_rd[1], _rd[1])
                klc_find = KoreanLunarCalendar(); found = False
                for y in range(2026, 1899, -1):
                    klc_find.setSolarDate(y, 7, 1); gj_y = klc_find.getChineseGapJaString().split()
                    if gj_y and gj_y[0][:2] == ry_h:
                        curr_dt = dt_mod.date(y+1, 2, 28)
                        while curr_dt >= dt_mod.date(y, 1, 1):
                            klc_find.setSolarDate(curr_dt.year, curr_dt.month, curr_dt.day)
                            gj = klc_find.getChineseGapJaString().split()
                            if len(gj) >= 3 and gj[0][:2] == ry_h and gj[1][:2] == rm_h and gj[2][:2] == rd_h:
                                st.session_state.s_y, st.session_state.s_m, st.session_state.s_d = curr_dt.year, curr_dt.month, curr_dt.day
                                time_map_rev = {'子':'00:30 ~ 01:29 (朝子)시','丑':'01:30 ~ 03:29 (丑)시','寅':'03:30 ~ 05:29 (寅)시','卯':'05:30 ~ 07:29 (卯)시','辰':'07:30 ~ 09:29 (辰)시','巳':'09:30 ~ 11:29 (巳)시','午':'11:30 ~ 13:29 (午)시','未':'13:30 ~ 15:29 (未)시','申':'15:30 ~ 17:29 (申)시','酉':'17:30 ~ 19:29 (酉)시','戌':'19:30 ~ 21:29 (戌)시','亥':'21:30 ~ 23:29 (亥)시'}
                                if rt:
                                    ji_char = rt.replace("시","").replace(" ","")[-1]
                                    rt_h = K2H_JI.get(ji_char, ji_char)
                                    if rt_h in time_map_rev: st.session_state.s_t = time_map_rev[rt_h]
                                found = True
                                is_leap = getattr(klc_find, 'isIntercalary', False)
                                leap_str = "윤달" if is_leap else "평달"
                                st.success(f"✅ 양력{curr_dt.year}년 {curr_dt.month:02d}월 {curr_dt.day:02d}일 음력{klc_find.lunarYear}년 {klc_find.lunarMonth:02d}월 {klc_find.lunarDay:02d}일 ({leap_str})")
                                break
                            curr_dt -= dt_mod.timedelta(days=1)
                        if found: break
                if not found: st.error("일치하는 날짜가 없습니다.")
            else: st.warning("간지를 2글자씩 정확히 입력하세요.")

    st.markdown("---")
    st.markdown("<div style='font-weight:900; color:#1A237E; margin-bottom:5px;'>👤 신청인 기본 정보</div>", unsafe_allow_html=True)
    u_name = st.text_input("이름", value="", placeholder="홍길동", key="u_n")
    u_gender = st.selectbox("성별", ["남성", "여성"], index=0, key="u_g")
    u_marital = st.selectbox("혼인여부", ["선택", "미혼", "기혼", "돌싱"], index=1, key="u_m_stat")
    u_cal = st.selectbox("달력", ["양력", "음력(평달)", "음력(윤달)"], index=0, key="u_c")
    
    col1, col2, col3 = st.columns(3)
    u_y = col1.number_input("년", 1900, 2050, value=st.session_state.get('s_y', 2010), key="s_y")
    u_m = col2.number_input("월", 1, 12, value=st.session_state.get('s_m', 1), key="s_m")
    u_d = col3.number_input("일", 1, 31, value=st.session_state.get('s_d', 1), key="s_d")
    
    idx_list = ["시간 모름", "00:30 ~ 01:29 (朝子)시", "01:30 ~ 03:29 (丑)시", "03:30 ~ 05:29 (寅)시", "05:30 ~ 07:29 (卯)시", "07:30 ~ 09:29 (辰)시", "09:30 ~ 11:29 (巳)시", "11:30 ~ 13:29 (午)시", "13:30 ~ 15:29 (未)시", "15:30 ~ 17:29 (申)시", "17:30 ~ 19:29 (酉)시", "19:30 ~ 21:29 (戌)시", "21:30 ~ 23:29 (亥)시", "23:30 ~ 00:29 (夜子)시"]
    u_t = st.selectbox("태어난 시간", idx_list, index=0, key="s_t")
    
    is_2person_product = (main_category == "3. 커플 연애/결혼운 (궁합) 풀이") or (u_product == "4-2. 타 감명서 비교 (궁합)")
    
    p_name, p_gender, p_marital, p_cal, p_y, p_m, p_d, p_t = "", "여성", "미혼", "양력", 0, 0, 0, "시간 모름"
    other_reading_text = ""
    run_delivery_calc = False  
    start_date, end_date = None, None
    baby_gender = "미정"
    compare_mode = "자동대조"
    run_iljin_calc = False

    if main_category in ["1. 개인 사주팔자 풀이 (종합)", "2. 테마별 특성화 상담"]:
        if u_product in ["1-1. 사주팔자 및 대운 분석", "1-4. 특정 주간 및 특정일운 상세분석"]:
            st.markdown("<hr style='border:1px dashed #1A237E; margin:15px 0;'>", unsafe_allow_html=True)
            run_iljin_calc = st.checkbox("🔮 일운 운세 분석 가동", value=False)
            if run_iljin_calc:
                if 'target_date' not in st.session_state: st.session_state['target_date'] = dt_mod.datetime.now(pytz.timezone('Asia/Seoul')).date()
                st.session_state['target_date'] = st.date_input("분석할 일자 선택", value=st.session_state['target_date'])

    elif main_category == "4. 타 감명서 비교":
        st.markdown("<hr style='border:1px dashed #2E7D32; margin:15px 0;'>", unsafe_allow_html=True)
        compare_mode = st.radio("대조 분석 모드", ["전통 명리학과 1:1 자동 대조", "외부 타 감명서 원문 대조"], index=0)
        if compare_mode == "외부 타 감명서 원문 대조":
            other_reading_text = st.text_area("타 감명서 원문 텍스트 입력", value="", height=180)

    if is_2person_product:
        st.markdown("<hr style='border:1px dashed #C62828; margin:15px 0;'>", unsafe_allow_html=True)
        
        with st.expander("🔍 상대방 사주팔자 역산 검색", expanded=False):
            p_col_g1, p_col_g2 = st.columns(2)
            with p_col_g1: p_ry = st.text_input("상대방 년주", value="", key="p_ry_rev")
            with p_col_g2: p_rm = st.text_input("상대방 월주", value="", key="p_rm_rev")
            p_col_g3, p_col_g4 = st.columns(2)
            with p_col_g3: p_rd = st.text_input("상대방 일주", value="", key="p_rd_rev")
            with p_col_g4: p_rt = st.text_input("상대방 시주", value="", key="p_rt_rev")
            
            if st.button("🔍 상대방 생년월일 자동입력", use_container_width=True, key="btn_partner_rev"):
                _p_ry = p_ry.replace("년","").replace(" ","")[:2]
                _p_rm = p_rm.replace("월","").replace(" ","")[:2]
                _p_rd = p_rd.replace("일","").replace(" ","")[:2]
                if len(_p_ry)==2 and len(_p_rm)==2 and len(_p_rd)==2:
                    p_ry_h = K2H_GAN.get(_p_ry[0], _p_ry[0]) + K2H_JI.get(_p_ry[1], _p_ry[1])
                    p_rm_h = K2H_GAN.get(_p_rm[0], _p_rm[0]) + K2H_JI.get(_p_rm[1], _p_rm[1])
                    p_rd_h = K2H_GAN.get(_p_rd[0], _p_rd[0]) + K2H_JI.get(_p_rd[1], _p_rd[1])
                    klc_find_p = KoreanLunarCalendar(); found_p = False
                    for y in range(2026, 1899, -1):
                        klc_find_p.setSolarDate(y, 7, 1); gj_y = klc_find_p.getChineseGapJaString().split()
                        if gj_y and gj_y[0][:2] == p_ry_h:
                            curr_dt_p = dt_mod.date(y+1, 2, 28)
                            while curr_dt_p >= dt_mod.date(y, 1, 1):
                                klc_find_p.setSolarDate(curr_dt_p.year, curr_dt_p.month, curr_dt_p.day)
                                gj = klc_find_p.getChineseGapJaString().split()
                                if len(gj) >= 3 and gj[0][:2] == p_ry_h and gj[1][:2] == p_rm_h and gj[2][:2] == p_rd_h:
                                    st.session_state.p_y_in = curr_dt_p.year
                                    st.session_state.p_m_in = curr_dt_p.month
                                    st.session_state.p_d_in = curr_dt_p.day
                                    time_map_rev_p = {'子':'00:30 ~ 01:29 (朝子)시','丑':'01:30 ~ 03:29 (丑)시','寅':'03:30 ~ 05:29 (寅)시','卯':'05:30 ~ 07:29 (卯)시','辰':'07:30 ~ 09:29 (辰)시','巳':'09:30 ~ 11:29 (巳)시','午':'11:30 ~ 13:29 (午)시','未':'13:30 ~ 15:29 (未)시','申':'15:30 ~ 17:29 (申)시','酉':'17:30 ~ 19:29 (酉)시','戌':'19:30 ~ 21:29 (戌)시','亥':'21:30 ~ 23:29 (亥)시'}
                                    if p_rt:
                                        ji_char_p = p_rt.replace("시","").replace(" ","")[-1]
                                        p_rt_h = K2H_JI.get(ji_char_p, ji_char_p)
                                        if p_rt_h in time_map_rev_p: st.session_state.p_t_in = time_map_rev_p[p_rt_h]
                                    found_p = True
                                    is_leap_p = getattr(klc_find_p, 'isIntercalary', False)
                                    leap_str_p = "윤달" if is_leap_p else "평달"
                                    st.success(f"✅양력{curr_dt_p.year}년 {curr_dt_p.month:02d}월 {curr_dt_p.day:02d}일 음력{klc_find_p.lunarYear}년 {klc_find_p.lunarMonth:02d}월 {klc_find_p.lunarDay:02d}일 ({leap_str_p})")
                                    break
                                curr_dt_p -= dt_mod.timedelta(days=1)
                            if found_p: break
                    if not found_p: st.error("일치하는 날짜가 없습니다.")
                else: st.warning("간지를 2글자씩 정확히 입력하세요.")

        st.markdown("<div style='font-weight:900; color:#C62828; margin-bottom:5px;'>💕 상대방 기본 정보</div>", unsafe_allow_html=True)
        p_name = st.text_input("이름", value="", placeholder="이영희", key="p_n")
        p_gender_default = "여성" if u_gender == "남성" else "남성"
        p_gender = st.selectbox("성별", ["남성", "여성"], index=["남성", "여성"].index(p_gender_default), key="p_g")
        p_marital = st.selectbox("혼인여부", ["미혼", "기혼", "돌싱"], index=0, key="p_m_stat")
        p_cal = st.selectbox("달력", ["양력", "음력(평달)", "음력(윤달)"], index=0, key="p_c")
        
        if 'p_y_in' not in st.session_state: st.session_state['p_y_in'] = 2010
        if 'p_m_in' not in st.session_state: st.session_state['p_m_in'] = 1
        if 'p_d_in' not in st.session_state: st.session_state['p_d_in'] = 1
        if 'p_t_key' not in st.session_state: st.session_state['p_t_key'] = idx_list[0]
        if 'p_t_select_key' not in st.session_state: st.session_state['p_t_select_key'] = st.session_state['p_t_key']

        p_col1, p_col2, p_col3 = st.columns(3)
        p_y = p_col1.number_input("년", 1900, 2050, key="p_y_in")
        p_m = p_col2.number_input("월", 1, 12, key="p_m_in")
        p_d = p_col3.number_input("일", 1, 31, key="p_d_in")
        
        p_t_idx = idx_list.index(st.session_state['p_t_select_key']) if st.session_state['p_t_select_key'] in idx_list else 0
        p_t = st.selectbox("태어난 시간", idx_list, index=p_t_idx, key="p_t_select_key")
        st.session_state['p_t_key'] = p_t
        
        current_year = dt_mod.datetime.now().year 
        f_year = u_y if u_gender == "여성" else p_y

        if u_product in ["3-2. 결혼 택일", "3-3. 출산 택일"] or ((current_year - f_year + 1) <= 49 and main_category == "3. 커플 연애/결혼운 (궁합) 풀이"):
            st.markdown("<hr style='border:1px solid #ddd; margin:15px 0;'>", unsafe_allow_html=True)
            
            with st.expander("📅 택일 달력 기간 선택", expanded=(u_product in ["3-2. 결혼 택일", "3-3. 출산 택일"])):
                baby_gender = st.radio("태아 성별 (출산택일 전용)", ["미정", "남아", "여아"], index=0)
                start_date = st.date_input("탐색 시작일", value=dt_mod.date.today())
                end_date = st.date_input("탐색 종료일", value=dt_mod.date.today() + dt_mod.timedelta(days=30))
                
                st.markdown("<div style='margin-top:15px;'></div>", unsafe_allow_html=True)
                run_delivery_calc = st.checkbox("✅ 택일 가동 확정 (체크 후 하단 메인 가동버튼 클릭)", value=(u_product in ["3-2. 결혼 택일", "3-3. 출산 택일"]))

    st.markdown("---")
    btn_single = st.button("🚀 초연 전통명리 사주풀이 가동", key="btn_run", use_container_width=True, type="primary")

    if st.button("🖨️ 풀이 결과 인쇄 / PDF 저장", key="btn_print", use_container_width=True, type="secondary"):
        components.html("<script>window.parent.print();</script>", height=0)

    if btn_single:
        is_compare_type = (main_category == "4. 타 감명서 비교")

        if not u_name.strip(): 
            st.warning("⚠️ 신청인의 이름을 입력해 주세요.")
        elif is_compare_type and compare_mode == "외부 타 감명서 원문 대조" and not other_reading_text.strip():
            st.warning("⚠️ 타 감명서 원문을 입력해 주세요.")
        elif is_2person_product and not p_name.strip(): 
            st.warning("⚠️ 상대방의 이름을 입력해 주세요.")
        else:
            st.session_state['app_running'] = True
            
            for key in ['saved_report_html', 'saved_report_2', 'saved_report_gh_cover', 'saved_report_gh_m', 'saved_report_gh_f', 'saved_report_gh_g', 'saved_report_del', 'saved_report_iljin']:
                if key in st.session_state: del st.session_state[key]

            if main_category in ["1. 개인 사주팔자 풀이 (종합)", "2. 테마별 특성화 상담"] and run_iljin_calc:
                st.session_state['need_calc'] = True
                st.session_state['run_waterfall'] = True
            elif is_2person_product and run_delivery_calc:
                st.session_state['need_calc'] = True
                st.session_state['run_delivery_only'] = True
            else:
                st.session_state['need_calc'] = True
                st.session_state['run_waterfall'] = False
                st.session_state['run_delivery_only'] = False
            
            st.rerun()

# ==============================================================================
# 5. 분석 가동 로직 (Ver 50.4 완결본)
# ==============================================================================
if st.session_state.get('need_calc', False):
    spinner_msg = f"⏳ [초연 전통명리 정밀 분석({u_product}) 연산 중....]"
    with st.spinner(spinner_msg):
        try:
            name = u_name if u_name.strip() else "홍길동"
            disp_name = name

            kst = pytz.timezone('Asia/Seoul')
            curr_dt_sys = dt_mod.datetime.now(kst)
            curr_y = curr_dt_sys.year
            curr_m = curr_dt_sys.month
            u_age = curr_y - u_y + 1
            base_dt = dt_mod.datetime(u_y, u_m, u_d, 12, 0)
            
            klc = KoreanLunarCalendar()
            if u_cal == "양력": klc.setSolarDate(u_y, u_m, u_d)
            elif u_cal == "음력(평달)": klc.setLunarDate(u_y, u_m, u_d, False)
            else: klc.setLunarDate(u_y, u_m, u_d, True)
            
            is_leap = getattr(klc, 'isIntercalary', False)
            leap_str = "윤달" if is_leap else "평달"
            sol_str = f"{klc.solarYear}년 {klc.solarMonth:02d}월 {klc.solarDay:02d}일"
            lun_str = f"{klc.lunarYear}년 {klc.lunarMonth:02d}월 {klc.lunarDay:02d}일 ({leap_str})"
            
            true_ym, true_mm, _ = get_true_year_month_pillar(u_y, u_m, u_d, 12, 0)
            ys, yb = true_ym[0], true_ym[1]
            ms, mb = true_mm[0], true_mm[1]
            
            gj = klc.getChineseGapJaString().split()
            ds, db = gj[2][0], gj[2][1]
            hs, hb = get_time_ganji(ds, u_t, base_dt)
            
            gans, jjis = [hs, ds, ms, ys], [hb, db, mb, yb]
            applicant_bazi = [f"{hs}{hb}", f"{ds}{db}", f"{ms}{mb}", f"{ys}{yb}"]

            st.session_state['global_gans'] = gans
            st.session_state['global_jjis'] = jjis
            st.session_state['global_ds'] = ds
            st.session_state['global_db'] = db

            adj_mins = get_total_time_adjustment(base_dt)
            utc_dt = base_dt - dt_mod.timedelta(hours=9) + dt_mod.timedelta(minutes=adj_mins)
            order = 1 if (GAN.index(ys)%2==0) == (u_gender=='남성') else -1
            calc_d = get_daeun_su_accurate(utc_dt, order)
            current_daewun_age = ((u_age - calc_d) // 10) * 10 + calc_d
            
            base_y_idx = (curr_y - 1984) % 60
            curr_y_ganji = GAN[base_y_idx % 10] + JI[base_y_idx % 12]
            time_str = f" {u_t.split('(')[0].strip()} ({hb})시" if u_t != "시간 모름" else ""
            
            def td(c, size="18px"): return f"<td class='color-{get_color(c)}' style='font-size:{size}; font-weight:900; border:1px solid #444 !important;'><span style='color:inherit !important;'>{('?' if c in ['?',' ','-'] else c)}</span></td>"
            
            p_icon = "♂️" if u_gender == "남성" else "♀️"
            p_color = "#1A237E" if u_gender == "남성" else "#D50000"
            today_str = (dt_mod.datetime.utcnow() + dt_mod.timedelta(hours=9)).strftime("%Y년 %m월 %d일")

            user_ilju_key = f"{ds}{db}"
            ilju_full_db = choyeon_db.get("ilju_full_master", {})
            ilju_master_data = ilju_full_db.get(user_ilju_key, {})
            ilju_summary_text = ilju_master_data.get('summary', f"{user_ilju_key}의 고유한 본성")

            intro_html = """
    <hr style="border: 0; border-top: 2px solid #000000; margin: 25px 0;">
    <div style="margin: 0; padding: 0;">
        <p class="ai-body-p" style="margin-top: 0; margin-bottom: 6px; font-weight: 600; text-align: justify; text-indent: 0; color: #000000;">
            <b>"초연 전통 명리학"</b>은 태어난 연·월·일·시의 정통 <b>사주팔자 원국과 격국, 십성, 12운성 및 신살</b>을 바탕으로 내담자의 타고난 천성과 삶의 궤적을 맑고 깊이 있게 통변합니다.
        </p> 
        <p class="ai-body-p" style="margin-top: 0; margin-bottom: 0; font-weight: 600; text-align: justify; text-indent: 0; color: #000000;">
            따라서, 본 감명서는 고전 명리의 이치에 철저히 입각하여 인생의 길흉화복과 시기별 흐름을 가장 정교하고 품격 있게 제시합니다.
        </p>
    </div>
    <hr style="border: 0; border-top: 2px solid #000000; margin: 25px 0;">
"""

            hap_chung_hyoung_pa_hae = (
                f"일-월지:{get_ji_rel_set(db, mb)}, 일-년지:{get_ji_rel_set(db, yb)}, "
                f"일-시지:{get_ji_rel_set(db, hb)}, 월-년지:{get_ji_rel_set(mb, yb)}"
            )

            cover_html = (
                f"<div class='report-page cover-page' style='padding:0; margin:0; width:100%; height:297mm; display:flex; flex-direction:column; justify-content:center; align-items:center; page-break-after: always; -webkit-print-color-adjust: exact;'>\n"
                f"    <div style='border: 4px solid #1A237E; padding: 50px 30px; border-radius: 20px; text-align: center; background: white; width: 80%; max-width: 600px; box-shadow: 0 10px 25px rgba(0,0,0,0.1); margin: auto;'>\n"
                f"        <div style='border-bottom:4px double #1A237E; padding-bottom:20px; margin-bottom:40px;'>\n"
                f"            <h1 class='title-gothic' style='font-family: \"Nanum Gothic\", sans-serif; font-size: 36px !important; font-weight: 900; margin:0 !important;'>초연 전통 명리사주 풀이</h1>\n"
                f"            <div style='text-align: right; margin-top: 10px;'>\n"
                f"                <span class='ver-gothic' style='font-family: \"Nanum Gothic\", sans-serif; font-size: 14px; font-weight: 700; letter-spacing: 1px;'>{APP_VERSION}</span>\n"
                f"            </div>\n"
                f"        </div>\n"
                f"        <div style='background:#F8F9FA; border: 1px solid #E8EAF6; padding: 30px 20px; border-radius: 15px;'>\n"
                f"            <h2 style='font-family: \"Nanum Gothic\", sans-serif; font-size: 24px; font-weight: 800; color: {p_color}; margin-bottom: 20px;'>{p_icon} 신청인 : {u_name} 님</h2>\n"
                f"            <div style='font-family: \"Nanum Gothic\", sans-serif; font-size: 15px; font-weight: 600; color: #555; line-height: 1.8;'>\n"
                f"                <p style='margin: 0; white-space: nowrap;'>[양력] {sol_str} | [음력] {lun_str}</p>\n"
                f"                <p style='margin: 5px 0 0 0; color: #D50000; white-space: nowrap;'>{time_str}</p>\n"
                f"            </div>\n"
                f"        </div>\n"
                f"        <p style='font-family: \"Nanum Gothic\", sans-serif; font-size: 18px; margin-top: 50px; font-weight: 800;'>{today_str}</p>\n"
                f"        <p style='font-family: \"Nanum Gothic\", sans-serif; font-size: 22px; font-weight: 800; color: #1A237E; margin-top: 20px;'>초연 전통명리 연구소</p>\n"
                f"    </div>\n"
                f"</div>"
            )
            st.session_state['saved_report_cover'] = cover_html

            if u_product == "1-1. 사주팔자와 운세풀이":
                report_title = "🎯 사주팔자와 운세풀이"
            elif u_product == "1-2. 올해 및 특정연도 운세 상세분석":
                report_title = "🎯 올해 및 특정연도 운세 상세분석"
            elif u_product == "1-3. 이번달 및 특정월 운세 상세분석":
                report_title = "🎯 이번달 및 특정월 운세 상세분석"
            elif u_product == "1-4. 특정 주간 및 특정일운 상세분석":
                report_title = "🎯 특정 주간 및 특정일운 상세분석"
            elif u_product == "2-1. 재물운 특화 분석":
                report_title = "🎯 재물운 특화 정밀 분석"
            elif u_product == "2-2. 연애/결혼운 특화 분석":
                report_title = "🎯 연애/결혼운 특화 정밀 분석"
            elif u_product == "2-3. 진학/입시운 특화 분석":
                report_title = "🎯 진학/입시운 특화 정밀 분석"
            elif u_product == "2-4. 직업/커리어운 특화 분석":
                report_title = "🎯 직업/커리어운 특화 정밀 분석"
            elif u_product == "2-5. 건강운 특화 분석":
                report_title = "🎯 건강운 특화 정밀 분석"
            elif u_product == "2-6. 이사 택일":
                report_title = "🎯 이사 택일 추천 리포트"
            elif u_product == "2-7. 개업 택일":
                report_title = "🎯 개업 택일 추천 리포트"
            elif u_product == "3-1. 연애/결혼운 (궁합) 풀이":
                report_title = "🎯 커플 연애/결혼운 정밀 궁합 분석"
            elif u_product == "3-2. 결혼 택일":
                report_title = "🎯 최고의 결혼 길일 추천 리포트"
            elif u_product == "3-3. 출산 택일":
                report_title = "🎯 새 생명 마중 출산 길일 추천 리포트"
            elif u_product == "4-1. 타 감명서 비교 (사주)":
                report_title = "🎯 사주 감명서 학술 검증 및 1:1 대조 리포트"
            elif u_product == "4-2. 타 감명서 비교 (궁합)":
                report_title = "🎯 궁합 감명서 학술 검증 및 1:1 대조 리포트"
            else:
                report_title = "🎯 사주팔자 정밀 분석"

            ji_rel_rows = ""
            for l_idx, r_idx in enumerate([1, 2, 0, 3]):
                b_bot = "1px solid #444 !important" if l_idx == 3 else "0px solid transparent !important"
                b_top = "0px solid transparent !important"
                cells = "".join([f"<td style='color:{('#D50000' if ci==r_idx else ('#000' if get_ji_rel_set(jjis[r_idx], jjis[ci])!='-' else '#BBB'))}; font-weight:900; border-top:{b_top}; border-bottom:{b_bot}; border-left:1px solid #444 !important; border-right:1px solid #444 !important;'><span style='color:inherit !important;'>{('←('+jjis[r_idx]+')→' if ci==r_idx else get_ji_rel_set(jjis[r_idx], jjis[ci]))}</span></td>" for ci in range(4)])
                lbl = f"<td rowspan='4' class='header-cell-main' style='border-right: 1px solid #444 !important; border-left: 1px solid #444 !important; border-bottom: 1px solid #444 !important; border-top: 0px solid transparent !important; font-size:14px !important;'><span style='color:inherit !important;'>합충형파해</span></td>" if l_idx==0 else ""
                ji_rel_rows += f"<tr style='border:none;'>{lbl}{cells}</tr>"

            info_h = f"<div style='text-align:center; font-family:\"Nanum Gothic\", sans-serif; margin-bottom:15px; line-height:1.5;'><span style='font-size:18px; font-weight:900; color:{p_color}; white-space:nowrap;'>{p_icon} {disp_name}님 ({u_gender}, {u_marital}, {u_age}세)</span><br><span style='font-size:14px; font-weight:bold; color:#555; white-space:nowrap;'>[양력: {sol_str} | 음력: {lun_str} {time_str}]</span></div>"

            table_html = f"""<div style='text-align:center; margin-bottom:10px;'>{info_h}</div>
<table class='result-table' style='width:100%; border-collapse:collapse; text-align:center;'>
<tr class='top-header-cell'>
<td style='border:1px solid #444; color:#FFFFFF !important; font-weight:900;'><span style='color:#FFFFFF !important;'>구분</span></td>
<td style='border:1px solid #444; color:#FFFFFF !important; font-weight:900;'><span style='color:#FFFFFF !important;'>시주</span></td>
<td style='border:1px solid #444; color:#FFFFFF !important; font-weight:900;'><span style='color:#FFFFFF !important;'>일주</span></td>
<td style='border:1px solid #444; color:#FFFFFF !important; font-weight:900;'><span style='color:#FFFFFF !important;'>월주</span></td>
<td style='border:1px solid #444; color:#FFFFFF !important; font-weight:900;'><span style='color:#FFFFFF !important;'>년주</span></td>
</tr>
<tr><td class='header-cell-main' style='border:1px solid #444; background:#f5f5f5; font-weight:900; font-size:14px !important;'><span style='color:inherit !important;'>천간합충</span></td>{"".join([f"<td style='border:1px solid #444;'><span style='color:inherit !important;'>{get_gan_rel_all(i, gans)}</span></td>" for i in range(4)])}</tr>
<tr><td class='header-cell-main' style='border:1px solid #444; background:#f5f5f5; font-weight:900; font-size:14px !important;'><span style='color:inherit !important;'>천간십성</span></td><td style='border:1px solid #444;'><span style='color:inherit !important;'>{get_ss(ds,hs)}</span></td><td style='border:1px solid #444;'><span style='color:#D50000; font-weight:900;'>日元</span></td><td style='border:1px solid #444;'><span style='color:inherit !important;'>{get_ss(ds,ms)}</span></td><td style='border:1px solid #444;'><span style='color:inherit !important;'>{get_ss(ds,ys)}</span></td></tr>
<tr><td class='header-cell-main' style='border:1px solid #444; background:#E8EAF6; color:#1A237E; font-weight:900; font-size:14px !important;'><span style='color:inherit !important;'>천간</span></td>{td(hs)}{td(ds)}{td(ms)}{td(ys)}</tr>
<tr><td class='header-cell-main' style='border:1px solid #444; background:#E8EAF6; color:#1A237E; font-weight:900; font-size:14px !important;'><span style='color:inherit !important;'>지지</span></td>{td(hb)}{td(db)}{td(mb)}{td(yb)}</tr>
<tr><td class='header-cell-main' style='border:1px solid #444; background:#f5f5f5; font-weight:900; font-size:14px !important;'><span style='color:inherit !important;'>지지십성</span></td><td style='border:1px solid #444;'><span style='color:inherit !important;'>{get_ss(ds,hb)}</span></td><td style='border:1px solid #444;'><span style='color:inherit !important;'>{get_ss(ds,db)}</span></td><td style='border:1px solid #444;'><span style='color:inherit !important;'>{get_ss(ds,mb)}</span></td><td style='border:1px solid #444;'><span style='color:inherit !important;'>{get_ss(ds,yb)}</span></td></tr>
<tr><td class='header-cell-main' style='padding:0; border:1px solid #444; background:#f5f5f5; font-weight:900; font-size:14px !important;'><span style='color:inherit !important;'>지장간</span></td>{"".join([f"<td style='padding:0; border:1px solid #444;'><span style='color:inherit !important;'>{get_jijanggan_full(ds, jjis[i])}</span></td>" for i in range(4)])}</tr>
{ji_rel_rows}
<tr><td class='header-cell-main' style='border:1px solid #444 !important; background:#f5f5f5; font-weight:900; font-size:14px !important;'><span style='color:inherit !important;'>십이운성</span></td>{"".join([f"<td style='color:#0D47A1; border:1px solid #444 !important;'><span style='color:inherit !important;'>{get_unsung(ds, jjis[i])}</span></td>" for i in range(4)])}</tr>
<tr><td class='header-cell-main' style='border:1px solid #444 !important; background:#f5f5f5; font-weight:900; font-size:14px !important;'><span style='color:inherit !important;'>십이신살</span></td>{"".join([f"<td style='color:#C62828; border:1px solid #444 !important;'><span style='color:inherit !important;'>{get_12_shinsal(yb, jjis[i])}</span></td>" for i in range(4)])}</tr>
<tr><td class='header-cell-main' style='border:1px solid #444 !important; background:#f5f5f5; font-weight:900; font-size:14px !important;'><span style='color:inherit !important;'>일반신살</span></td>{"".join([f"<td style='vertical-align:top; padding:2px; border:1px solid #444 !important;'><span style='color:inherit !important;'>{'<br>'.join(get_general_shinsal_filtered(i, gans, jjis, u_gender)) if get_general_shinsal_filtered(i, gans, jjis, u_gender) else '-'}</span></td>" for i in range(4)])}</tr>
</table>
"""
            calc_gyukgook, gyukgook_detail = get_gyukgook_detailed(ds, ys, ms, hs, mb)

            SEASON_SOLAR_TERMS = {
                '寅': '입춘과 경칩 사이의 이른 봄(寅月)', '卯': '경칩과 청명 사이의 완연한 봄(卯月)',
                '辰': '청명과 입하 사이의 봄과 여름의 환절기(辰月)', '巳': '입하와 망종 사이의 이른 여름(巳月)',
                '午': '망종과 소서 사이의 완연한 여름(午月)', '未': '소서와 입추 사이의 가장 무더운 여름(未月)',
                '申': '입추와 백로 사이의 이른 가을(申月)', '酉': '백로와 한로 사이의 완연한 가을(酉月)',
                '戌': '한로와 입동 사이의 가을과 겨울의 환절기(戌月)', '亥': '입동과 대설 사이의 이른 겨울(亥月)',
                '子': '대설과 소한 사이의 완연한 한겨울(子月)', '丑': '소한과 입춘 사이의 가장 추운 겨울(丑月)'
            }
            wol_korean_str = SEASON_SOLAR_TERMS.get(mb, f"{mb}월")
            gyuk_name = calc_gyukgook

            ilju_struct_db = choyeon_db.get("ilju_structure", {})
            struct_data = ilju_struct_db.get(user_ilju_key, [])
            if len(struct_data) >= 3:
                action_type = struct_data[1]
                main_tendency = struct_data[2]
            else:
                action_type = "자율활동형"
                main_tendency = "독자적인 삶의 무대를 개척하는"

            ilju_full_db = choyeon_db.get("ilju_full_master", {})
            ilju_master_data = ilju_full_db.get(user_ilju_key, {})
            ilju_summary_text = ilju_master_data.get('summary', '고유의 역량을 품은')

            choyeon_golden_text = f"""
<div style='font-family: "Nanum Myeongjo", "바탕체", Batang, serif; font-size: 15px; line-height: 1.8; color: #000000; margin-bottom: 20px;'>
    <p style='text-indent: 1.0em; text-align: justify; margin-bottom: 5px;'>
        정통 명리학적으로 풀이하면 <b>{disp_name}님</b>은 <b>{wol_korean_str}</b>에 <b>'{gyuk_name}'</b>의 그릇을 갖추고 태어나셨으며, 성격은 <b>'{action_type}'</b>으로 <b>'{main_tendency}'</b> 성향이 있습니다.
    </p>
</div>
<hr style="border: 0; border-top: 2px solid #000000; margin: 25px 0;">
"""

            gen_shinsal_list = []
            for i in range(4):
                raw_tags = get_general_shinsal_filtered(i, gans, jjis, u_gender)
                for tag in raw_tags:
                    if ">" in tag and "<" in tag: gen_shinsal_list.append(tag.split('>')[1].split('<')[0])
            shinsal_str = ", ".join(list(dict.fromkeys(gen_shinsal_list))) if gen_shinsal_list else "특이 신살 없음"
            
            s12_list = [get_12_shinsal(yb, j) for j in jjis if get_12_shinsal(yb, j) != "-"]
            s12_str = ", ".join(list(dict.fromkeys(s12_list))) if s12_list else "특이 12신살 없음"
            
            samhyung_warn_list = []
            jjis_set = set(jjis)
            if len({'寅', '巳', '申'}.intersection(jjis_set)) == 3:
                samhyung_warn_list.append("원국 인사신(寅巳申) 삼형살 전면 성립")
            elif len({'寅', '巳', '申'}.intersection(jjis_set)) == 2:
                missing = list({'寅', '巳', '申'} - jjis_set)[0]
                samhyung_warn_list.append(f"원국 인사신(寅巳申) 가형 상태 (운에서 '{missing}' 도래 시 삼형 완성)")

            if len({'丑', '戌', '未'}.intersection(jjis_set)) == 3:
                samhyung_warn_list.append("원국 축술미(丑戌未) 삼형살 전면 성립")
            elif len({'丑', '戌', '未'}.intersection(jjis_set)) == 2:
                missing = list({'丑', '戌', '未'} - jjis_set)[0]
                samhyung_warn_list.append(f"원국 축술미(丑戌未) 가형 상태 (운에서 '{missing}' 도래 시 삼형 완성)")

            samhyung_warn = " / ".join(samhyung_warn_list) if samhyung_warn_list else "해당 없음"

            counts = {"목":0,"화":0,"토":0,"금":0,"수":0}
            for char in gans + jjis:
                if char != "?": counts[get_color(char)] += 1
            
            guiin_map = {'甲':'丑, 未','乙':'子, 申','丙':'酉, 亥','丁':'酉, 亥','戊':'丑, 未','己':'子, 申','庚':'丑, 未','辛':'午寅','壬':'卯巳','癸':'卯, 巳'}
            guiin_str = guiin_map.get(ds, '없음')
            direction_str = "순행" if order == 1 else "역행"
            n_gong = calculate_gongmang(ys, yb)
            i_gong = calculate_gongmang(ds, db)
            
            gongmang_targets = n_gong.split(',') + i_gong.split(',')
            gongmang_hits = []
            if yb in gongmang_targets: gongmang_hits.append(f"년지({yb})")
            if mb in gongmang_targets: gongmang_hits.append(f"월지({mb})")
            if db in gongmang_targets: gongmang_hits.append(f"일지({db})")
            if hb in gongmang_targets: gongmang_hits.append(f"시지({hb})")
            gongmang_actual = ", ".join(gongmang_hits) + "에 공망 작용함" if gongmang_hits else "사주 원국 내 공망 작용 없음"
            
            cur_samjae = get_samjae(yb, curr_y_ganji[1])
            samjae_color = "#C62828" if cur_samjae != "해당 없음" else "#555"

            master_bar_html = f"<div style='border:2px solid #3E2723; margin-top:20px; padding:8px; display:flex; justify-content:space-between; font-weight:900; font-size:12px; border-radius:8px; white-space:nowrap;'><div>🔢 대운수: {calc_d}</div><div>💥 오행: 木({counts['목']}) 火({counts['화']}) 土({counts['토']}) 金({counts['금']}) 水({counts['수']})</div><div>🌟 천을귀인: {guiin_str}</div><div>🎯 공망: [일] {i_gong}</div><div>🌪️ 삼재: <span style='color:{samjae_color};'>{cur_samjae}</span></div></div>"

            daewun_info = []
            un_html = f"<div style='margin-top:5px; margin-bottom:10px; font-size:18px; font-weight:900; color:#1A237E;'>[ 대운의 흐름 (대운수: {calc_d}, {direction_str}) ]</div><div style='display:flex; flex-direction:row-reverse; width:100%; border:2px solid #3E2723; background:white; margin-bottom:5px;'>"
            for i in range(10):
                val, c, j = i*10+calc_d, GAN[(GAN.index(ms)+(i+1)*order)%10] if ms in GAN else "-", JI[(JI.index(mb)+(i+1)*order)%12] if mb in JI else "-"
                daewun_info.append(f"{val}세:{c}{j}")
                is_active = val <= u_age < val+10
                bg_col = "#FFF9C4" if is_active else "transparent"
                b_left = "1px solid #ccc" if i != 9 else "none"
                un_html += f"<div style='flex:1; border-left:{b_left}; text-align:center; padding-bottom:3px; background-color:{bg_col};'><div style='background-color:#3E2723; color:#FFFFFF; font-weight:900; padding:4px 0; font-size:12px; border-bottom:1px solid #ccc;'>{val}세</div><div style='padding:2px; font-size:12px;'>{get_ss(ds,c)}</div><div class='color-{get_color(c)}' style='font-size:16px; font-weight:900;'>{c}</div><div class='color-{get_color(j)}' style='font-size:16px; font-weight:900;'>{j}</div><div style='padding:2px; font-size:12px;'>{get_ss(ds,j)}</div><div style='font-size:11px; border-top:1px solid #ccc;'>{get_unsung(ds,j)}</div><div style='font-size:11px; color:#C62828; border-top:1px solid #ccc;'>{get_12_shinsal(yb, j)}</div></div>"
            un_html += "</div>"

            cur_dw_idx = max(0, (u_age - calc_d) // 10)
            dw_g_cur = GAN[(GAN.index(ms) + (cur_dw_idx+1)*order)%10] if ms in GAN else "-"
            dw_j_cur = JI[(JI.index(mb) + (cur_dw_idx+1)*order)%12] if mb in JI else "-"
            current_daewun_age = cur_dw_idx * 10 + calc_d
            
            dw_start_age = current_daewun_age
            dw_mid_age   = current_daewun_age + 4
            dw_mid2_age  = current_daewun_age + 5
            dw_end_age   = current_daewun_age + 9

            start_year = u_y + current_daewun_age - 1
            sewun_info = []
            se_html = f"<div style='margin-top:5px; margin-bottom:10px; font-size:18px; font-weight:900; color:#1A237E;'>[ 세운의 흐름 ({dw_g_cur}{dw_j_cur}대운 기준) ]</div><div style='display:flex; flex-direction:row-reverse; width:100%; border:2px solid #3E2723; background:white; margin-bottom:5px;'>"
            for i in range(10):
                ty = start_year + i
                tage = current_daewun_age + i
                base = (ty - 1984) % 60
                tc, tj = GAN[base % 10], JI[base % 12]
                sewun_info.append(f"{ty}년({tc}{tj})")
                is_cur_yr = (ty == curr_y)
                bg_col = "#E1F5FE" if is_cur_yr else "transparent"
                b_left = "1px solid #ccc" if i != 9 else "none"
                se_html += f"<div style='flex:1; border-left:{b_left}; text-align:center; padding-bottom:3px; background-color:{bg_col};'><div style='background-color:#3E2723; color:#FFFFFF; font-weight:900; padding:4px 0; font-size:12px; line-height:1.2; border-bottom:1px solid #ccc;'>{ty}년<br>({tage}세)</div><div style='padding:2px; font-size:12px;'>{get_ss(ds,tc)}</div><div class='color-{get_color(tc)}' style='font-size:16px; font-weight:900;'>{tc}</div><div class='color-{get_color(tj)}' style='font-size:16px; font-weight:900;'>{tj}</div><div style='padding:2px; font-size:12px;'>{get_ss(ds,tj)}</div><div style='font-size:11px; border-top:1px solid #ccc;'>{get_unsung(ds,tj)}</div><div style='font-size:11px; color:#C62828; border-top:1px solid #ccc;'>{get_12_shinsal(yb, tj)}</div></div>"
            se_html += "</div>"

            wol_gans = ["己", "庚", "辛", "壬", "癸", "甲", "乙", "丙", "丁", "戊", "己", "庚"]
            wol_jis = ["丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥", "子"]
            cur_wol_g = wol_gans[curr_m - 1]
            cur_wol_j = wol_jis[curr_m - 1]
            
            wol_html = f"<div style='margin-top:5px; margin-bottom:10px; font-size:18px; font-weight:900; color:#1A237E;'>[ 월운의 흐름 ({curr_y}년도 양력기준) ]</div><div style='display:flex; flex-direction:row-reverse; width:100%; border:2px solid #3E2723; background:white; margin-bottom:5px;'>"
            for i in range(12):
                tm, tc, tj = i + 1, wol_gans[i], wol_jis[i]
                is_cur_m = (tm == curr_m)
                bg_col = "#E8F5E9" if is_cur_m else "transparent"
                b_left = "1px solid #ccc" if i != 11 else "none"
                wol_html += f"<div style='flex:1; border-left:{b_left}; text-align:center; padding-bottom:3px; background-color:{bg_col};'><div style='background-color:#3E2723; color:#FFFFFF; font-weight:900; padding:4px 0; font-size:12px; border-bottom:1px solid #ccc;'>{tm}월</div><div style='padding:2px; font-size:12px;'>{get_ss(ds,tc)}</div><div class='color-{get_color(tc)}' style='font-size:16px; font-weight:900;'>{tc}</div><div class='color-{get_color(tj)}' style='font-size:16px; font-weight:900;'>{tj}</div><div style='padding:2px; font-size:12px;'>{get_ss(ds,tj)}</div><div style='font-size:11px; border-top:1px solid #ccc;'>{get_unsung(ds,tj)}</div><div style='font-size:11px; color:#C62828; border-top:1px solid #ccc;'>{get_12_shinsal(yb, tj)}</div></div>"
            wol_html += "</div>"

            past_daewun_list = []
            for idx in range(cur_dw_idx):
                val = idx * 10 + calc_d
                d_gan = GAN[(GAN.index(ms) + (idx + 1) * order) % 10] if ms in GAN else "-"
                d_ji = JI[(JI.index(mb) + (idx + 1) * order) % 12] if mb in JI else "-"
                past_daewun_list.append(f"• {val}세~{val+9}세 ({d_gan}{d_ji}대운): ")
            past_daewun_html = "\n".join(past_daewun_list) if past_daewun_list else "• (첫 대운 시기이므로 이전 대운 생략)"

            curr_dw_start_year = u_y + current_daewun_age - 1
            sewun_start_calc = min(curr_dw_start_year, curr_y - 3)
            past_sewun_list = []
            for py in range(sewun_start_calc, curr_y):
                base = (py - 1984) % 60
                past_sewun_list.append(f"• {py}년({GAN[base%10]}{JI[base%12]}년): ")
            past_sewun_html = "\n".join(past_sewun_list) if past_sewun_list else "• (분석할 과거 세운 없음)"

            terms_name = {1:"소한", 2:"입춘", 3:"경칩", 4:"청명", 5:"입하", 6:"망종", 7:"소서", 8:"입추", 9:"백로", 10:"한로", 11:"입동", 12:"대설"}
            def get_term_day(y, m):
                _, p1, _ = get_true_year_month_pillar(y, m, 1, 12, 0)
                for d in range(2, 12):
                    _, pd, _ = get_true_year_month_pillar(y, m, d, 12, 0)
                    if pd != p1: return d, pd
                return 5, p1

            past_wol_list = []
            prev_y_idx = (curr_y - 1 - 1984) % 60
            prev_y_ganji = GAN[prev_y_idx % 10] + JI[prev_y_idx % 12]
            for pm in range(1, curr_m):
                tc, tj = wol_gans[pm-1], wol_jis[pm-1]
                s_day, _ = get_term_day(curr_y, pm)
                next_m = pm + 1 if pm < 12 else 1
                next_y = curr_y if pm < 12 else curr_y + 1
                e_day, _ = get_term_day(next_y, next_m)
                t_start = terms_name[pm]
                t_end = terms_name[next_m]
                year_prefix = f"{prev_y_ganji}년 " if pm == 1 else ""
                past_wol_list.append(f"• {pm}월({tc}{tj}월): ({year_prefix}{pm}월 {s_day}일 {t_start} ~ {next_m}월 {e_day-1}일 {t_end} 전)")
            past_months_html = "\n".join(past_wol_list) if past_wol_list else "• (올해 첫 달이므로 작년 하반기 요약): "

            curr_term_day, curr_wol_pillar = get_term_day(curr_y, curr_m)
            next_m = curr_m + 1 if curr_m < 12 else 1
            next_y = curr_y if curr_m < 12 else curr_y + 1
            next_term_day, _ = get_term_day(next_y, next_m)
            curr_t_name = terms_name[curr_m]
            next_t_name = terms_name[next_m]

            if curr_m == 6:
                sun = ephem.Sun()
                haji_day = 21
                for d in range(20, 24):
                    dt_utc = dt_mod.datetime(curr_y, 6, d, 12, 0).astimezone(pytz.utc)
                    sun.compute(dt_utc)
                    if math.degrees(ephem.Ecliptic(sun).lon) % 360.0 >= 90.0: haji_day = d; break
                prompt_first_half = f"▶ 이번 달 전반기 ({curr_m}월 {curr_term_day}일 {curr_t_name} ~ {curr_m}월 {haji_day-1}일 하지 전: {curr_wol_pillar})"
                prompt_second_half = f"▶ 이번 달 후반기 ({curr_m}월 {haji_day}일 하지 ~ {next_m}월 {next_term_day-1}일 {next_t_name} 전: {curr_wol_pillar})"
            else:
                mid_day = curr_term_day + 15
                prompt_first_half = f"▶ 이번 달 전반기 ({curr_m}월 {curr_term_day}일 {curr_t_name} ~ {curr_m}월 {mid_day-1}일: {curr_wol_pillar})"
                prompt_second_half = f"▶ 이번 달 후반기 ({curr_m}월 {mid_day}일 ~ {next_m}월 {next_term_day-1}일 {next_t_name} 전: {curr_wol_pillar})"

            closing_html = f"""<div style='margin-top: 30px;'>
<p style='text-indent: 15px; text-align: justify; line-height: 1.8; margin-bottom: 8px;'>'사주팔자'는 태어날 때 부여받은 정통 명식의 바코드와 같지만, 우리가 살아가며 마주하는 '운'은 늘 변화하며 흐릅니다.</p>
<p style='text-indent: 15px; text-align: justify; line-height: 1.8; margin-bottom: 8px;'>따라서 오늘의 '초연 전통명리와의 인연'이 <b>{disp_name}님</b>의 삶이라는 긴 여정에서 올바른 방향을 잡는 든든한 '나침반'이 되기를 진심으로 기원합니다.</p>
<p style='text-indent: 15px; text-align: justify; line-height: 1.8; margin-bottom: 15px;'>앞으로 인생의 길흉화복과 명리에 대한 더 깊은 지혜가 필요하실 때 언제든 <b>'초연 전통명리 연구소'</b>를 찾아 주십시오.</p>
<p style='text-indent: 15px; font-size: 16px; line-height: 1.8; font-weight: bold; margin-bottom: 0px;'>오늘 닿은 귀한 인연에 다시 한 번 깊이 감사드립니다.</p>
<div style='text-align: right; margin-top: 30px;'>
<span style='font-weight: 900; font-size: 18px; color: #1A237E;'>- 초연 전통명리 연구소 드림 -</span>
</div>
</div>"""

            report_1_full_html = f"""{cover_html}
<div class='report-page' style='page-break-before: avoid;'>
<div class='vip-inset-frame' style='border:2px solid #1A237E; box-sizing: border-box; padding: 20px; border-radius:15px; margin-top: 0;'>
<h1 style='text-align:center; font-size: 24px; font-weight: 900; white-space: nowrap;'>{report_title}</h1>
{table_html}
{master_bar_html}
<div style='margin-top:20px;'>
{{full_content_clean_placeholder}}
</div>
</div>
</div>"""

            base_gans_list = [hs, ds, ms, ys]
            base_jjis_list = [hb, db, mb, yb]

            won_guk_vaults = []
            for attacker in base_jjis_list:
                won_guk_vaults.extend(check_vault_status(base_gans_list, base_jjis_list, attacker))
            won_guk_vaults = list(dict.fromkeys(won_guk_vaults)) 
            won_guk_vaults_str = ", ".join(won_guk_vaults) if won_guk_vaults else "해당 없음"

            daewun_vaults = check_vault_status(base_gans_list, base_jjis_list, dw_j_cur)
            sewun_vaults = check_vault_status(base_gans_list, base_jjis_list, curr_y_ganji[1])
            wolwun_vaults = check_vault_status(base_gans_list, base_jjis_list, cur_wol_j)

            hang_un_vaults = list(dict.fromkeys(daewun_vaults + sewun_vaults + wolwun_vaults))
            hang_un_vaults_str = ", ".join(hang_un_vaults) if hang_un_vaults else "해당 없음"

            disp_first_name = disp_name[1:] if len(disp_name) > 2 else disp_name
            
            age_prompt = ""
            if u_age < 20:
                age_prompt = "내담자는 청소년기(10대)입니다. 학업 진학운과 부모 형제운을 최우선으로 상세히 분석하고 재물 사업운은 축소하십시오."
            elif 20 <= u_age < 40:
                age_prompt = "내담자는 청년기(20~30대) MZ세대입니다. 고리타분한 명리 용어를 버리고 직업은 '스타트업, 프리랜서, 워라밸, 퍼스널 브랜딩', 연애는 '소개팅, 썸, 연인 간의 소통' 등 2030 청년들이 100% 공감할 수 있는 세련되고 트렌디한 어휘로 통변하십시오."
            elif 40 <= u_age < 60:
                age_prompt = "내담자는 중장년기(40~50대)입니다. 재성운과 관직 명예운에 집중하여 현실적인 자산 관리와 사회적 성취를 중심으로 서술하십시오."
            else:
                age_prompt = "내담자는 노년기(60대 이상)입니다. 건강운 및 심리적 평안, 노후 자산 안정을 최우선으로 깊이 다루십시오."

            gender_prompt = ""
            if u_gender == "남성":
                gender_prompt = "남성 내담자입니다. 배우자운(재성)과 자식운(관성)을 남명 이론에 입각하여 해석하십시오."
            else:
                gender_prompt = "여성 내담자입니다. 배우자운(관성)과 자식운(식상)을 여명 이론에 입각하여 해석하십시오."

            if ilju_master_data:
                ilju_master_prompt_context = f"""
🎯 [초연 전통명리의 뼈때리는 팩트폭격 - {user_ilju_key}일주 전용 마스터 비기]
- 물상 및 성향 요약: {ilju_master_data.get('summary', '')}
- 심리적 관점: {ilju_master_data.get('psychology', '')}
- 육친적 관점: {ilju_master_data.get('family', '')}
- 사회적 관점: {ilju_master_data.get('society', '')}
- 지장간 좌법(座法) 분석: {ilju_master_data.get('jijanggan_zaBeob', '')}
- 인종법(引從法) 숨겨진 내면: {ilju_master_data.get('injong_beob', '')}
- 신살, 변곡점, 건강, 과숙/고신, 도망역: {ilju_master_data.get('shinsal_warnings', '')}
- 💥 뼈때리는 팩트폭격 핵심 비기: {ilju_master_data.get('choyeon_secret', '')}

🚨 [통변 절대 규칙]: 위 박사님의 '초연 전통명리의 뼈때리는 팩트폭격'에 담긴 문장과 임상적 통찰을 사주풀이 에세이(성격 분석, 사주구조분석, 운의 흐름) 전반에 100% 녹여내어 깊이 있게 풀이하십시오.
"""
            else:
                ilju_master_prompt_context = ""
                                
            db_header = (
                f"[시스템 강제 시간 인식: 현재 시점은 {curr_y}년 {curr_m}월 입니다.]\n"
                "당신은 정통 명리심리상담사 1급 자격을 갖춘 초연 박사입니다. \n"
                f"- 내담자 성함: {disp_name}\n"
                f"- 나이 / 성별: {u_age}세 / {u_gender}\n"
                f"- marital_status: {u_marital}\n"
                f"- 선택 상품: {u_product}\n"
                f"- 격국 팩트: {gyukgook_detail}\n"
                f"- 실제 타격받는 공망 궁위 팩트: {gongmang_actual}\n"
                f"- 올해({curr_y}년) 삼재 여부: {cur_samjae}\n" 
                f"- 원국 삼형살(인사신/축술미) 팩트: {samhyung_warn}\n"
                f"- 원국 내부 묘고(입고/개고) 작용: {won_guk_vaults_str}\n"
                f"- 현재 행운(대/세/월운) 외부 충격에 의한 묘고 작용: {hang_un_vaults_str}\n"
                f"🚨 [AI 환각 및 UI 파괴 원천 차단 절대 규칙]\n"
                f"1. 서론 철저 금지: '안녕하십니까', '기쁩니다' 등의 인사말이나 감성적인 도입부를 절대로 작성하지 마십시오.\n"
                f"2. 호칭 절대 규칙: 각 대목차의 첫 문장은 반드시 '{disp_name}님은~'으로 격식있게 시작하고, 그 이후 본문에서는 친근하게 '{disp_first_name}님은~'으로 부르십시오.\n"
                f"3. 🚨 공망 소설 금지: 위 '실제 타격받는 공망 궁위 팩트'에 명시된 자리만 공망으로 해석하십시오.\n"
                f"4. 괄호 병기 금지: 에세이 작성 시 전문 용어나 한자를 괄호 안에 병기하는 행위를 금지합니다.\n"
                f"5. HTML 훼손 금지: </div> 태그를 임의로 닫거나 마크다운 기호를 남발하지 마십시오.\n"
            )

            if u_gender == '남성':
                yukchin_rule = f"""
🚨 [육친 통변 특수부대 절대 규칙 (남성용)]: 
- 본 내담자는 남성(현재 상태: {u_marital})입니다. 아래의 명리학적 육친 생극제화 및 대체 규칙을 100% 엄수하십시오.
1. 👨‍👩‍👦 [핵심 가족]: 
   - 아내(부인) = 정재 (정재가 없으면 편재로 대체)
   - 애인(여친) = 편재 (편재가 없으면 정재로 대체)
   - 자녀 = 관성(정관/편관) 🚨(경고: 남명에서 '식상'을 자녀로 풀이하는 즉시 치명적 오류로 간주함!)
2. 👵👴 [부모 및 조부모]: 
   - 아버지 = 편재 (없으면 정재) / 어머니 = 정인 (없으면 편인)
   - 조부(할아버지) = 편인 / 조모(할머니) = 상관
3. 🏠 [처가 및 형제]: 
   - 장모(처가) = 식상 (아내를 생하는 기운)
   - 동성 형제(형/남동생) = 비견 / 이성 형제(누나/여동생) = 겁재
4. 🚨 [상태별 호칭 맞춤형 타겟팅]: 내담자의 현재 혼인 상태({u_marital})를 반드시 반영하십시오. 
   - 기혼: '현재 아내/배우자'로 칭할 것.
   - 미혼: '미래의 인연'으로 칭할 것.
   - 🚨돌싱(이혼/사별): '과거의 인연(전처)'에 대한 성찰이나 '새로운 인연(재혼운)'으로 변환하여 카운슬링할 것.
"""
            else:
                yukchin_rule = f"""
🚨 [육친 통변 특수부대 절대 규칙 (여성용)]: 
- 본 내담자는 여성(현재 상태: {u_marital})입니다. 아래의 명리학적 육친 생극제화 및 대체 규칙을 100% 엄수하십시오.
1. 👩‍❤️‍👨 [핵심 가족]: 
   - 남편 = 정관 (정관이 없으면 편관으로 대체)
   - 애인(남친) = 편관 (편관이 없으면 정관으로 대체)
   - 자녀 = 식상(식신/상관) 🚨(경고: 여명에서 '관성'을 자녀로 풀이하는 즉시 치명적 오류로 간주함!)
2. 👵👴 [부모 및 조부모]: 
   - 아버지 = 편재 (없으면 정재) / 어머니 = 정인 (없으면 편인)
   - 조부(외할아버지) = 편인 / 조모(외할머니) = 상관
3. 🏠 [시댁 및 자매]: 
   - 시어머니(시댁) = 재성 (남편을 생하는 기운)
   - 동성 형제(언니/여동생) = 비견 / 이성 형제(오빠/남동생) = 겁재
4. 🚨 [상태별 호칭 맞춤형 타겟팅]: 내담자의 현재 혼인 상태({u_marital})를 반드시 반영하십시오. 
   - 기혼: '현재 남편/배우자'로 칭할 것.
   - 미혼: '미래의 인연'으로 칭할 것.
   - 🚨돌싱(이혼/사별): '과거의 인연(전 남편)'에 대한 성찰이나 '새로운 인연(재혼운)'으로 변환하여 카운슬링할 것.
"""

            prompt = ""
            clean_ai_text = ""

            # ==============================================================
            # [A-1] 1. 개인 사주팔자 풀이 (종합 파이프라인)
            # ==============================================================
            if main_category == "1. 개인 사주팔자 풀이 (종합)":

                wood_cnt = counts.get('목', 0)
                fire_cnt = counts.get('화', 0)
                earth_cnt = counts.get('토', 0)
                metal_cnt = counts.get('금', 0)
                water_cnt = counts.get('수', 0)

                if u_product == "1-1. 사주팔자와 운세풀이 (기본)":
                    prompt = f"""
{db_header}
{ilju_master_prompt_context}

================================================================================
🧠 [1단계: AI 내부 심층 분석 및 표(Table)·마스터바 데이터 연동 지침]
================================================================================
당신은 정통 명리심리상담사 1급 자격을 갖춘 '초연 박사'입니다.
상단 표와 마스터 바에 출력된 핵심 팩트(오행 분포, 격국:{gyukgook_detail}, 천간합충, 지지합충형해파:{hap_chung_hyoung_pa_hae}, 공망:{gongmang_actual}, 삼재:{cur_samjae}, 원국 삼형살:{samhyung_warn}, 묘고 작용:{won_guk_vaults_str}, 신살:{shinsal_str})를 본문 에세이와 100% 매칭하여 통변하십시오.

🚨 [명리 용어 표기 & 알기 쉬운 개념 풀이 절대 규칙]:
1. 🚨 **[용어 표기 서식 규칙 - 필출]**: 본문에 나타나는 모든 명리학 용어(예: 격국명, 십성, 천간합충, 지지합충형해파, 귀인, 신살, 공망, 삼재, 묘고, 대운, 세운 등) 및 특별히 강조하고자 하는 핵심 개념은 반드시 **'작은따옴표와 진한 글씨체'**를 결합하여 **'명리용어'** 서식(예: **'편관격'**, **'천을귀인'**, **'공망'**, **'방합'**, **'눌삼재'**)으로 작성하십시오.
2. **천간 vs 지지 역할 구분**:
   - **천간의 합/충/극**: 내담자의 정신적 지향점, 마음의 기운, 의지의 결속 및 심리적 갈등의 상호작용임을 먼저 설명하고 현실적 심리 팩트를 서술하십시오.
   - **지지의 합충형해파**: 내담자의 실제 삶의 무대(직업, 주거, 대인관계, 자산, 신체)에서 일어나는 현실적 환경 변화와 인생의 변곡점임을 설명하고 팩트를 서술하십시오.
3. **삼형살 및 묘고 작용 필수 통변**:
   - 삼형살({samhyung_warn})이나 묘고 작용({won_guk_vaults_str})이 성립하는 경우, 해당 명리학적 개념(기운의 조정·수술·개고·입고)의 뜻을 쉽게 풀어준 후 그것이 가져오는 삶의 거대한 변곡점을 명쾌히 서술하십시오.
4. **용어 해설 + 현실 결론 구조**:
   - 상단 표에 나타난 용어가 본문에 등장할 때, **'해당 용어의 원리적 의미 1문장 해설 -> 그것이 내담자의 삶에서 가져오는 현실적 행동/심리/사건·사고 결론'** 형태로 알기 쉽게 풀어서 통변하십시오.
5. 원국 8글자 한자 외 불필요한 한자 병기를 금지하며, 품격 있는 현대적 구어체 존댓말(-합니다, -입니다)로 서술하십시오.

================================================================================
✍️ [2단계: 최종 출력물 작성 규칙]
================================================================================
1. 모든 통변 문장은 반드시 <p style='text-indent: 1em;'> 태그로 감싸하십시오.
2. 표(Table) 생성 절대 금지. ([DAEWUN_TABLE_HERE], [SEWUN_TABLE_HERE] 태그 위치 엄수)

<h3 style='color:#1A237E; font-size: 24px; font-weight: 900;'>1. 성격 분석</h3>
<div class='content-box-loose'>
{choyeon_golden_text}

<span class='sub-title' style='font-size: 20px; font-weight: 900; color: #111;'>1) 겉으로 드러난 성격</span>
- 내담자의 일간·일지 기운과 원국 구성을 종합하여 **'육친적'**, **'심리적'**, **'사회적'** 관점에서 대외적 행동 방식, 조직 소속감, 대인관계 스타일을 서술하십시오. (자의형상 물상 수식어 배제)

<span class='sub-title' style='font-size: 20px; font-weight: 900; color: #111;'>2) 감추어진 내 속마음</span>
- 일지 지장간, 십이운성, 공망 궁위가 형성하는 무의식적 파동을 심층 분석하여, 외부로 드러내지 않는 내면의 본능적 욕구, 가치관, 남모를 정신적 고독감이나 결핍감을 알기 쉽게 풀어 정밀 서술하십시오.
</div>

<h3 style='color:#1A237E; font-size: 24px; font-weight: 900;'>2. 사주팔자 구조분석</h3>
<div class='content-box-loose'>
<span class='sub-title' style='font-size: 20px; font-weight: 900; color: #111;'>1) 내 삶의 무대와 타고난 기본 성향</span>
- 상단 표의 **'오행 분포'**(木:{wood_cnt}, 火:{fire_cnt}, 土:{earth_cnt}, 金:{metal_cnt}, 水:{water_cnt}) 및 **'격국'**({gyukgook_detail})의 원리적 의미를 먼저 설명한 후, 타고난 삶의 무대와 성품의 강약점을 서술하십시오.

<span class='sub-title' style='font-size: 20px; font-weight: 900; color: #111;'>2) 내 삶의 역동성과 상호작용</span>
- 상단 표의 **'천간 합충'**(극)과 **'지지 합충형해파'**({hap_chung_hyoung_pa_hae})를 구분하여, 천간은 정신적 기운의 변화로, 지지는 현실적 환경 변화와 대인/배우자 관계의 역동성으로 풀어서 서술하십시오.

<span class='sub-title' style='font-size: 20px; font-weight: 900; color: #111;'>3) 내 삶의 숨겨진 능력과 특별한 행운의 요소</span>
- 마스터 바의 **'천을귀인'**({guiin_str}) 및 표의 **'신살'**({shinsal_str}) 개념을 알기 쉽게 해설하고, 이것이 실제 삶에서 위기를 극복하게 만드는 행운의 조력으로 어떻게 작용하는지 서술하십시오.

<span class='sub-title' style='font-size: 20px; font-weight: 900; color: #111;'>4) 내 삶의 변곡점과 주의해야 할 시련</span>
- 원국 내 **'삼형살'**({samhyung_warn}), **'묘고 작용'**({won_guk_vaults_str}), **'공망'**({gongmang_actual})의 원리(조정, 입고/개고, 결핍)를 알기 쉽게 풀어서 설명하고, 인생에서 마주할 변곡점과 시련에 대한 현실적 대처법을 조언하십시오.
</div>

<h3 style='color:#1A237E; font-size: 24px; font-weight: 900;'>3. 현재 대운 및 세운 흐름 분석</h3>
<div class='content-box-loose'>
<p style='text-indent: 1em;'><b>'대운'(大運)의 명리학적 의미:</b> 명리학에서 **'대운'**이란 흔히 생각하는 대통할 운이 아니라, 10년 단위로 바뀌는 내 삶의 <b>'거대한 계절과 환경의 변화'</b>를 의미합니다. 원국이라는 자동차가 어떤 도로 환경을 달리고 있는지를 보여주는 나침반입니다.</p>

<span class='sub-title' style='font-size: 20px; font-weight: 900; color: #111;'>1) 대운의 흐름 분석</span>
[DAEWUN_TABLE_HERE]
▶ 대운에 따른 과거·현재·미래 운세 분석:
- 지나온 대운의 환경 변화와 현재 대운({dw_g_cur}{dw_j_cur})이 가져다주는 삶의 기회/시련, 그리고 앞으로 다가올 미래 대운의 발전 가능성을 10년 주기 파동에 입각하여 깊이 있게 정밀 통변하십시오.

<span class='sub-title' style='font-size: 20px; font-weight: 900; color: #111;'>2) 세운의 흐름 분석</span>
[SEWUN_TABLE_HERE]
▶ 현재 대운 속 세운의 과거·현재·미래 운세 분석 (삼재 여부: {cur_samjae}):
- 마스터 바의 **'삼재'**({cur_samjae}) 개념(**'들삼재'**/**'눌삼재'**/**'날삼재'**의 의미)을 알기 쉽게 풀어 설명하고, 올해 세운({curr_y_ganji})을 중심으로 과거 3개년, 올해 상/하반기 환경 변동, 다가올 미래 세운의 준비 전략을 상세히 서술하십시오.
</div>

<h3 style='color:#1A237E; font-size: 24px; font-weight: 900;'>4. 삶을 바꾸는 지혜로운 조언 및 개운 비법</h3>
<div class='content-box-loose'>
<span class='sub-title' style='font-size: 18px; font-weight: 900; color: #111;'>1) 나를 돕는 에너지와 색상:</span>
- 용신/희신 오행에 부합하는 개운 색상과 전통 하도 수리(水 1·6, 火 2·7, 木 3·8, 金 4·9, 土 5·10) 행운의 숫자를 명쾌히 제시하십시오.
<span class='sub-title' style='font-size: 18px; font-weight: 900; color: #111;'>2) 재물을 부르는 이재(理財)와 절제의 지혜:</span>
- 손재수를 막고 실질적인 부를 축적할 지출 절제 및 투자 가이드를 조언하십시오.
<span class='sub-title' style='font-size: 18px; font-weight: 900; color: #111;'>3) 재능 효율을 높이는 직업적 지혜:</span>
- 강점을 극대화할 직업적 처세술을 조언하십시오.
<span class='sub-title' style='font-size: 18px; font-weight: 900; color: #111;'>4) 신체 밸런스와 에너지 관리:</span>
- 취약 신체 부위 및 건강 습관을 제시하십시오.
<span class='sub-title' style='font-size: 18px; font-weight: 900; color: #111;'>5) 공간의 흐름과 방위의 지혜:</span>
- 길한 방향과 공간 정돈 개운 인테리어를 제시하십시오.

<div style='margin-top: 25px; padding-top: 15px; border-top: 1.5px dashed #1A237E;'>
<span class='sub-title' style='font-size: 20px; font-weight: 900; color: #1A237E; display: block; margin-bottom: 10px;'>🎯 전통명리 특별 개운 비법</span>
<span class='sub-title' style='font-size: 18px; font-weight: 900; color: #111;'>1) 수호 천사의 기운 조언:</span>
- **'천을귀인'** 등 나를 돕는 귀인 성분과 조력자 활용 개운법을 제시하십시오.
<span class='sub-title' style='font-size: 18px; font-weight: 900; color: #111;'>2) 백년해로의 기운 조언:</span>
- 부부·연인 간 갈등을 피하고 인연을 지키는 백년해로 지혜를 조언하십시오.
<span class='sub-title' style='font-size: 18px; font-weight: 900; color: #111;'>3) 행운에 따른 기운 조언:</span>
- 현재 운의 파동을 타고 흉한 변곡점을 우회하는 행운 처세술을 조언하십시오.
</div>
</div>

<div style='margin-top: 30px; padding: 15px; background-color: #F8F9FA; border-left: 4px solid #1A237E; border-radius: 4px;'>
<p style='font-size: 16px; font-weight: 900; color: #1A237E; margin: 0; line-height: 1.6;'>💡 [초연 전통명리 안내]</p>
<p style='font-size: 15px; font-weight: 600; color: #333; margin-top: 5px; margin-bottom: 0; line-height: 1.7;'>본 풀이는 사주 원국의 본질과 현재 운의 큰 흐름을 짚어드린 기본 감명입니다. 특정 연도별·월별 정밀한 세부 흐름은 <b>'올해 및 특정연도 운세 상세분석'</b>을, 재물·직업 등 특정 분야의 집중 상담은 <b>'테마별 특성화 상담'</b>을 통해 확인하실 수 있습니다.</p>
</div>
"""
                elif u_product == "1-2. 올해 및 특정연도 운세 상세분석":
                    target_year_val = st.session_state.get('target_year_input', curr_y)
                    prompt = f"""
{db_header}
{ilju_master_prompt_context}

================================================================================
🧠 [1-2. {target_year_val}년 운세 상세분석 정밀 지침]
================================================================================
당신은 정통 명리심리상담사 '초연 박사'입니다. 본 상담은 지정된 **{target_year_val}년**의 연도별 운세 흐름을 칼같이 분석하는 상세 리포트입니다.

1. 최근 과거 세운 흐름 회고:
   {past_sewun_html}
2. 지정 연도({target_year_val}년) 전반기 및 후반기 정밀 통변:
   - 전반기(상반기): 환경적 기회, 재물/직업 변동성, 실질적 사건·사고 팩트 서술.
   - 후반기(하반기): 핵심 결실, 인연의 길흉, 리스크 방어 가이드 서술.
3. 올해/해당 연도 삶을 바꾸는 지혜로운 조언 및 개운 비법을 상세 서술하십시오.

================================================================================
✍️ [2단계: 최종 출력물 작성 규칙]
================================================================================
1. 난해한 명리학 용어 해설 배제, 현실적 결론 직행.
2. 모든 문단은 <p style='text-indent: 1em;'> 태그 적용.
3. 표(Table) 생성 금지.

<h3 style='color:#1A237E; font-size: 24px; font-weight: 900;'>1. 지나온 과거 세운 흐름 회고</h3>
<div class='content-box-loose'>
🚨 [세운 줄바꿈 절대 규칙]: 각 세운 항목(• ... :)의 쌍점(:) 뒤 해설은 반드시 독립된 <p style='text-indent: 1em; margin-bottom: 12px;'> 태그로 감싸 한 줄씩 완전히 줄바꿈하여 작성하십시오.
{past_sewun_html}
</div>

<h3 style='color:#1A237E; font-size: 24px; font-weight: 900;'>2. {target_year_val}년 운세 정밀 상세분석</h3>
<div class='content-box-loose'>
▶ {target_year_val}년 전반기(상반기) 상세 분석:
- 상반기 동안 일어나는 주된 환경적 기회, 재물/직업상의 변동성, 실질적 사건·사고의 팩트를 명쾌하게 풀이하십시오.
▶ {target_year_val}년 후반기(하반기) 상세 분석:
- 하반기 동안 집중해야 할 핵심 결실, 인연의 길흉, 리스크 방어를 위한 실질적 지침을 서술하십시오.
</div>

<h3 style='color:#1A237E; font-size: 24px; font-weight: 900;'>3. {target_year_val}년 맞춤형 개운 비법 및 조언</h3>
<div class='content-box-loose'>
- 해당 연도의 기운을 극대화하고 리스크를 우회할 실질적 처세술 및 개운 비법을 서술하십시오.
</div>
"""
                else:
                    prompt = f"""
{db_header}
{ilju_master_prompt_context}

================================================================================
🧠 [1-3 / 1-4. 월운 및 일진 상세분석 정밀 지침]
================================================================================
당신은 정통 명리심리상담사 '초연 박사'입니다. 본 상담은 특정 월과 일진의 미세한 기운 파동을 포착하는 초단기 실전 분석 리포트입니다.

1. 지나온 과거 월운의 흐름 회고:
   {past_months_html}
2. 현재/지정 월운 정밀 통변:
   - {prompt_first_half}: 이번 달 전반기 심리 파동, 행동 지침, 주의점 팩트 서술.
   - {prompt_second_half}: 이번 달 후반기 사건·사고, 재물/대인관계 성패, 마무리 전략 서술.
3. 단기 리스크 방어와 성취를 위한 개운 비법 조언.

================================================================================
✍️ [2단계: 최종 출력물 작성 규칙]
================================================================================
1. 난해한 용어 배제, 즉각적 행동 지침 위주.
2. 모든 문단은 <p style='text-indent: 1em;'> 태그 적용.
3. 표(Table) 생성 금지.

<h3 style='color:#1A237E; font-size: 24px; font-weight: 900;'>1. 지나온 월운 회고</h3>
<div class='content-box-loose'>
{past_months_html}
</div>

<h3 style='color:#1A237E; font-size: 24px; font-weight: 900;'>2. 월운 상세 파동 분석</h3>
<div class='content-box-loose'>
{prompt_first_half}
- 이번 달 전반기 동안 발생할 주요 심리 파동, 실질적 행동 지침 및 주의점 팩트를 서술하십시오.
{prompt_second_half}
- 이번 달 후반기 동안 맞이할 실질적 사건, 재물/대인관계의 성패, 마무리 대응 전략을 상세히 서술하십시오.
</div>

<h3 style='color:#1A237E; font-size: 24px; font-weight: 900;'>3. 단기 성공을 위한 개운 비법</h3>
<div class='content-box-loose'>
- 이번 달 파동을 극대화할 단기 처세술과 행운의 에너지 활용법을 조언하십시오.
</div>
"""

                try:
                    res = model.generate_content(prompt)
                    ai_text = "\n".join([line.lstrip() for line in res.text.split("\n")])
                    
                    un_html_clean = un_html.replace("\n", " ").replace("\r", "")
                    se_html_clean = se_html.replace("\n", " ").replace("\r", "")

                    daeoun_target = f"<div style='margin: 15px 0; overflow-x: auto;'>{un_html_clean}</div>"
                    sewun_target = f"<div style='margin: 15px 0; overflow-x: auto;'>{se_html_clean}</div>"

                    clean_ai_text, _ = re.subn(r'[\#\*\_\s]*\[\s*DAEWUN_TABLE_HERE\s*\][\#\*\_\s]*', daeoun_target, ai_text, flags=re.IGNORECASE)
                    clean_ai_text, _ = re.subn(r'[\#\*\_\s]*\[\s*SEWUN_TABLE_HERE\s*\][\#\*\_\s]*', sewun_target, clean_ai_text, flags=re.IGNORECASE)

                    bordered_closing_html = f"<hr style='border: 0; border-top: 2px dashed #1A237E; margin: 35px 0 20px 0;'>{closing_html}"

                    full_content_clean = f"<div style='font-family: \"Nanum Myeongjo\", \"바탕체\", Batang, serif; font-size: 15px; line-height: 1.8; color: #000000;'>{clean_ai_text}<br><br>{bordered_closing_html}</div>"

                    report_1_full_html = report_1_full_html.replace("{full_content_clean_placeholder}", full_content_clean)
                    
                    st.session_state['saved_report_html'] = report_1_full_html
                    
                except Exception as e: 
                    st.error(f"1번 개인 사주풀이 AI 연산 오류: {e}")

            # ==============================================================
            # [A-2] 2. 테마별 특성화 상담 (1:1 솔루션 제외 / 군더더기 없는 명쾌한 정통명리 통변)
            # ==============================================================
            elif main_category == "2. 테마별 특성화 상담":
                
                # 에러 방어용 기본 변수 세팅
                wealth_goal = st.session_state.get('wealth_goal', '안정적인 자산 증식')
                love_goal = st.session_state.get('love_goal', '좋은 인연과 화목한 관계')
                career_goal = st.session_state.get('career_goal', '성공적인 진로와 커리어 성취')
                health_goal = st.session_state.get('health_goal', '일상의 활력과 신체 밸런스 유지')
                
                공통_시스템_헤더 = f"{db_header}\n{ilju_master_prompt_context}\n"

                if u_product == "2-1. 재물운 특화 분석":
                    prompt = 공통_시스템_헤더 + f"""
[SYSTEM ROLE: 초연 전통명리 최고위 재물/자산 분석가]
귀하는 정통 명리학의 오행 생극제화, 십성(정재/편재, 식신/상관), 신강약 및 용희신을 완벽히 통달한 명리학자입니다. 사주 원국에 나타난 재물의 그릇과 대운/세운의 흐름을 정밀하게 분석하되, 내담자가 쉽게 이해할 수 있는 세련된 에세이 형식으로 서술하십시오.

🚨 [출력 목차 강제 지시]: 아래 제목을 100% 그대로 출력하십시오.

[출력 서식 및 통변 지침]

1. 나의 재물운과 진단
[DAEWUN_TABLE_HERE]
[SEWUN_TABLE_HERE]
1) 내가 가진 부의 성향과 자산 그릇
(※ 분석: 원국의 재성(편재/정재)과 식상생재 여부를 바탕으로 안정적 수입형인지 투자/사업형인지 통변하십시오.)
2) 현재의 금전운 흐름 진단
(※ 분석: 내담자의 재물 목표({wealth_goal})와 관련하여 현재 운기를 바탕으로 명쾌하게 진단하십시오.)

2. 자산이 늘어나는 시기와 현금 흐름
1) 대운과 세운이 가져다주는 재물운의 파동
(※ 분석: 재성운이나 용희신 운이 도래하여 금전운이 강하게 발현되는 시기를 서술하십시오.)
2) 나에게 가장 잘 맞는 맞춤형 자산 증식법
(※ 분석: 원국의 구조(재생관, 식상생재, 인성용신 등)에 부합하는 재테크 수단(부동산, 저축, 사업 등)을 추천하십시오.)

3. 내 재산을 안전하게 지키는 리스크 관리
1) 금전적 손실이 우려되는 시기와 방어 가이드
(※ 분석: 군비쟁재(비겁운)나 재성 충극 시기를 경고하고 실질적인 지출 통제 조언을 작성하십시오.)

4. 부를 끌어당기는 일상 속 개운법
1) 나에게 부족한 기운을 채우는 행운의 습관
(※ 분석: 용신 오행을 돕는 행운의 컬러, 방향, 생활 풍수 비법을 제시하십시오.)
"""

                elif u_product == "2-2. 연애/결혼운 특화 분석":
                    prompt = 공통_시스템_헤더 + f"""
[SYSTEM ROLE: 초연 전통명리 최고위 연애/궁합 카운슬러]
정통 명리학의 배우자성(남:재성, 여:관성), 배우자궁(일지)의 동태, 도화/홍염 등의 신살 작용을 바탕으로 내담자의 연애관과 인연의 흐름을 분석하되, 2030 세대가 공감할 수 있는 따뜻한 연애 에세이로 서술하십시오.

🚨 [출력 목차 강제 지시]: 아래 제목을 100% 그대로 출력하십시오.

[출력 서식 및 통변 지침]

1. 내 마음에 깃든 사랑의 형태와 인연
[DAEWUN_TABLE_HERE]
1) 내가 그리는 이상형과 애정을 표현하는 방식
(※ 분석: 일지 십성과 배우자성의 동태를 분석하여 이상형과 연애 스타일을 서술하십시오.)
2) 나의 애정운 흐름 진단
(※ 분석: 내담자의 이성 고민({love_goal})에 대해 현재 기운을 바탕으로 진단해 주십시오.)

2. 새로운 인연이 다가오는 시기와 만남
1) 운명적인 만남이 이루어지는 타이밍
(※ 분석: 대운과 세운에서 합(육합/삼합)이 들어오거나 배우자성 운이 도래하는 시기를 서술하십시오.)

3. [관계의 밸런스] 사랑을 지키기 위한 조언
1) 갈등을 피하고 주도권을 조율하는 지혜
(※ 분석: 일지 충/형/원진 또는 관살혼잡/군비쟁재 등으로 인한 마찰 요인을 짚어주고 현명한 관계 유지법을 조언하십시오.)

4. 변함없는 사랑을 위한 마음가짐과 개운법
1) 건강한 관계를 위한 나만의 처세술
(※ 분석: 서로의 기운을 보완하고 건강한 거리를 유지하기 위한 현실적 명리 팁을 제시하십시오.)
"""

                elif u_product == "2-3. 진학/입시운 특화 분석":
                    prompt = 공통_시스템_헤더 + f"""
[SYSTEM ROLE: 초연 전통명리 최고위 진로/학업 멘토]
정통 명리학의 인성(수용력/학문)과 식상(표현력/응용력)의 구조, 관인상생 여부, 학당/문창귀인 등의 팩트를 바탕으로 타고난 학습 기질과 적성을 분석하되, 수험생과 학부모에게 용기를 주는 확신에 찬 에세이로 서술하십시오.

🚨 [출력 목차 강제 지시]: 아래 제목을 100% 그대로 출력하십시오.

[출력 서식 및 통변 지침]

1. 타고난 배움의 에너지와 나의 적성
[DAEWUN_TABLE_HERE]
[SEWUN_TABLE_HERE]
1) 나에게 가장 잘 맞는 학습 스타일
(※ 분석: 인성 발달(엉덩이 공부/이해형) vs 식상 발달(응용/순발력형)을 분석하여 최적의 공부법을 코칭하십시오.)
2) 현재의 학업운 흐름 진단
(※ 분석: 학업 목표({career_goal}) 달성을 위해 현재 운기가 어떻게 작용하는지 진단하십시오.)

2. 나를 가장 빛나게 할 전공과 진로
1) 나의 재능이 만개할 최적의 학문 분야
(※ 분석: 용희신 오행과 십성에 가장 잘 부합하는 계열(문/이과, 예체능 등)과 세부 전공을 추천하십시오.)

3. 노력의 결실을 맺는 합격과 성취의 타이밍
1) 성취운이 강해지는 대/세운의 흐름
(※ 분석: 관성 및 인성 운이 들어와 시험 합격운과 문서운이 강해지는 시기를 서술하십시오.)

4. 목표 달성을 위한 일상 속 마인드 컨트롤
1) 집중력을 끌어올리는 공간 풍수와 에너지
(※ 분석: 용신을 돕는 책상 방위, 행운의 색상 등 실전 팁을 조언하십시오.)
"""

                elif u_product == "2-4. 직업/커리어운 특화 분석":
                    prompt = 공통_시스템_헤더 + f"""
[SYSTEM ROLE: 초연 전통명리 최고위 커리어/직업 멘토]
정통 명리학의 격국, 관성(조직)과 식재(독립/사업)의 유기적 결합을 분석하여 사회적 성취와 직업적 승부처를 도출하되, 현대 직장인들이 공감할 수 있는 통찰력 있는 에세이로 서술하십시오.

🚨 [출력 목차 강제 지시]: 아래 제목을 100% 그대로 출력하십시오.

[출력 서식 및 통변 지침]

1. 내 삶의 무대와 타고난 커리어 성향
[DAEWUN_TABLE_HERE]
[SEWUN_TABLE_HERE]
1) 나의 직무 재능과 나만의 경쟁력
(※ 분석: 격국과 주도적인 십성을 바탕으로 타고난 재능, 장인정신, 리더십 성향을 분석하십시오.)
2) 조직에 남을 것인가, 나만의 길을 갈 것인가
(※ 분석: 관인상생(조직 직장형)인지 식상생재(독립 사업/프리랜서형)인지 판별하십시오.)
3) 현재의 커리어운 흐름 진단
(※ 분석: 진로/이직 목표({career_goal})에 대해 현재 운기를 바탕으로 진단하십시오.)

2. 나를 성장시킬 최적의 직무와 환경
1) 내 에너지가 가장 잘 발휘되는 산업과 직종
(※ 분석: 사주 용희신과 격국에 부합하는 전문 직종을 추천하십시오.)
2) 가치를 인정받는 슬기로운 직장 처세술
(※ 분석: 상사(관성), 동료(비겁), 부하(식상)와의 관계성을 분석하여 대인관계 팁을 서술하십시오.)

3. 도약과 성취를 이루는 커리어 변곡점
1) 승진과 이직을 위한 결정적 골든타임
(※ 분석: 관운, 인성운 도래 시기나 역마/지살 이동수가 긍정적으로 작용하는 타이밍을 제시하십시오.)

4. 성공적인 커리어를 위한 개운법
1) 사회적 가치를 극대화하는 행동 지침
(※ 분석: 현재 대운에 맞는 직업적 처세술과 실전 조언을 서술하십시오.)
"""

                elif u_product == "2-5. 건강운 특화 분석":
                    prompt = 공통_시스템_헤더 + f"""
[SYSTEM ROLE: 초연 전통명리 최고위 헬스케어 코치]
정통 명리학의 오행 태과/불급, 한난조습(조후), 그리고 충극에 의한 오행 손상을 면밀히 연산하되, 공포감을 주는 대신 '나를 돌보는 다정한 라이프스타일 처방전'처럼 따뜻한 에세이로 서술하십시오.

🚨 [출력 목차 강제 지시]: 아래 제목을 100% 그대로 출력하십시오.

[출력 서식 및 통변 지침]

1. 내 몸의 리듬과 타고난 체질
[DAEWUN_TABLE_HERE]
[SEWUN_TABLE_HERE]
1) 선천적인 신체 기질과 체력의 바탕
(※ 분석: 원국 오행의 밸런스를 바탕으로 타고난 신체적 강약점을 부드럽게 분석하십시오.)
2) 평생 챙겨야 할 건강의 핵심 포인트
(※ 분석: 원국 내 지나치게 강하거나 충극을 받는 오행과 연관된 취약 장기(예: 목-간/담, 화-심혈관 등)를 주의 깊게 짚어주십시오.)

2. 앞으로의 10년, 그리고 올해의 건강 흐름
1) 현재 대운에서 살필 신체 밸런스
(※ 분석: 향후 10년간 기운의 쏠림 현상이 건강에 미칠 영향을 서술하십시오.)
2) 올해 특히 신경 써야 할 일상 속 건강 흐름
(※ 분석: 올해 세운 천간/지지의 충극 작용에 따른 건강 주의점을 진단하십시오.)

3. 건강한 일상을 지키기 위한 리스크 관리
1) 피로와 스트레스가 쌓이는 시기의 대처법
(※ 분석: 귀문/원진살이나 극신약 운기에 발생할 수 있는 멘탈 스트레스 관리법을 다독여 주십시오.)

4. 내 몸을 살리는 다정한 섭생과 개운법
1) 에너지를 보충하는 실전 솔루션
(※ 분석: 부족한 용희신 오행을 채우기 위한 음식, 운동법, 생활 풍수를 다정하게 조언하십시오.)
"""

                elif u_product == "2-6. 이사 택일":
                    prompt = 공통_시스템_헤더 + f"""
[SYSTEM ROLE: 초연 전통명리 최고위 택일/풍수 마스터]
정통 명리학의 일진 생극제화, 십이건제(十二建除), 천을귀인 및 합(육합/삼합)의 길일을 연산하여, 대흉일(충/형/공망/십악대패일 등)을 철저히 배제한 완벽한 이사 길일을 추천하는 희망찬 에세이를 작성하십시오.

🚨 [출력 목차 강제 지시]: 아래 제목을 100% 그대로 출력하십시오.

[출력 서식 및 통변 지침]

1. 새로운 공간으로의 이동이 갖는 의미
[DAEWUN_TABLE_HERE]
[SEWUN_TABLE_HERE]
1) 이사가 나의 운명에 가져올 긍정적인 변화
(※ 분석: 역마살, 지살 등 이동의 기운이 내담자의 사주에 어떤 활력을 주는지 분석하십시오.)

2. 평안과 안정을 부르는 최적의 이사 길일
[WEEKLY_CALENDAR_HERE]
1) 나에게 완벽하게 맞는 이사 날짜와 명리적 이유
(※ 분석: 탐색된 최적의 이사 길일이 사주 원국과 어떻게 조화(합, 상생)를 이루는지 서술하십시오.)
2) 흉한 기운을 피하고 좋은 기운만 담은 날의 선택
(※ 분석: 일진의 충극과 공망을 철저히 배제하여 가정이 평안할 것임을 입증하십시오.)

3. 복을 부르는 이사 당일의 지혜와 풍수
1) 이사 당일 행운을 부르는 시간대(길시)
(※ 분석: 이사 당일 흉시를 피하고 짐을 들이기 좋은 길시를 지정하십시오.)
2) 새로운 집을 안락하게 채울 개운 풍수 팁
(※ 분석: 용희신 방향이나 행운의 색상 등 평안을 부르는 생활 풍수를 조언하십시오.)
"""

                elif u_product == "2-7. 개업 택일":
                    prompt = 공통_시스템_헤더 + f"""
[SYSTEM ROLE: 초연 전통명리 최고위 비즈니스 택일 마스터]
정통 명리학의 일진 생극제화 및 재성/식상이 살아나는 길일을 연산하여, 사업 번창과 금전 유입을 극대화할 수 있는 완벽한 개업 길일을 추천하는 트렌디하고 에너지 넘치는 응원의 에세이를 작성하십시오.

🚨 [출력 목차 강제 지시]: 아래 제목을 100% 그대로 출력하십시오.

[출력 서식 및 통변 지침]

1. 새로운 도약과 사업 시작의 타이밍
[DAEWUN_TABLE_HERE]
[SEWUN_TABLE_HERE]
1) 개업이 내 운명에 불어넣을 새로운 성장의 기운
(※ 분석: 사주의 식상생재 기운을 바탕으로 사업 개창의 운기가 발동하고 있음을 희망차게 서술하십시오.)

2. 재물과 번창을 부르는 최적의 개업 길일
[WEEKLY_CALENDAR_HERE]
1) 성공적인 시작을 위한 최고의 날짜와 명리적 이유
(※ 분석: 탐색된 개업 길일이 내담자의 재성운을 어떻게 돕는지 명리적 근거(상생, 합)로 서술하십시오.)
2) 리스크를 피하고 현금 흐름을 지키는 날의 선택
(※ 분석: 비견/겁재 운이나 충극일을 철저히 배제했음을 든든하게 입증하십시오.)

3. 대박을 터뜨릴 오픈 당일의 지혜와 비즈니스 풍수
1) 손님을 끌어모을 개업 당일의 최적 시간대(길시)
(※ 분석: 첫 손님을 맞이하거나 고사를 지내기 좋은 최상의 오픈 길시를 지정하십시오.)
2) 재물을 당기는 사업장 풍수와 인테리어 팁
(※ 분석: 금전등록기 위치, 간판 방향 등 사업 번창을 돕는 개운 풍수를 조언하십시오.)
"""

                try:
                    res = model.generate_content(prompt)
                    ai_text = "\n".join([line.lstrip() for line in res.text.split("\n")])
                    
                    # 🚨 AI 프롬프트의 테이블 마커 찌꺼기를 안전하게 청소
                    ai_text = ai_text.replace("[WEEKLY_CALENDAR_HERE]", "").replace("[DAEWUN_TABLE_HERE]", "").replace("[SEWUN_TABLE_HERE]", "")
                    
                    # 🚨 2-6, 2-7 전용 택일 결과 블록 생성 로직
                    extra_html = ""
                    if u_product in ["2-6. 이사 택일", "2-7. 개업 택일"]:
                        s_d_val = start_date if start_date else dt_mod.date.today()
                        e_d_val = end_date if end_date else dt_mod.date.today() + dt_mod.timedelta(days=30)
                        FORBIDDEN_LIST = ['병오', '임자', '계해', '신유', '경신']
                        recommended_days = get_optimized_delivery_days(s_d_val, e_d_val, jjis, jjis, FORBIDDEN_LIST)
                        
                        extra_html += f"<h3 style='color:#4A148C; text-align:center; margin-top:20px;'>📅 추천 길일 (탐색기간: {s_d_val} ~ {e_d_val})</h3>\n"
                        for day_info in recommended_days:
                            extra_html += f"<div style='font-size:16px; font-weight:bold; margin-bottom:8px; padding:8px; background:#F8F9FA; border-radius:6px; text-align:center;'>✅ 추천 길일: <b style='color:#D50000;'>{day_info['date']}</b> (명리 적합도: {day_info['score']}점)</div>\n"
                        extra_html += "<hr style='border:1px dashed #4A148C; margin:15px 0;'>\n"

                    full_content_clean = f"<div style='font-family: \"Nanum Myeongjo\", \"바탕체\", Batang, serif; font-size: 15px; line-height: 1.8; color: #000000;'>{extra_html}{ai_text}<br><br>{closing_html}</div>"

                    report_1_full_html = report_1_full_html.replace("{full_content_clean_placeholder}", full_content_clean)
                    
                    st.session_state['saved_report_html'] = report_1_full_html
                    
                except Exception as e: 
                    st.error(f"테마별 특성화 분석 AI 연산 오류: {e}")

            # ==============================================================
            # [A-3] 4-1. 타 감명서 비교 (사주) 파이프라인
            # ==============================================================
            elif main_category == "4. 타 감명서 비교" and u_product == "4-1. 타 감명서 비교 (사주)":
                comp_prompt = f"""
[SYSTEM ROLE: CHOYEON SYSTEM CHIEF CHANCELLOR]
당신은 '초연 박사님'을 보좌하는 수석보좌관 AI입니다.
제출된 타 감명서 원문과 초연시공명리의 정밀 사주풀이 팩트를 1:1로 엄밀히 비교 대조하여 학술 검증 리포트를 작성하십시오.
타 감명서의 고전적/단식적 해석(단순 신살, 오행 개수 위주)과 초연 시공명리(월령 시공간, 일주 구조, 대운 파동)의 입체적 해석을 1:1로 대조하여 차이점을 서술하십시오.
"""
                try:
                    c_res = call_claude_api(comp_prompt, max_tokens=10000)
                    
                    report_2_html = (
                        f"<div class='page-break-before'></div>\n"
                        f"<div class='report-page'>\n"
                        f"<div class='vip-inset-frame' style='border-color:#2E7D32; padding:20px;'>\n"
                        f"<h1 style='text-align:center; color:#2E7D32; font-size: 26px; font-weight: 900; border-bottom:2px solid #2E7D32; padding-bottom:15px; margin-bottom:20px;'>⚖️ 타 감명서 학술 검증 및 1:1 대조 리포트</h1>\n"
                        f"<div style='margin-top:20px;'>{c_res}</div>\n"
                        f"<hr style='border:1px dashed #2E7D32; margin:30px 0;'>\n"
                        f"<h3 style='color:#555; font-size:18px; font-weight:900; margin-bottom:10px;'>📜 [제출된 타 감명서 원문]</h3>\n"
                        f"<div style='font-family: \"Nanum Myeongjo\", serif; font-size: 14px; line-height: 1.8; color: #444; background:#F9F9F9; padding:15px; border-radius:8px;'>{other_reading_text.replace(chr(10), '<br>')}</div>\n"
                        f"</div>\n"
                        f"</div>"
                    )
                    st.session_state['saved_report_2'] = report_2_html
                except Exception as e:
                    st.error(f"비교 분석 가동 장애: {e}")

            # ==============================================================
            # [C] 2인 명조 파이프라인 (궁합 3-1, 택일 3-2/3-3, 타감명서 궁합 4-2)
            # ==============================================================
            elif is_2person_product:
                try:
                    p_klc = KoreanLunarCalendar()
                    if p_cal == "양력": p_klc.setSolarDate(p_y, p_m, p_d)
                    elif p_cal == "음력(평달)": p_klc.setLunarDate(p_y, p_m, p_d, False)
                    else: p_klc.setLunarDate(p_y, p_m, p_d, True)
                    
                    p_is_leap = getattr(p_klc, 'isIntercalary', False)
                    p_leap_str = "윤달" if p_is_leap else "평달"
                    p_sol_str = f"{p_klc.solarYear}년 {p_klc.solarMonth:02d}월 {p_klc.solarDay:02d}일"
                    p_lun_str = f"{p_klc.lunarYear}년 {p_klc.lunarMonth:02d}월 {p_klc.lunarDay:02d}일 ({p_leap_str})"
                    p_age = curr_y - p_y + 1
                    
                    p_base_dt = dt_mod.datetime(p_y, p_m, p_d, 12, 0)
                    p_gj = p_klc.getChineseGapJaString().split()
                    p_ys, p_yb, p_ms, p_mb, p_ds, p_db = p_gj[0][0], p_gj[0][1], p_gj[1][0], p_gj[1][1], p_gj[2][0], p_gj[2][1]
                    p_hs, p_hb = get_time_ganji(p_ds, p_t, p_base_dt)
                    
                    partner_bazi = [f"{p_hs}{p_hb}", f"{p_ds}{p_db}", f"{p_ms}{p_mb}", f"{p_ys}{p_yb}"]
                    st.session_state['partner_bazi'] = partner_bazi

                    if u_gender == "남성":
                        m_name, m_sol, m_lun, m_time, m_age = u_name, sol_str, lun_str, time_str, u_age
                        m_gans, m_jjis = gans, jjis
                        m_ys, m_yb, m_ms, m_mb, m_ds, m_db, m_hs, m_hb = ys, yb, ms, mb, ds, db, hs, hb
                        m_calc_d, m_order = calc_d, order
                        
                        f_name, f_sol, f_lun, f_time, f_age = p_name, p_sol_str, p_lun_str, f" {p_t.split('(')[0].strip()} ({p_hb})시" if p_t != "시간 모름" else "", p_age
                        f_gans, f_jjis = [p_hs, p_ds, p_ms, p_ys], [p_hb, p_db, p_mb, p_yb]
                        f_ys, f_yb, f_ms, f_mb, f_ds, f_db, f_hs, f_hb = p_ys, p_yb, p_ms, p_mb, p_ds, p_db, p_hs, p_hb
                        p_utc_dt = p_base_dt - dt_mod.timedelta(hours=9) + dt_mod.timedelta(minutes=get_total_time_adjustment(p_base_dt))
                        p_order = 1 if (GAN.index(p_ys)%2==0) == (p_gender=='남성') else -1
                        f_calc_d, f_order = get_daeun_su_accurate(p_utc_dt, p_order), p_order
                        
                        male_data_pack, female_data_pack = applicant_bazi, partner_bazi
                    else:
                        m_name, m_sol, m_lun, m_time, m_age = p_name, p_sol_str, p_lun_str, f" {p_t.split('(')[0].strip()} ({p_hb})시" if p_t != "시간 모름" else "", p_age
                        m_gans, m_jjis = [p_hs, p_ds, p_ms, p_ys], [p_hb, p_db, p_mb, p_yb]
                        m_ys, m_yb, m_ms, m_mb, m_ds, m_db, m_hs, m_hb = p_ys, p_yb, p_ms, p_mb, p_ds, p_db, p_hs, p_hb
                        p_utc_dt = p_base_dt - dt_mod.timedelta(hours=9) + dt_mod.timedelta(minutes=get_total_time_adjustment(p_base_dt))
                        p_order = 1 if (GAN.index(p_ys)%2==0) == (p_gender=='남성') else -1
                        m_calc_d, m_order = get_daeun_su_accurate(p_utc_dt, p_order), p_order
                        
                        f_name, f_sol, f_lun, f_time, f_age = u_name, sol_str, lun_str, time_str, u_age
                        f_gans, f_jjis = gans, jjis
                        f_ys, f_yb, f_ms, f_mb, f_ds, f_db, f_hs, f_hb = ys, yb, ms, mb, ds, db, hs, hb
                        f_calc_d, f_order = calc_d, order
                        
                        male_data_pack, female_data_pack = partner_bazi, applicant_bazi

                    if u_product == "4-2. 타 감명서 비교 (궁합)":
                        m_name_val = u_name if u_gender == "남성" else p_name
                        f_name_val = p_name if u_gender == "남성" else u_name
                        
                        gh_engine = UniversalPrintableGunghap(m_name_val, f_name_val, male_data_pack, female_data_pack, 10)
                        gh_engine.run_universal_logic()

                        comp_prompt = f"""
[SYSTEM ROLE: CHOYEON SYSTEM CHIEF CHANCELLOR (초연시공명리 수석보좌관)]
당신은 '초연 박사님'을 보좌하는 수석보좌관 AI입니다.
제출된 [{m_name_val}님과 {f_name_val}님의 외부 궁합 감명서 원문]을 박사님의 [초연시공명리 궁합 정밀 통변 팩트]와 1:1로 엄밀히 비교 대조하여 학술 검증 리포트를 작성하십시오.
"""
                        c_res = call_claude_api(comp_prompt, max_tokens=10000)
                        
                        report_2_html = (
                            f"<div class='page-break-before'></div>\n"
                            f"<div class='report-page'>\n"
                            f"<div class='vip-inset-frame' style='border-color:#C62828; padding:20px;'>\n"
                            f"<h1 style='text-align:center; color:#C62828; font-size: 26px; font-weight: 900; border-bottom:2px solid #C62828; padding-bottom:15px; margin-bottom:20px;'>⚖️ 타 궁합 감명서 학술 검증 및 1:1 대조 리포트</h1>\n"
                            f"<div style='margin-top:20px;'>{c_res}</div>\n"
                            f"<hr style='border:1px dashed #C62828; margin:30px 0;'>\n"
                            f"<h3 style='color:#555; font-size:18px; font-weight:900; margin-bottom:10px;'>📜 [제출된 타 감명서 원문]</h3>\n"
                            f"<div style='font-family: \"Nanum Myeongjo\", serif; font-size: 14px; line-height: 1.8; color: #444; background:#F9F9F9; padding:15px; border-radius:8px;'>{other_reading_text.replace(chr(10), '<br>')}</div>\n"
                            f"</div>\n"
                            f"</div>"
                        )
                        st.session_state['saved_report_2'] = report_2_html

                    else:
                        curr_j = JI[((curr_y - 1984) % 60) % 12]

                        def get_counts(t_gans, t_jjis):
                            c = {"목":0,"화":0,"토":0,"금":0,"수":0}
                            for x in t_gans + t_jjis:
                                if x != "?": c[get_color(x)] += 1
                            return c

                        m_cnt, f_cnt = get_counts(m_gans, m_jjis), get_counts(f_gans, f_jjis)

                        m_name = m_name.replace("+", "").strip()
                        f_name = f_name.replace("+", "").strip()

                        def build_bazi_table(gender_icon, name, gender_str, marital_str, age, sol, lun, time, t_gans, t_jjis, t_ds, t_yb, counts, guiin, y_gong, d_gong, samjae, daeun_su, color):
                            ji_rel_rows = ""
                            for l_idx, r_idx in enumerate([1, 2, 0, 3]):
                                b_bot = "1px solid #444 !important" if l_idx == 3 else "none !important"
                                cells = "".join([f"<td style='color:{('#D50000' if ci==r_idx else ('#000' if get_ji_rel_set(t_jjis[r_idx], t_jjis[ci])!='-' else '#BBB'))}; font-weight:900; border-top:none !important; border-bottom:{b_bot}; border-left:1px solid #444 !important; border-right:1px solid #444 !important;'><span style='color:inherit !important;'>{('←('+t_jjis[r_idx]+')→' if ci==r_idx else get_ji_rel_set(t_jjis[r_idx], t_jjis[ci]))}</span></td>" for ci in range(4)])
                                lbl = f"<td rowspan='4' class='header-cell-main' style='border:1px solid #444 !important;'><span style='color:inherit !important;'>합충형파해</span></td>" if l_idx==0 else ""
                                ji_rel_rows += f"<tr>{lbl}{cells}</tr>"

                            info_str = f"<div style='text-align:center; margin-bottom:15px; font-family:\"Malgun Gothic\", sans-serif;'><span style='font-size:18px; font-weight:900; color:{color};'>{gender_icon} {name}님 ({gender_str}, {marital_str}, {age}세)</span><br><span style='font-size:14px; font-weight:900; color:#222;'>[양력] {sol} | [음력] {lun}{time}</span></div>"
                            
                            def td(c): return f"<td class='color-{get_color(c)}' style='font-size:20px; font-weight:900; border:1px solid #444 !important;'><span style='color:inherit !important;'>{('?' if c in ['?',' ','-'] else c)}</span></td>"
                            
                            return (
                                f"{info_str}\n"
                                f"<table class='result-table' style='width:100%; border-collapse:collapse; text-align:center;'>\n"
                                f"<tr class='top-header-cell'>\n"
                                f"<td style='border:1px solid #444; font-size:15px !important; white-space:nowrap;'><span style='color:#FFFFFF !important;'>구분</span></td>\n"
                                f"<td style='border:1px solid #444; font-size:15px !important; white-space:nowrap;'><span style='color:#FFFFFF !important;'>시주</span></td>\n"
                                f"<td style='border:1px solid #444; font-size:15px !important; white-space:nowrap;'><span style='color:#FFFFFF !important;'>일주</span></td>\n"
                                f"<td style='border:1px solid #444; font-size:15px !important; white-space:nowrap;'><span style='color:#FFFFFF !important;'>월주</span></td>\n"
                                f"<td style='border:1px solid #444; font-size:15px !important; white-space:nowrap;'><span style='color:#FFFFFF !important;'>년주</span></td>\n"
                                f"</tr>\n"
                                f"<tr><td class='header-cell-main' style='border:1px solid #444; font-size:15px !important; white-space:nowrap;'><span style='color:inherit !important;'>천간십성</span></td><td style='border:1px solid #444;'><span style='color:inherit !important;'>{get_ss(t_ds,t_gans[0])}</span></td><td style='border:1px solid #444;'><span style='color:#D50000; font-weight:900;'>日元</span></td><td style='border:1px solid #444;'><span style='color:inherit !important;'>{get_ss(t_ds,t_gans[2])}</span></td><td style='border:1px solid #444;'><span style='color:inherit !important;'>{get_ss(t_ds,t_gans[3])}</span></td></tr>\n"
                                f"<tr><td class='header-cell-main' style='border:1px solid #444; font-size:15px !important; white-space:nowrap;'><span style='color:inherit !important;'>천간</span></td>{td(t_gans[0])}{td(t_gans[1])}{td(t_gans[2])}{td(t_gans[3])}</tr>\n"
                                f"<tr><td class='header-cell-main' style='border:1px solid #444; font-size:15px !important; white-space:nowrap;'><span style='color:inherit !important;'>지지</span></td>{td(t_jjis[0])}{td(t_jjis[1])}{td(t_jjis[2])}{td(t_jjis[3])}</tr>\n"
                                f"<tr><td class='header-cell-main' style='border:1px solid #444; font-size:15px !important; white-space:nowrap;'><span style='color:inherit !important;'>지지십성</span></td><td style='border:1px solid #444;'><span style='color:inherit !important;'>{get_ss(t_ds,t_jjis[0])}</span></td><td style='border:1px solid #444;'><span style='color:inherit !important;'>{get_ss(t_ds,t_jjis[1])}</span></td><td style='border:1px solid #444;'><span style='color:inherit !important;'>{get_ss(t_ds,t_jjis[2])}</span></td><td style='border:1px solid #444;'><span style='color:inherit !important;'>{get_ss(t_ds,t_jjis[3])}</span></td></tr>\n"
                                f"<tr><td class='header-cell-main' style='border:1px solid #444; padding:0; font-size:15px !important; white-space:nowrap;'><span style='color:inherit !important;'>지장간</span></td>{''.join([f'<td style=\"border:1px solid #444; padding:0;\"><span style=\"color:inherit !important;\">{get_jijanggan_full(t_ds, t_jjis[i])}</span></td>' for i in range(4)])}</tr>\n"
                                f"{ji_rel_rows}\n"
                                f"<tr><td class='header-cell-main' style='border:1px solid #444; font-size:15px !important; white-space:nowrap;'><span style='color:inherit !important;'>십이운성</span></td>{''.join([f'<td style=\"border:1px solid #444; color:#0D47A1; font-weight:bold;\"><span style=\"color:inherit !important;\">{get_unsung(t_ds, t_jjis[i])}</span></td>' for i in range(4)])}</tr>\n"
                                f"<tr><td class='header-cell-main' style='border:1px solid #444; font-size:15px !important; white-space:nowrap;'><span style='color:inherit !important;'>십이신살</span></td>{''.join([f'<td style=\"border:1px solid #444; color:#C62828; font-weight:bold;\"><span style=\"color:inherit !important;\">{get_12_shinsal(t_yb, t_jjis[i])}</span></td>' for i in range(4)])}</tr>\n"
                                f"</table>\n"
                                f"<div style='border:2px solid {color}; margin-top:10px; margin-bottom:20px; padding:6px 8px; display:flex; justify-content:space-between; align-items:center; font-weight:900; font-size:11px; letter-spacing:-0.5px; border-radius:8px; background-color:#FAFAFA;'><div style='white-space:nowrap;'>🔢 대운수: {daeun_su}</div><div style='white-space:nowrap;'>💥 오행: 木({counts['목']}) 火({counts['화']}) 土({counts['토']}) 金({counts['금']}) 水({counts['수']})</div><div style='white-space:nowrap;'>🌟 천을귀인: <span style='color:{color};'>{guiin}</span></div><div style='white-space:nowrap;'>🎯 공망: [년] <span style='color:#C62828;'>{y_gong}</span> [일] <span style='color:#C62828;'>{d_gong}</span></div><div style='white-space:nowrap;'>🌪️ 삼재: {samjae}</div></div>"
                            )

                        m_marital = u_marital if u_gender == "남성" else p_marital
                        f_marital = p_marital if u_gender == "남성" else u_marital
                        
                        guiin_map = {'甲':'丑, 未','乙':'子, 申','丙':'酉, 亥','丁':'酉, 亥','戊':'丑, 未','己':'子, 申','庚':'丑, 未','辛':'午寅','壬':'卯巳','癸':'卯, 巳'}
                        
                        m_tbl = build_bazi_table("♂️", m_name, "남명", m_marital, m_age, m_sol, m_lun, m_time, m_gans, m_jjis, m_ds, m_yb, m_cnt, guiin_map.get(m_ds, '-'), calculate_gongmang(m_ys, m_yb), calculate_gongmang(m_ds, m_db), get_samjae(m_yb, curr_j), m_calc_d, "#1A237E")
                        f_tbl = build_bazi_table("♀️", f_name, "여명", f_marital, f_age, f_sol, f_lun, f_time, f_gans, f_jjis, f_ds, f_yb, f_cnt, guiin_map.get(f_ds, '-'), calculate_gongmang(f_ys, f_yb), calculate_gongmang(f_ds, f_db), get_samjae(f_yb, curr_j), f_calc_d, "#2E7D32")
                        
                        def build_daewun_html(name, t_ds, t_ms, t_mb, t_yb, t_calc_d, t_order, age, color):
                            d_str = "순행" if t_order == 1 else "역행"
                            html = f"<div style='margin-bottom:10px;'><div style='font-size:15px; font-weight:900; color:{color}; margin-bottom:5px;'>[ {name}님 대운 흐름표 (대운수: {t_calc_d}), {d_str} ]</div>"
                            html += f"<div style='display:flex; flex-direction:row-reverse; width:100%; border:2px solid #3E2723; background:white;'>"
                            for i in range(10):
                                val = i*10 + t_calc_d
                                tc = GAN[(GAN.index(t_ms)+(i+1)*t_order)%10]
                                tj = JI[(JI.index(t_mb)+(i+1)*t_order)%12]
                                bg = "#FFF9C4" if val <= age < val+10 else "transparent"
                                brd = "1px solid #ccc" if i != 9 else "none"
                                html += f"<div style='flex:1; border-left:{brd}; text-align:center; padding-bottom:3px; background-color:{bg};'><div style='background-color:#3E2723; color:#FFFFFF; font-weight:900; padding:4px 0; font-size:11px; border-bottom:1px solid #ccc;'>{val}세</div><div style='padding:2px; font-size:11px;'>{get_ss(t_ds,tc)}</div><div class='color-{get_color(tc)}' style='font-size:15px; font-weight:900;'>{tc}</div><div class='color-{get_color(tj)}' style='font-size:15px; font-weight:900;'>{tj}</div><div style='padding:2px; font-size:11px;'>{get_ss(t_ds,tj)}</div><div style='font-size:10px; border-top:1px solid #eee;'>{get_unsung(t_ds,tj)}</div><div style='font-size:10px; color:#C62828; border-top:1px solid #eee;'>{get_12_shinsal(t_yb, tj)}</div></div>"
                            return html + "</div></div>"

                        m_page_un_html = build_daewun_html(m_name, m_ds, m_ms, m_mb, m_yb, m_calc_d, m_order, m_age, "#1A237E")
                        f_page_un_html = build_daewun_html(f_name, f_ds, f_ms, f_mb, f_yb, f_calc_d, f_order, f_age, "#2E7D32")
                        
                        couple_daewun_tables = f"<div style='margin-bottom: 25px;'>{m_page_un_html}<div style='height:20px;'></div>{f_page_un_html}</div>"

                        ilju_struct_db = choyeon_db.get("ilju_structure", {})

                        m_ilju_key = f"{m_ds}{m_db}"
                        m_struct_data = ilju_struct_db.get(m_ilju_key, [])
                        m_action_type = m_struct_data[1] if len(m_struct_data) >= 3 else "자율활동형"
                        m_main_tendency = m_struct_data[2] if len(m_struct_data) >= 3 else "독자적인 삶의 무대를 개척하는"
                        m_gy_name, m_gy_desc = get_gyukgook_detailed(m_ds, m_ys, m_ms, m_hs, m_mb)

                        m_traditional_text_html = f"""
                        <div style='font-family: "Nanum Myeongjo", "바탕체", Batang, serif; font-size: 15px; line-height: 1.8; color: #000000; margin-bottom: 20px;'>
                            <p style='text-indent: 15px; margin-bottom: 5px;'>
                                정통 명리학적으로 풀이하면 <b>{m_name}님</b>은 <b>{m_mb}월</b>에 <b>'{m_gy_name}'</b>의 그릇을 갖추고 태어나셨으며, 성격은 <b>'{m_action_type}'</b>으로 <b>'{m_main_tendency}'</b> 성향이 있습니다.
                            </p>
                        </div>
                        <hr style="border: 0; border-top: 2px solid #000000; margin: 25px 0;">
                        """

                        f_ilju_key = f"{f_ds}{f_db}"
                        f_struct_data = ilju_struct_db.get(f_ilju_key, [])
                        f_action_type = f_struct_data[1] if len(f_struct_data) >= 3 else "자율활동형"
                        f_main_tendency = f_struct_data[2] if len(f_struct_data) >= 3 else "독자적인 삶의 무대를 개척하는"
                        f_gy_name, f_gy_desc = get_gyukgook_detailed(f_ds, f_ys, f_ms, f_hs, f_mb)

                        f_traditional_text_html = f"""
                        <div style='font-family: "Nanum Myeongjo", "바탕체", Batang, serif; font-size: 15px; line-height: 1.8; color: #000000; margin-bottom: 20px;'>
                            <p style='text-indent: 15px; margin-bottom: 5px;'>
                                정통 명리학적으로 풀이하면 <b>{f_name}님</b>은 <b>{f_mb}월</b>에 <b>'{f_gy_name}'</b>의 그릇을 갖추고 태어나셨으며, 성격은 <b>'{f_action_type}'</b>으로 <b>'{f_main_tendency}'</b> 성향이 있습니다.
                            </p>
                        </div>
                        <hr style="border: 0; border-top: 2px solid #000000; margin: 25px 0;">
                        """

                        gh_engine = UniversalPrintableGunghap(u_name, p_name, male_data_pack, female_data_pack, 10)
                        gh_engine.run_universal_logic()
                        
                        essay_prompt = f"""[SYSTEM ROLE: CHOYEON TRADITIONAL MASTER]
당신은 정통 명리심리상담사 '초연 박사'입니다.

🚨 [출력 절대 형식 및 내용 생성 규칙]
1. 각 소제목 아래에 절대로 안내 문구를 그대로 복사해서 출력하지 마십시오!
2. 반드시 내담자의 명리적 특징을 분석하여 3~4문장 분량의 실제 통변 내용을 직접 작성해야 합니다.
3. 모든 통변 문장은 HTML 태그 <p style='font-family: "Nanum Myeongjo", serif; font-size: 15px; line-height: 1.8; color: #000; text-indent: 1em; text-align: justify;'> 로 감싸하십시오.

[MALE_START]
<h3 style='color:#1A237E; font-size: 22px; font-weight: 900; margin-top: 15px;'>1. 성격 및 가치관</h3>
<span class='sub-title' style='display: block; font-size: 18px; font-weight: 900; color: #111; margin-top: 15px; margin-bottom: 5px;'>1) 겉으로 드러난 성격</span>
(이곳에 남성의 사회적 표면 성격을 분석한 실제 에세이 작성)
<span class='sub-title' style='display: block; font-size: 18px; font-weight: 900; color: #111; margin-top: 15px; margin-bottom: 5px;'>2) 감추어진 내 속마음</span>
(이곳에 남성의 내면과 무의식을 분석한 실제 에세이 작성)
<span class='sub-title' style='display: block; font-size: 18px; font-weight: 900; color: #111; margin-top: 15px; margin-bottom: 5px;'>3) 무의식이 갈망하는 반려자의 상</span>
(남성의 연애 및 결혼관을 실제 에세이로 작성)

<h3 style='color:#1A237E; font-size: 22px; font-weight: 900; margin-top: 15px;'>2. 사주팔자의 요약</h3>
{m_traditional_text_html}
<span class='sub-title' style='display: block; font-size: 18px; font-weight: 900; color: #111; margin-top: 15px; margin-bottom: 5px;'>1) 타고난 삶의 무대와 기본 성향</span>
(이곳에 남성의 정통 명리적 성향을 분석한 실제 에세이 작성)
<span class='sub-title' style='display: block; font-size: 18px; font-weight: 900; color: #111; margin-top: 15px; margin-bottom: 5px;'>2) 내 삶의 리듬과 에너지 균형</span>
(이곳에 남성의 오행 및 조후 에너지를 분석한 실제 에세이 작성)
[MALE_END]

[FEMALE_START]
<h3 style='color:#D50000; font-size: 22px; font-weight: 900; margin-top: 15px;'>1. 성격 및 가치관</h3>
<span class='sub-title' style='display: block; font-size: 18px; font-weight: 900; color: #111; margin-top: 15px; margin-bottom: 5px;'>1) 겉으로 드러난 성격</span>
(이곳에 여성의 사회적 표면 성격을 분석한 실제 에세이 작성)
<span class='sub-title' style='display: block; font-size: 18px; font-weight: 900; color: #111; margin-top: 15px; margin-bottom: 5px;'>2) 감추어진 내 속마음</span>
(이곳에 여성의 내면과 무의식을 분석한 실제 에세이 작성)
<span class='sub-title' style='display: block; font-size: 18px; font-weight: 900; color: #111; margin-top: 15px; margin-bottom: 5px;'>3) 무의식이 갈망하는 반려자의 상</span>
(여성의 연애 및 결혼관을 실제 에세이로 작성)

<h3 style='color:#D50000; font-size: 22px; font-weight: 900; margin-top: 15px;'>2. 사주팔자의 요약</h3>
{f_traditional_text_html}
<span class='sub-title' style='display: block; font-size: 18px; font-weight: 900; color: #111; margin-top: 15px; margin-bottom: 5px;'>1) 타고난 삶의 무대와 기본 성향</span>
(이곳에 여성의 정통 명리적 성향을 분석한 실제 에세이 작성)
<span class='sub-title' style='display: block; font-size: 18px; font-weight: 900; color: #111; margin-top: 15px; margin-bottom: 5px;'>2) 내 삶의 리듬과 에너지 균형</span>
(이곳에 여성의 오행 및 조후 에너지를 분석한 실제 에세이 작성)
[FEMALE_END]

[GUNGHAP_START]
<h3 style='color: #1B5E20; font-size: 22px; font-weight: 900; margin-top: 10px;'>🍀 두 사람의 운명적 만남에 대하여</h3>
(이곳에 두 사람의 인연 총평을 깊이 있게 통변한 실제 에세이 작성)

<h3 style='color: #1A237E; font-size: 22px; font-weight: 900; margin-top: 25px;'>🌈 커플의 인생 기상도 분석</h3>
[COUPLE_DAEWUN_TABLES_HERE]
(이곳에 상하 대운 교차점에 따른 상생/보완을 분석한 실제 에세이 작성)

<h4 style='color: #1A237E; font-size: 18px; font-weight: 900; margin-top: 25px;'>💞 커플의 상생과 조화 궁합 분석</h4>
(이곳에 속궁합, 겉궁합, 오행 궁합을 통합 분석한 실제 에세이 작성)

<h4 style='color: #1A237E; font-size: 18px; font-weight: 900; margin-top: 25px;'>⚓ 조율의 지혜</h4>
(이곳에 갈등 극복 및 개운 처방을 담은 실제 에세이 작성)
[GUNGHAP_END]
"""
                        res_text = call_claude_api(essay_prompt, max_tokens=12000)
                        ai_clean = "\n".join([line.lstrip() for line in res_text.split("\n")])
                        
                        m_ess, f_ess, g_ess = "", "", ai_clean
                        
                        m_match = re.search(r'\[MALE_START\](.*?)\[MALE_END\]', ai_clean, re.DOTALL)
                        if m_match: m_ess = m_match.group(1).strip()
                        
                        f_match = re.search(r'\[FEMALE_START\](.*?)\[FEMALE_END\]', ai_clean, re.DOTALL)
                        if f_match: f_ess = f_match.group(1).strip()
                        
                        g_match = re.search(r'\[GUNGHAP_START\](.*?)\[GUNGHAP_END\]', ai_clean, re.DOTALL)
                        if g_match: 
                            g_ess = g_match.group(1).strip()
                        else:
                            g_ess = ai_clean.replace(m_ess, "").replace(f_ess, "").replace("[MALE_START]", "").replace("[MALE_END]", "").replace("[FEMALE_START]", "").replace("[FEMALE_END]", "")
                        
                        g_ess, count = re.subn(r'\[\s*COUPLE_DAEWUN_TABLES_HERE\s*\]', couple_daewun_tables, g_ess, flags=re.IGNORECASE)
                        if count == 0:
                            g_ess = re.sub(r'(<h3[^>]*>🌈 커플의 인생 기상도 분석</h3>)', r'\1\n<div style="margin-top:15px;">' + couple_daewun_tables + '</div>', g_ess)

                        def wrap_a4(content, title_color="#1A237E", title="[ 초연 전통 명리사주 풀이 ]"):
                            return (
                                f"<div class='report-page'>\n"
                                f"<div class='vip-inset-frame' style='border-color:{title_color}; padding:20px;'>\n"
                                f"<h1 style='text-align:center; color:{title_color}; font-family:\"Malgun Gothic\", sans-serif; font-weight:900; border-bottom:2px solid {title_color}; padding-bottom:15px; margin-bottom:30px;'>{title}</h1>\n"
                                f"{content}\n"
                                f"</div>\n"
                                f"</div>"
                            )

                        t_col = "#3498db" if gh_engine.final_score >= 70 else ("#f39c12" if gh_engine.final_score >= 60 else "#e74c3c")
                        bars = "".join([f"<div style='display:flex; align-items:center; margin-bottom:12px;'><div style='width:130px; font-size:13px; font-weight:bold; color:#555;'>{d['label']}</div><div style='flex:1; height:12px; margin:0 10px;'><svg width='100%' height='12'><rect width='100%' height='12' rx='6' ry='6' fill='#eee' /><rect width='{d['pct']}%' height='12' rx='6' ry='6' fill='{d['color']}' /></svg></div><div style='width:35px; font-size:12px; font-weight:bold;'>{d['pct']}%</div></div>" for d in gh_engine.details])
                        
                        closing_original = (
                            f"<div style='margin-top: 40px; padding-top: 30px; page-break-inside: avoid;'>\n"
                            f"<p style='font-family: \"Nanum Myeongjo\", serif; font-size: 15px; line-height: 1.8; color: #333;'>&nbsp;&nbsp;&nbsp;&nbsp;두 분의 <b style='color:#1A237E;'>'만남'</b>은 결코 우연이 아닌, <b style='color:#1A237E;'>'수많은 인연의 이치 속에서 기적처럼 찾아온 귀한 인연'</b>입니다. 사주팔자는 각자의 명식이지만, <b style='color:#1A237E;'>'궁합(宮合)'</b>은 두 명식이 만나 그려내는 새로운 <b style='color:#1A237E;'>'조화와 상생'</b>입니다.</p>\n"
                            f"<p style='font-family: \"Nanum Myeongjo\", serif; font-size: 15px; line-height: 1.8; color: #333; margin-top: 10px;'>&nbsp;&nbsp;&nbsp;&nbsp;서로의 기운을 보완하고 다독여주는 든든한 <b style='color:#1A237E;'>'반려자'</b>가 되시기를 진심으로 기원하며, 두 분의 앞날에 늘 전통 명리의 축복이 가득하시길 소망합니다.</p>\n"
                            f"<div style='text-align: right; margin-top: 25px;'><span style='font-weight: 900; font-size: 16px; color: #1A237E; font-family: \"Nanum Myeongjo\", serif;'>- 초연 전통명리 연구소 드림 -</span></div>\n"
                            f"</div>"
                        )

                        g_full_content = (
                            f"<div class='choyeon-premium-report'>\n{g_ess}\n</div>\n"
                            f"<h2 style='text-align:center; margin-top:40px; font-size:22px; font-weight:900;'>📊 최종 궁합 점수</h2>\n"
                            f"<div style='display:flex; justify-content:center; align-items:center; margin:20px 0;'>\n"
                            f"<div style='width:130px; height:130px; border-radius:50%; background:conic-gradient({t_col} {gh_engine.final_score}%, #eee 0); display:flex; justify-content:center; align-items:center; -webkit-print-color-adjust: exact;'>\n"
                            f"<div style='width:98px; height:98px; background:#fff; border-radius:50%; display:flex; flex-direction:column; justify-content:center; align-items:center;'>\n"
                            f"<span style='font-size:32px; font-weight:900; color:{t_col};'>{gh_engine.final_score}</span>\n"
                            f"<span style='font-size:10px; color:#888; font-weight:bold;'>SCORE</span>\n"
                            f"</div>\n"
                            f"</div>\n"
                            f"</div>\n"
                            f"<div style='text-align:center; margin-bottom:20px;'><span style='font-size:16px; font-weight:bold; color:#fff; background:{t_col}; padding:8px 32px; border-radius:30px; -webkit-print-color-adjust: exact;'>{gh_engine.grade}</span></div>\n"
                            f"<div style='max-width:500px; margin:0 auto;'>\n{bars}\n</div>\n"
                            f"{closing_original}"
                        )

                        cover_html = (
                            f"<div class='report-page cover-page' style='padding:0; margin:0; width:100%; height:297mm; display:flex; flex-direction:column; justify-content:center; align-items:center; page-break-after: always; -webkit-print-color-adjust: exact;'>\n"
                            f"    <div style='border: 4px solid #1A237E; padding: 50px 30px; border-radius: 20px; text-align: center; background: white; width: 80%; max-width: 600px; box-shadow: 0 10px 25px rgba(0,0,0,0.1); margin: auto;'>\n"
                            f"        <div style='border-bottom:4px double #1A237E; padding-bottom:20px; margin-bottom:40px;'>\n"
                            f"            <h1 class='title-gothic' style='font-size: 36px !important; margin:0 !important;'>초연 전통 명리궁합 풀이</h1>\n"
                            f"            <div style='text-align: right; margin-top: 10px;'>\n"
                            f"                <span class='ver-gothic' style='font-size: 14px; letter-spacing: 1px;'>{APP_VERSION}</span>\n"
                            f"            </div>\n"
                            f"        </div>\n"
                            f"        <div style='background:#F8F9FA; border: 1px solid #E8EAF6; padding: 25px 20px; border-radius: 15px; margin-bottom: 20px;'>\n"
                            f"            <h2 style='font-size: 24px; font-weight: 800; color: #1A237E; margin-bottom: 15px;'>♂️ 남명 : {m_name} 님 <span style='font-size:16px; color:#555;'>( {m_age}세 )</span></h2>\n"
                            f"            <div style='font-size: 15px; font-weight: 600; color: #555; line-height: 1.8;'>\n"
                            f"                <p style='margin: 0; white-space: nowrap;'>[양력] {m_sol} | [음력] {m_lun}</p>\n"
                            f"            </div>\n"
                            f"        </div>\n"
                            f"        <div style='background:#F8F9FA; border: 1px solid #E8EAF6; padding: 25px 20px; border-radius: 15px;'>\n"
                            f"            <h2 style='font-size: 24px; font-weight: 800; color: #D50000; margin-bottom: 15px;'>♀️ 여명 : {f_name} 님 <span style='font-size:16px; color:#555;'>( {f_age}세 )</span></h2>\n"
                            f"            <div style='font-size: 15px; font-weight: 600; color: #555; line-height: 1.8;'>\n"
                            f"                <p style='margin: 0; white-space: nowrap;'>[양력] {f_sol} | [음력] {f_lun}</p>\n"
                            f"            </div>\n"
                            f"        </div>\n"
                            f"        <p style='font-size: 18px; margin-top: 40px; font-weight: 800;'>{today_str}</p>\n"
                            f"        <p style='font-size: 22px; font-weight: 800; color: #1A237E; margin-top: 15px;'>초연 전통명리 연구소</p>\n"
                            f"    </div>\n"
                            f"</div>"
                        )
                        st.session_state['saved_report_gh_cover'] = cover_html

                        m_page_content = f"{m_tbl}\n<div class='choyeon-premium-report' style='margin-top:20px;'>\n{m_ess}\n</div>"
                        f_page_content = f"{f_tbl}\n<div class='choyeon-premium-report' style='margin-top:20px;'>\n{f_ess}\n</div>"
                        
                        st.session_state['saved_report_gh_m'] = wrap_a4(m_page_content, "#1A237E", "[ 남명 사주팔자표 및 요약 ]")
                        st.session_state['saved_report_gh_f'] = wrap_a4(f_page_content, "#D50000", "[ 여명 사주팔자표 및 요약 ]")
                        st.session_state['saved_report_gh_g'] = wrap_a4(g_full_content, "#1B5E20", "[ 초연 전통명리 종합 궁합풀이 ]")

                        if u_product in ["3-2. 결혼 택일", "3-3. 출산 택일"]:
                            s_d_val = start_date if start_date else dt_mod.date.today()
                            e_d_val = end_date if end_date else dt_mod.date.today() + dt_mod.timedelta(days=30)
                            m_jj_list = m_jjis if u_gender == "남성" else [b[1] if len(b)>1 else "?" for b in partner_bazi]
                            f_jj_list = [b[1] if len(b)>1 else "?" for b in partner_bazi] if u_gender == "남성" else m_jjis
                            
                            FORBIDDEN_LIST = ['병오', '임자', '계해', '신유', '경신']
                            delivery_days = get_optimized_delivery_days(s_d_val, e_d_val, m_jj_list, f_jj_list, FORBIDDEN_LIST)
                            
                            t_title = "💍 최고의 결혼 길일 추천 리포트" if u_product == "3-2. 결혼 택일" else "👶 새 생명 마중 출산 길일 추천"
                            del_content = f"<h2 style='text-align:center; color:#4A148C;'>{t_title}</h2><p style='text-align:center; font-weight:bold; color:#555;'>탐색 기간: {s_d_val} ~ {e_d_val} (태아 성별: {baby_gender})</p><hr style='border:1px dashed #4A148C; margin:15px 0;'>\n"
                            for day_info in delivery_days:
                                del_content += f"<div style='font-size:16px; font-weight:bold; margin-bottom:8px; padding:8px; background:#F8F9FA; border-radius:6px;'>✅ 추천 길일: <b>{day_info['date']}</b> (조화 점수: {day_info['score']}점)</div>\n"
                            
                            delivery_prompt = f"""
[SYSTEM ROLE: CHOYEON TRADITIONAL MASTER]
당신은 정통 명리심리상담사 '초연 박사'입니다. 부모의 사주 원국 기운을 바탕으로 탐색 기간 내에 태어날 아기에게 가장 길하고 복된 최고의 프리미엄 희망일/길일을 선정하여 전통 명리 에세이로 상세히 풀어내십시오.
- 부모 원국: 남명({m_name}) / 여명({f_name})
- 탐색 기간: {s_d_val} ~ {e_d_val} / 태아 성별: {baby_gender}
"""
                            del_res = model.generate_content(delivery_prompt)
                            ai_delivery_html = del_res.text.strip().replace("\n", "<br>")
                            del_content += f"<div class='content-box-loose' style='font-size:15px; line-height:1.8; margin-top:20px;'>\n{ai_delivery_html}\n</div>"

                            def wrap_takil_a4(content, title_color="#4A148C", title="[ 초연 전통명리 택일 리포트 ]"):
                                return f"<div class='report-page'>\n<div class='vip-inset-frame' style='border-color:{title_color}; padding:20px;'>\n<h1 style='text-align:center; color:{title_color}; font-family:\"Malgun Gothic\", sans-serif; font-weight:900; border-bottom:2px solid {title_color}; padding-bottom:15px; margin-bottom:30px;'>{title}</h1>\n{content}\n</div>\n</div>"

                            st.session_state['saved_report_del'] = wrap_takil_a4(del_content, "#4A148C", f"[ 초연 전통명리 {u_product} ]")

                except Exception as e:
                    st.error(f"3단계 궁합 종합 분석 가동 장애: {e}")

            st.session_state['need_calc'] = False

        except Exception as e: 
            st.error(f"시스템 연산 중 치명적 오류 발생: {e}")
            st.session_state['need_calc'] = False
            st.stop()

# ==============================================================================
# 🌊 7. [독립 모듈] 일진 분석 (오류 검증 완료)
# ==============================================================================
if st.session_state.get('app_running', False) and st.session_state.get('run_waterfall', False) and 'global_gans' in st.session_state:
    if not st.session_state.get('saved_report_iljin'):
        if st.session_state.get('saved_report_html'):
            st.markdown(st.session_state.get('saved_report_html', ''), unsafe_allow_html=True)
            
        t_date = st.session_state['target_date']
        gans_list = st.session_state['global_gans']
        jjis_list = st.session_state['global_jjis']
        m_ilgan = st.session_state['global_ds']
        m_ilji = st.session_state['global_db']
            
        def get_gan_rel_simple(g1, g2):
            if not g1 or not g2 or g1=="?" or g2=="?": return "-"
            s = {g1, g2}
            if s in [{'甲','己'}, {'乙','庚'}, {'丙','辛'}, {'丁','壬'}, {'戊','癸'}]: return "합(合)"
            if s in [{'甲','庚'}, {'乙','辛'}, {'丙','壬'}, {'丁','癸'}]: return "충(沖)"
            극_dict = {'甲':'戊', '乙':'己', '丙':'庚', '丁':'辛', '戊':'壬', '己':'癸', '庚':'甲', '辛':'乙', '壬':'丙', '癸':'丁'}
            if 극_dict.get(g1) == g2 or 극_dict.get(g2) == g1: return "극(剋)"
            return "-"
            
        def get_ji_rel_set_simple(j1, j2):
            if not j1 or not j2 or j1 == "?" or j2 == "?": return "-"
            s = {j1, j2}
            if s in [{'子','丑'}, {'寅','亥'}, {'卯','戌'}, {'辰','酉'}, {'巳','申'}, {'午','未'}]: return "육합"
            if s in [{'子','午'}, {'丑','未'}, {'寅','申'}, {'卯','酉'}, {'辰','戌'}, {'巳','亥'}]: return "충"
            if s in [{'子','未'}, {'丑','午'}, {'寅','酉'}, {'卯','申'}, {'辰','亥'}, {'巳','戌'}]: return "원진"
            if s in [{'寅','巳'}, {'巳','申'}, {'寅','申'}, {'丑','戌'}, {'戌','未'}, {'丑','未'}, {'子','卯'}]: return "형"
            return "-"

        dklc = KoreanLunarCalendar()
        dklc.setSolarDate(t_date.year, t_date.month, t_date.day)
        gj_str = dklc.getChineseGapJaString()
        
        if gj_str:
            parts = gj_str.split()
            target_year = parts[0][:2]
            target_wol = parts[1][:2]
            target_il = parts[2][:2]
            
            gan_res = []
            labels_gan = ["년간", "월간", "일간", "시간"]
            for idx, label in enumerate(labels_gan):
                rel = get_gan_rel_simple(gans_list[idx], target_il[0])
                if rel != "-":
                    gan_res.append(f"☁️ <b>{label}({gans_list[idx]})</b> → <span style='color:#1976D2; font-weight:bold;'>천간 {rel}</span>")
            gan_res_html = '<br>'.join(gan_res) if gan_res else '특이 천간 파동 없음'

            r_res = []
            labels_ji = ["년지", "월지", "일지", "시지"]
            for idx, label in enumerate(labels_ji):
                rel_full = get_ji_rel_set_simple(jjis_list[idx], target_il[1])
                if rel_full != "-":
                    r_res.append(f"🌊 <b>{label}({jjis_list[idx]})</b> → <span style='color:#D50000; font-weight:bold;'>{rel_full}</span>")

            r_res_html = '<br>'.join(r_res) if r_res else '특이 지지 파동 없음'

            iljin_prompt = f"""
당신은 정통 명리심리상담사 초연 박사입니다. 아래의 정밀 연산된 팩트를 바탕으로 오늘 하루(일진)의 흐름을 날카롭게 분석하십시오.
- 내담자 일주: {m_ilgan}{m_ilji}
- 일진 날짜: {t_date.year}년 {t_date.month}월 {t_date.day}일 ({target_year}년 {target_wol}월 {target_il}일)
- 천간 파동: {gan_res_html}
- 지지 형충파해: {r_res_html}

[출력 템플릿]
<br><b>🌅 전반부 (자시~오시):</b> (내용 상세 작성)
<br><b>🌃 후반부 (미시~야자시):</b> (내용 상세 작성)
"""
            with st.spinner("⏳ 메인 사주풀이 보존 완료! 하단에 [일진 정밀 분석] 추가 가동 중..."):
                try:
                    res = model.generate_content(iljin_prompt)
                    ai_iljin_html = res.text.strip().replace("\n", "<br>")
                except Exception as e:
                    ai_iljin_html = f"<div style='color:red;'>🚨 AI 일진 분석 장애: {e}</div>"

            html_output = (
                f"<div class='page-break-before'></div>\n"
                f"<div class='report-page'>\n"
                f"<div class='vip-inset-frame' style='border: 3px solid #1A237E;'>\n"
                f"<h1 style='text-align: center; color: #1A237E;'>🔮 일진 정밀 분석서 {APP_VERSION}</h1>\n"
                f"<div style='text-align: center; font-size: 16px; font-weight: bold; color: #555; margin-bottom: 20px;'>대상일자: {t_date}</div>\n"
                f"<div class='content-box-loose' style='font-size: 15px; line-height: 1.8;'>{ai_iljin_html}</div>\n"
                f"</div>\n"
                f"</div>"
            )
            st.session_state['saved_report_iljin'] = html_output
            st.rerun()

# ==============================================================================
# 👶 8. [독립 모듈] 출산택일 정밀 분석 (None 예외 방어 적용)
# ==============================================================================
if st.session_state.get('app_running', False) and st.session_state.get('run_delivery_only', False) and 'global_gans' in st.session_state:
    with st.spinner("⏳ [출산택일 분석실] 최적의 길일 연산 및 AI 통변 중..."):
        try:
            gans = st.session_state['global_gans']
            jjis = st.session_state['global_jjis']
            p_bazi_context = st.session_state.get('partner_bazi', ["?", "?", "?", "?"])
            
            if u_gender == "남성":
                m_jjis = jjis
                f_jjis = [b[1] if len(b)>1 else "?" for b in p_bazi_context]
            else:
                m_jjis = [b[1] if len(b)>1 else "?" for b in p_bazi_context]
                f_jjis = jjis

            s_d_val = start_date if start_date else dt_mod.date.today()
            e_d_val = end_date if end_date else dt_mod.date.today() + dt_mod.timedelta(days=30)

            FORBIDDEN_LIST = ['병오', '임자', '계해', '신유', '경신']
            delivery_days = get_optimized_delivery_days(s_d_val, e_d_val, m_jjis, f_jjis, FORBIDDEN_LIST)
            
            t_title = "💍 최고의 결혼 길일 추천 리포트" if u_product == "3-2. 결혼 택일" else "👶 새 생명 마중 출산 길일 추천"
            del_content = f"<h2 style='text-align:center; color:#4A148C;'>{t_title}</h2>\n<p style='text-align:center; font-weight:bold; color:#555;'>탐색 기간: {s_d_val} ~ {e_d_val} (태아 성별: {baby_gender})</p><hr style='border:1px dashed #4A148C; margin:15px 0;'>\n"
            for day_info in delivery_days:
                del_content += f"<div style='font-size:16px; font-weight:bold; margin-bottom:8px; padding:8px; background:#F8F9FA; border-radius:6px;'>✅ 추천 길일: <b>{day_info['date']}</b> (조화 점수: {day_info['score']}점)</div>\n"
            
            delivery_prompt = f"""
[SYSTEM ROLE: CHOYEON TRADITIONAL MASTER]
당신은 정통 명리심리상담사 '초연 박사'입니다. 부모의 사주 원국 기운을 바탕으로 탐색 기간 내에 태어날 아기에게 가장 길하고 복된 최고의 프리미엄 희망일/길일을 선정하여 전통 명리 에세이로 상세히 풀어내십시오.
- 부모 원국: 남명/여명 사주기운 ({gans} / {jjis})
- 탐색 기간: {s_d_val} ~ {e_d_val} / 태아 성별: {baby_gender}
"""
            del_res = model.generate_content(delivery_prompt)
            ai_delivery_html = del_res.text.strip().replace("\n", "<br>")
            del_content += f"<div class='content-box-loose' style='font-size:15px; line-height:1.8; margin-top:20px;'>\n{ai_delivery_html}\n</div>"

            def wrap_takil_a4(content, title_color="#4A148C", title="[ 초연 전통명리 택일 리포트 ]"):
                return f"<div class='report-page'>\n<div class='vip-inset-frame' style='border-color:{title_color}; padding:20px;'>\n<h1 style='text-align:center; color:{title_color}; font-family:\"Malgun Gothic\", sans-serif; font-weight:900; border-bottom:2px solid {title_color}; padding-bottom:15px; margin-bottom:30px;'>{title}</h1>\n{content}\n</div>\n</div>"

            st.session_state['saved_report_del'] = wrap_takil_a4(del_content, "#4A148C", f"[ 초연 전통명리 {u_product} ]")
            st.session_state['run_delivery_only'] = False
        except Exception as e:
            st.error(f"출산택일 연산 장애: {e}")
            st.session_state['run_delivery_only'] = False

# ==============================================================================
# 🍽️ 9. 화면 출력부 (통합 완결 출력)
# ==============================================================================
if st.session_state.get('app_running', False):
    
    # 1. 개인 사주 및 특성화 상품 출력
    if main_category in ["1. 개인 사주팔자 풀이 (종합)", "2. 테마별 특성화 상담"]:
        if st.session_state.get('saved_report_html'):
            st.markdown(st.session_state.get('saved_report_html', ''), unsafe_allow_html=True)
        if st.session_state.get('saved_report_iljin'):
            st.markdown(st.session_state.get('saved_report_iljin', ''), unsafe_allow_html=True)
    
    # 2. 타 감명서 대조 출력 (사주)
    elif main_category == "4. 타 감명서 비교" and u_product == "4-1. 타 감명서 비교 (사주)":
        if st.session_state.get('saved_report_html'):
            st.markdown(st.session_state.get('saved_report_html', ''), unsafe_allow_html=True)
        if st.session_state.get('saved_report_2'):
            st.markdown(st.session_state.get('saved_report_2', ''), unsafe_allow_html=True)
        
    # 3. 궁합 및 택일 / 타 감명서 대조 출력 (궁합)
    elif main_category == "3. 커플 연애/결혼운 (궁합) 풀이" or u_product == "4-2. 타 감명서 비교 (궁합)":
        if st.session_state.get('saved_report_gh_cover'):
            st.markdown(st.session_state.get('saved_report_gh_cover', ''), unsafe_allow_html=True)
            st.markdown("<div class='page-break-before'></div>", unsafe_allow_html=True)
            
        if st.session_state.get('saved_report_gh_m'):
            st.markdown(st.session_state.get('saved_report_gh_m', ''), unsafe_allow_html=True)
            st.markdown("<div class='page-break-before'></div>", unsafe_allow_html=True)

        if st.session_state.get('saved_report_gh_f'):
            st.markdown(st.session_state.get('saved_report_gh_f', ''), unsafe_allow_html=True)
            st.markdown("<div class='page-break-before'></div>", unsafe_allow_html=True)

        if st.session_state.get('saved_report_gh_g'):
            st.markdown(st.session_state.get('saved_report_gh_g', ''), unsafe_allow_html=True)

        if st.session_state.get('saved_report_del'):
            st.markdown("<div class='page-break-before'></div>", unsafe_allow_html=True)
            st.markdown(st.session_state.get('saved_report_del', ''), unsafe_allow_html=True)

        if st.session_state.get('saved_report_2'):
            st.markdown("<div class='page-break-before'></div>", unsafe_allow_html=True)
            st.markdown(st.session_state.get('saved_report_2', ''), unsafe_allow_html=True)
