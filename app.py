<h3 style='color:#1A237E; font-size: 24px; font-weight: 900;'> 🎯 초연 시공명리 특별 개운 비법</h3>
<div class='content-box-loose'>
<span class='sub-title' style='font-size: 18px; font-weight: 900; color: #111;'>◈ 수호 천사의 기운 조언:</span>
(사주원국 및 운의 흐름에 따른 천을귀인과 길신 등의 작용에 대하여 하이브리드 톤으로 상세하게 3~4문장 에세이 창작)

<span class='sub-title' style='font-size: 18px; font-weight: 900; color: #111;'>◈ 백년해로의 기운 조언:</span>
(오행의 치우침, 원진, 고란살, 고신, 과숙 등 이성 관계에 영향을 미치는 사주원국 및 운의 흐름을 분석하되, 전문 용어는 철저히 숨길 것. 오직 '부부 및 연인 관계에서 발생할 수 있는 성격적/상황적 갈등 요소'와 이를 극복하기 위한 '실질적이고 따뜻한 개운 비법'에만 100% 초점을 맞추어 카운슬러 어조로 3~4문장 창작)

<span class='sub-title' style='font-size: 18px; font-weight: 900; color: #111;'>◈ 행운에 따른 기운 조언:</span>
(운의 흐름에 따른 합형충파해와 진술축미의 입고/개고, 도화/망신/역마살 작용에 따른 역동성과 재물/대인관계 등 주의할 점을 하이브리드 톤으로 상세하게 3~4문장 에세이 창작)
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
