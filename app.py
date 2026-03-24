import streamlit as st
import google.generativeai as genai

# 페이지 기본 설정
st.set_page_config(page_title="📰 지면 최적화 헤드라인 제조기", page_icon="🗞️", layout="centered")

def generate_print_headlines(api_key, article_text):
    """Gemini API를 호출하여 지면 편집 문법에 맞는 헤드라인을 생성합니다."""
    genai.configure(api_key=api_key)
    
    # 모델명으로 인한 404 Not Found 에러를 방지하기 위해 사용 가능한 모델을 순차적으로 시도합니다.
    models_to_try = [
        'gemini-2.5-pro', 'gemini-2.5-flash', 
        'gemini-2.0-flash', 'gemini-1.5-pro-latest', 
        'gemini-1.5-flash-latest', 'gemini-pro'
    ]
    model = None
    last_error = None
    
    # 강력한 Few-Shot 프롬프팅 적용 (지면 편집기자 페르소나 및 모범 예시 하드코딩)
    prompt = f"""
당신은 30년 경력의 베테랑 종합일간지(예: 강원일보) 지면 편집기자입니다.
지면(종이신문)의 한정된 공간에 맞게 기사의 핵심을 가장 압축적이고 힘 있게 전달하는 완벽한 헤드라인 세트(주제목+부제목)를 뽑아내야 합니다.

[완벽한 지면 헤드라인 작성 5원칙]
1. 조사 생략 및 단어 압축: 불필요한 서술어나 조사('은/는/이/가/을/를')는 과감히 생략하고 명사나 비유적 한자어(예: 이중고, 역대 최저, 발목 등)로 뜻을 강하게 압축하세요.
2. 평서문 지양, 명사형 종결: 문장형 느낌을 최대한 빼고 임팩트 있게 명사형으로 끝맺으세요. (예: ~상승, ~인기, ~하락 등)
3. 제목의 계층화: 15자 내외의 눈길을 확 끄는 '큰 주제목'과, 20자 내외로 상황을 육하원칙 베이스로 설명하는 '작은 부제목'을 반드시 1:1 세트로 구성하세요.
4. 특수기호의 세련된 활용: 여운이나 원인/결과를 이을 때는 줄임표(…), 직접 인용이나 핵심 키워드 강조에는 작은따옴표(' '), 대등한 단어 병렬에는 가운데점(·)을 쓰세요.
5. 클릭베이트(웹 어그로) 절대 금지: 포털용 낚시성 네티즌 유도 제목이 아닌, 팩트를 온전히 전달하면서도 활자의 안정감과 기사의 무게감을 주는 전통 지면 편집 문법을 따르세요.

[모범 지면 헤드라인 데스크 픽 예시 (이 규격과 톤앤매너를 완벽히 모방할 것!)]
- 예시 1
  * 주제목: 중동사태에 수출 발목… 물류·원자재 '이중고'
  * 부제목: 호르무즈 해협 봉쇄로 운송 한달째 지연
- 예시 2  
  * 주제목: 어류 양식 생산 '역대 최저'
  * 부제목: 수온 오르며 생선값도 동반 상승
- 예시 3
  * 주제목: '식당 대신 편의점 김밥 한 줄'
  * 부제목: 고물가에 편의점 간편식 판매 인기
- 예시 4
  * 주제목: 교육도시 130년 발자취 따라 그날의 교실로
  * 부제목: 춘천 근대 교육 130년 희귀 사진 국내 첫 공개

자, 이제 막 취재기자가 쓴 조금 길고 다듬어지지 않은 투박한 송고용 [기사 본문] 원고가 도착했습니다.
이 본문을 꼼꼼히 읽고, 위 5원칙과 4가지 예시들을 완벽히 적용하여 데스크 국장의 컨펌을 한 번에 통과할 '최상급 지면 헤드라인 세트(주제목+부제목)'를 5개 후보안으로 뽑아주세요. 

[기사 본문]
{article_text}

결과는 반드시 덧붙이는 말 없이 딱 아래 형식으로만 깔끔하게 출력해주세요:
### 📰 데스크 추천 지면 헤드라인 TOP 5

**[1안]**
- 📌 주제목: (15자 내외)
- 📝 부제목: (20자 내외)

**[2안]**
- 📌 주제목: 
- 📝 부제목: 

**[3안]**
- 📌 주제목: 
- 📝 부제목: 

**[4안]**
- 📌 주제목: 
- 📝 부제목: 

**[5안]**
- 📌 주제목: 
- 📝 부제목: 
"""
    
    for model_name in models_to_try:
        try:
            model = genai.GenerativeModel(model_name)
            response = model.generate_content(prompt)
            return response.text
        except Exception as e:
            last_error = e
            continue
            
    raise Exception(f"사용 가능한 Gemini 모델을 찾지 못했습니다. 오류: {last_error}")

# --- UI 화면 구성 ---
st.title("📰 베테랑 지면 헤드라인 제조기")
st.markdown("강원일보 등 전통 종합일간지의 **편집기자 문법(조사 생략, 한자어 압축, 주제목+부제목 계층화)**을 완벽히 재현하여 팩트 기반의 묵직한 지면용 타이틀 세트를 뽑아줍니다.")

# 사이드바 (API 키 입력 등 설정)
with st.sidebar:
    st.header("⚙️ 환경 설정")
    api_key = st.text_input("Gemini API Key를 입력하세요", type="password", help="API 키는 별도 저장되지 않으며 1회성으로 사용됩니다.")
    st.markdown("[Google AI Studio](https://aistudio.google.com/app/apikey)에서 무료로 발급받을 수 있습니다.")
    st.markdown("---")
    st.markdown("💡 **지면 헤드라인 5대 원칙**\n1. 조사 생략 및 단어 압축\n2. 안정감 있는 명사형 종결\n3. '주제목 + 부제목' 세트 구성\n4. 특수기호(… ' ' ·) 의도적 활용\n5. 포털용 낚시성 제목 지양")
    st.markdown("<br><small>✅ 이 앱은 실시간 크롤링 없이, 자체 내장된 최고 수준의 **지면 데스크급 모범 예시(Few-Shot Prompt)**를 기반으로 빠르고 정확하게 편집 문법을 재현합니다.</small>", unsafe_allow_html=True)

# 메인 입력 창
article_input = st.text_area("취재기자가 송고한 기사 본문 원고를 그대로 복사해서 붙여넣으세요.", height=280, placeholder="춘천시는 오늘 바이오 산업 집중 육성을 위해 300억 원 규모의 대규모 민관 합동 투자 계획을 공식 발표했다. 이번 핵심 전략은...")

# 실행 버튼
if st.button("🚀 지면용 헤드라인 세트 추출하기", type="primary"):
    if not api_key:
        st.error("앗! 왼쪽 사이드바에서 Gemini API Key를 먼저 입력해주세요.")
    elif not article_input.strip():
        st.warning("기사 본문 원고를 입력해야 지면 편집이 가능합니다!")
    else:
        with st.spinner("🗞️ 30년 차 편집 데스크 AI가 기사를 분석하고 최적의 지면 제목을 짜는 중입니다..."):
            try:
                # Gemini를 통한 지면 프롬프트 분석 및 결과 생성
                result = generate_print_headlines(api_key, article_input)
                
                # 결과 출력
                st.success("✨ 데스크 편집 완료! 바로 지면에 올릴 수 있는 헤드라인 문구가 준비되었습니다.")
                st.markdown("---")
                st.markdown(result)
                        
            except Exception as e:
                st.error(f"오류가 발생했습니다. API 키가 정확한지 확인해주세요.\n\n상세 오류: {e}")
