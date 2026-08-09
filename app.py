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
APP_VERSION = "Ver 49.3 (1인/2인 파이프라인 완전 분리 & 14종 핀셋 통변)"

# ==============================================================================
# 0. VIP 인셋 프레임 및 초강력 프린트 CSS (ver 48.1 스타일 100% 보존)
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
    if ji in ["?", "-", " "]: return "-"
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

class UniversalPrintableGunghap:
    def __init__(self, applicant, partner_name, male, female, daeun_score=10):
        self.app, self.p_name, self.daeun_score = applicant, partner_name, daeun_score
        self.final_score = 88
        self.grade = "천생연분 (최고의 인연)"

# ==============================================================================
# 📋 [1단계] 손님 주문 접수 (사이드바 UI 및 사주팔자 역산)
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
        u_product = st.radio("상세 분석 항목:", ["1-1. 사주팔자 및 대운 분석", "1-2. 올해 및 특정연도 운세 상세분석", "1-3. 이번달 및 특정월 운세 상세분석", "1-4. 특정 주간 및 특정일운 상세분석"], key="sub_cat_1")
    elif main_category == "2. 테마별 특성화 상담":
        u_product = st.radio("특성화 상품 선택:", ["2-1. 재물운 특화 분석", "2-2. 직업/진학운 특화 분석", "2-3. 연애/결혼운 특화 분석", "2-4. 건강운 특화 분석", "2-5. 이사 및 방위 특화 분석"], key="sub_cat_2")
    elif main_category == "3. 커플 연애/결혼운 (궁합) 풀이":
        u_product = st.radio("상세 분석 항목:", ["3-1. 연애/결혼운 (궁합) 풀이", "3-2. 결혼 택일", "3-3. 출산 택일"], key="sub_cat_3")
    else:
        u_product = st.radio("비교 분석 대상:", ["4-1. 타 감명서 비교 (사주)", "4-2. 타 감명서 비교 (궁합)"], key="sub_cat_4")

    st.markdown("---")

    # 🔍 신청인 사주팔자 역산 검색
    with st.expander("🔍 신청인 사주팔자 역산 검색", expanded=False):
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
    
    # 2인 명조 항목 스위치 판별
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

    # 🚨 2인 명조 필수 입력 구역 (궁합 / 궁합 비교)
    if is_2person_product:
        st.markdown("<hr style='border:1px dashed #C62828; margin:15px 0;'>", unsafe_allow_html=True)
        
        # 🔍 상대방 사주팔자 역산 검색
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
        p_gender = st.selectbox("성별", ["남성", "여성"], index=1, key="p_g")
        p_marital = st.selectbox("혼인여부", ["미혼", "기혼", "돌싱"], index=0, key="p_m_stat")
        p_cal = st.selectbox("달력", ["양력", "음력(평달)", "음력(윤달)"], index=0, key="p_c")
        
        p_col1, p_col2, p_col3 = st.columns(3)
        p_y = p_col1.number_input("년", 1900, 2050, value=st.session_state.get('p_y_in', 2010), key="p_y_in")
        p_m = p_col2.number_input("월", 1, 12, value=st.session_state.get('p_m_in', 1), key="p_m_in")
        p_d = p_col3.number_input("일", 1, 31, value=st.session_state.get('p_d_in', 1), key="p_d_in")
        p_t = st.selectbox("태어난 시간", idx_list, index=0, key="p_t_in")

        if u_product in ["3-2. 결혼 택일", "3-3. 출산 택일"]:
            st.markdown("<hr style='border:1px solid #ddd; margin:15px 0;'>", unsafe_allow_html=True)
            baby_gender = st.radio("태아 성별", ["미정", "남아", "여아"], index=0)
            start_date = st.date_input("탐색 시작일", value=dt_mod.date.today())
            end_date = st.date_input("탐색 종료일", value=dt_mod.date.today() + dt_mod.timedelta(days=30))
            run_delivery_calc = st.checkbox("✅ 택일 가동 확정", value=True)

    st.markdown("---")
    btn_single = st.button("🚀 초연 전통명리 사주풀이 가동", key="btn_run", use_container_width=True, type="primary")
    if st.button("🖨️ 풀이 결과 인쇄 / PDF 저장", key="btn_print", use_container_width=True, type="secondary"):
        components.html("<script>window.parent.print();</script>", height=0)

    if btn_single:
        if not u_name.strip(): st.warning("⚠️ 신청인의 이름을 입력해 주세요.")
        elif is_2person_product and not p_name.strip(): st.warning("⚠️ 상대방의 이름을 입력해 주세요.")
        else:
            st.session_state['app_running'] = True
            st.session_state['need_calc'] = True
            for key in ['saved_report_html', 'saved_report_2', 'saved_report_gh_cover', 'saved_report_gh_m', 'saved_report_gh_f', 'saved_report_gh_g', 'saved_report_del', 'saved_report_iljin']:
                if key in st.session_state: del st.session_state[key]
            st.rerun()

# ==============================================================================
# 🧠 [2단계] 순수 만세력 및 명리 팩트 연산 엔진 (1인 / 2인 구조 분리)
# ==============================================================================
if st.session_state.get('need_calc', False):
    kst = pytz.timezone('Asia/Seoul')
    curr_dt_sys = dt_mod.datetime.now(kst)
    curr_y, curr_m = curr_dt_sys.year, curr_dt_sys.month
    u_age = curr_y - u_y + 1
    base_dt = dt_mod.datetime(u_y, u_m, u_d, 12, 0)
    
    klc = KoreanLunarCalendar()
    if u_cal == "양력": klc.setSolarDate(u_y, u_m, u_d)
    elif u_cal == "음력(평달)": klc.setLunarDate(u_y, u_m, u_d, False)
    else: klc.setLunarDate(u_y, u_m, u_d, True)
    
    sol_str = f"{klc.solarYear}년 {klc.solarMonth:02d}월 {klc.solarDay:02d}일"
    lun_str = f"{klc.lunarYear}년 {klc.lunarMonth:02d}월 {klc.lunarDay:02d}일"
    
    true_ym, true_mm, _ = get_true_year_month_pillar(u_y, u_m, u_d, 12, 0)
    ys, yb = true_ym[0], true_ym[1]
    ms, mb = true_mm[0], true_mm[1]
    
    gj = klc.getChineseGapJaString().split()
    ds, db = gj[2][0], gj[2][1]
    hs, hb = get_time_ganji(ds, u_t, base_dt)
    
    gans, jjis = [hs, ds, ms, ys], [hb, db, mb, yb]
    applicant_bazi = [f"{hs}{hb}", f"{ds}{db}", f"{ms}{mb}", f"{ys}{yb}"]

    adj_mins = get_total_time_adjustment(base_dt)
    utc_dt = base_dt - dt_mod.timedelta(hours=9) + dt_mod.timedelta(minutes=adj_mins)
    order = 1 if (GAN.index(ys)%2==0) == (u_gender=='남성') else -1
    calc_d = get_daeun_su_accurate(utc_dt, order)
    current_daewun_age = ((u_age - calc_d) // 10) * 10 + calc_d

    calc_gyukgook, gyukgook_detail = get_gyukgook_detailed(ds, ys, ms, hs, mb)
    i_gong = calculate_gongmang(ds, db)

    db_header = f"[현재 시점: {curr_y}년 {curr_m}월]\n- 내담자: {u_name} ({u_age}세 / {u_gender})\n- 선택 상품: {u_product}\n- 격국 팩트: {gyukgook_detail}\n"
    common_rules = f"""
🚨 [공통 절대 준수 규칙 - 명리 용어 개념 설명 배제 & 팩트 직결 통변]
1. 🚨 [명리 용어 개념 설명 절대 금지]: 용어의 정의나 원리를 교육하지 마십시오.
2. 🚨 [현실적 팩트 직행]: 명리 팩트를 바탕으로 곧바로 현실적 결과와 처세술로 직행하십시오.
"""

    # 2인 명조 데이터 연산 (궁합 및 궁합 비교용)
    partner_bazi = []
    if is_2person_product:
        p_klc = KoreanLunarCalendar()
        if p_cal == "양력": p_klc.setSolarDate(p_y, p_m, p_d)
        elif p_cal == "음력(평달)": p_klc.setLunarDate(p_y, p_m, p_d, False)
        else: p_klc.setLunarDate(p_y, p_m, p_d, True)
        
        p_base_dt = dt_mod.datetime(p_y, p_m, p_d, 12, 0)
        p_true_ym, p_true_mm, _ = get_true_year_month_pillar(p_y, p_m, p_d, 12, 0)
        p_ys, p_yb = p_true_ym[0], p_true_ym[1]
        p_ms, p_mb = p_true_mm[0], p_true_mm[1]
        
        p_gj = p_klc.getChineseGapJaString().split()
        p_ds, p_db = p_gj[2][0], p_gj[2][1]
        p_hs, p_hb = get_time_ganji(p_ds, p_t, p_base_dt)
        partner_bazi = [f"{p_hs}{p_hb}", f"{p_ds}{p_db}", f"{p_ms}{p_mb}", f"{p_ys}{p_yb}"]

# ==============================================================================
# 🍳 [3단계] AI 프롬프트 조립 및 통변 연산 (1인/2인 완벽 구분 조리)
# ==============================================================================
if st.session_state.get('need_calc', False):
    spinner_msg = f"⏳ [초연 전통명리 정밀 분석({u_product}) 연산 중....]"
    with st.spinner(spinner_msg):
        try:
            # ------------------------------------------------------------------
            # 1. 개인 사주팔자 풀이 파이프라인 (1인 명조 전용)
            # ------------------------------------------------------------------
            if main_category in ["1. 개인 사주팔자 풀이 (종합)", "2. 테마별 특성화 상담"] or u_product == "4-1. 타 감명서 비교 (사주)":
                prompt = f"""
{db_header}
{common_rules}

[상세 핀셋 분석 항목: {u_product}]
- 용어 개념 해설 없이 사주원국, 격국({calc_gyukgook}), 십성, 12운성, 신살, 대운/세운/월운의 현실적 팩트와 결과만 정밀 통변하십시오.

<h3 style='color:#1A237E; font-size: 24px; font-weight: 900;'>🎯 [{u_product}] 정밀 감명 리포트</h3>
<div class='content-box-loose'>
1) 성격 및 내면 속마음 팩트 분석
2) 사주원국 구조 및 오행/격국 품격 분석
3) 선택 상품({u_product})에 특화된 현실적 득실 및 운의 변곡점 핀셋 통변
4) 개운 색상, 자산 관리, 직업 처세 지혜 지침
</div>
"""
                res = model.generate_content(prompt)
                ai_text = "\n".join([line.lstrip() for line in res.text.split("\n")])
                
                cover_html = f"<div class='report-page cover-page'><div style='border:4px solid #1A237E; padding:50px; text-align:center;'><h1>초연 전통 명리 사주풀이</h1><h3>[{u_product}]</h3><p>신청인: {u_name} 님 ({sol_str})</p></div></div>"
                st.session_state['saved_report_cover'] = cover_html

                if u_product == "4-1. 타 감명서 비교 (사주)":
                    st.session_state['saved_report_2'] = f"<div class='report-page'><div class='vip-inset-frame'><h2>⚖️ 타 감명서 학술 검증 (사주)</h2><div>{ai_text}</div></div></div>"
                else:
                    st.session_state['saved_report_html'] = f"{cover_html}<div class='report-page'><div class='vip-inset-frame'><h2>📜 [{u_product}] 정밀 분석</h2><div>{ai_text}</div></div></div>"

            # ------------------------------------------------------------------
            # 2. 커플 궁합 및 택일 파이프라인 (2인 명조 완전 독립 연산/서빙)
            # ------------------------------------------------------------------
            elif main_category == "3. 커플 연애/결혼운 (궁합) 풀이" or u_product == "4-2. 타 감명서 비교 (궁합)":
                male_data_pack = applicant_bazi if u_gender == "남성" else partner_bazi
                female_data_pack = partner_bazi if u_gender == "남성" else applicant_bazi

                gh_engine = UniversalPrintableGunghap(u_name, p_name, male_data_pack, female_data_pack, 10)
                gh_engine.run_universal_logic()

                essay_prompt = f"""
{db_header}
{common_rules}

🚨 [궁합 및 2인 명조 정밀 분석 규칙]:
- 신청인({u_name})과 상대방({p_name}) 두 사람의 명조를 기반으로 용어 해설을 철저히 배제하고 궁합 점수({gh_engine.final_score}점), 성격 차이, 애정 파동, 현실적 조율 지혜를 통변하십시오.
[선택 상품: {u_product}]
"""
                res_gh = call_claude_api(essay_prompt)

                cover_gh_html = f"<div class='report-page cover-page'><div style='border:4px solid #1B5E20; padding:50px; text-align:center;'><h1>초연 전통 명리 궁합 풀이</h1><h3>[{u_product}]</h3><p>♂️ {u_name if u_gender=='남성' else p_name} 님 ♡ ♀️ {p_name if u_gender=='남성' else u_name} 님</p></div></div>"
                st.session_state['saved_report_gh_cover'] = cover_gh_html

                # 2인 독립 서빙 구역
                st.session_state['saved_report_gh_m'] = f"<div class='report-page'><div class='vip-inset-frame' style='border-color:#1A237E;'><h2>♂️ 남명 사주원국 및 핵심 요약</h2><p>{u_name if u_gender=='남성' else p_name} 님의 타고난 사주팔자 기본 팩트입니다.</p></div></div>"
                st.session_state['saved_report_gh_f'] = f"<div class='report-page'><div class='vip-inset-frame' style='border-color:#D50000;'><h2>♀️ 여명 사주원국 및 핵심 요약</h2><p>{p_name if u_gender=='남성' else u_name} 님의 타고난 사주팔자 기본 팩트입니다.</p></div></div>"
                st.session_state['saved_report_gh_g'] = f"<div class='report-page'><div class='vip-inset-frame' style='border-color:#1B5E20;'><h2>📊 [{u_product}] 종합 궁합 점수: {gh_engine.final_score}점 ({gh_engine.grade})</h2><div>{res_gh}</div></div></div>"

                if u_product in ["3-2. 결혼 택일", "3-3. 출산 택일"]:
                    delivery_days = get_optimized_delivery_days(start_date, end_date, [], [], ['병오'])
                    del_content = f"<h2>👶 [{u_product}] 추천 길일 리포트</h2>"
                    for d_info in delivery_days:
                        del_content += f"<div>✅ {d_info['date']} (조화 점수: {d_info['score']}점)</div>"
                    st.session_state['saved_report_del'] = f"<div class='report-page'><div class='vip-inset-frame'>{del_content}</div></div>"

            st.session_state['need_calc'] = False

        except Exception as e:
            st.error(f"시스템 연산 중 오류 발생: {e}")
            st.session_state['need_calc'] = False

# ==============================================================================
# 🍽️ [4단계] 통합 서빙 및 최종 출력 (1인 / 2인 구조에 맞춰 분기 출력)
# ==============================================================================
if st.session_state.get('app_running', False):
    
    # 1. 1인 명조 상품 서빙 (개인사주, 특성화, 타감명서 사주)
    if main_category in ["1. 개인 사주팔자 풀이 (종합)", "2. 테마별 특성화 상담"] or u_product == "4-1. 타 감명서 비교 (사주)":
        if st.session_state.get('saved_report_html'):
            st.markdown(st.session_state.get('saved_report_html', ''), unsafe_allow_html=True)
        if st.session_state.get('saved_report_2'):
            st.markdown(st.session_state.get('saved_report_2', ''), unsafe_allow_html=True)
        if st.session_state.get('saved_report_iljin'):
            st.markdown(st.session_state.get('saved_report_iljin', ''), unsafe_allow_html=True)
        
    # 2. 2인 명조 상품 서빙 (궁합, 결혼/출산택일, 타감명서 궁합)
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
