import streamlit as st
import google.generativeai as genai
import requests
from bs4 import BeautifulSoup

# 페이지 기본 설정
st.set_page_config(page_title="🔥 네이버 기반 헤드라인 제조기", page_icon="📝", layout="centered")

def get_naver_ranking_headlines():
    """네이버 많이 본 뉴스(랭킹 뉴스) 페이지를 실시간으로 크롤링하여 상위 헤드라인을 가져옵니다."""
    # 네이버 각 언론사별 많이 본 뉴스 링크
    url = "https://news.naver.com/main/ranking/popularDay.naver"
    
    # 크롤링 차단 방지를 위한 User-Agent 설정
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status() # 웹페이지를 정상적으로 가져왔는지 확인
        
        soup = BeautifulSoup(response.text, 'html.parser')
        headlines = []
        
        # 네이버 랭킹 뉴스 제목들 추출 (a 태그 중 class가 list_title인 것)
        titles = soup.select(".rankingnews_list .list_title")
        
        # 언론사별 1위 기사들 위주로 상위 15개를 먼저 수집
        for title in titles[:15]: 
            clean_title = title.get_text(strip=True)
            if clean_title:
                headlines.append(clean_title)
        
        # 중복 제거 후 상위 10개만 리스트로 반환
        return list(dict.fromkeys(headlines))[:10]
        
    except Exception as e:
        raise Exception(f"네이버 랭킹 뉴스 수집 실패: {e}")

def generate_headlines(api_key, article_text, trending_headlines):
    """Gemini API를 호출하여 헤드라인 트렌드를 분석하고 새 헤드라인을 생성합니다."""
    genai.configure(api_key=api_key)
    
    # 모델명으로 인한 404 Not Found 에러를 방지하기 위해 사용 가능한 모델을 순차적으로 시도합니다.
    models_to_try = ['gemini-2.5-flash', 'gemini-2.0-flash', 'gemini-1.5-flash-latest', 'gemini-pro']
    
    headlines_str = "\n".join([f"- {h}" for h in trending_headlines])
    
    prompt = f"""
최근 네이버에서 가장 인기 있는 실시간 랭킹 뉴스 헤드라인 10개입니다:
{headlines_str}

**작업 1**: 위 헤드라인들의 공통적인 특징(자극성, 문장 구조, 키워드 배치, 한국 독자의 호기심을 유발하는 요소 등)을 3가지로 분석해서 아주 짧게 핵심만 요약해주세요.

**작업 2**: 분석한 특징을 바탕으로, 아래 사용자가 제공한 [기사 본문]을 요약하여 한국 사람들의 클릭을 극대화할 수 있는 매우 매력적인 헤드라인을 5개 생성해주세요. 
헤드라인은 네이버 포털 메인에 걸릴 법하게 아주 자연스럽고 호기심을 강하게 자극해야 합니다.

[기사 본문]
{article_text}

결과는 반드시 다음 형식으로 출력해주세요:
### 📊 최근 네이버 인기 헤드라인 분석 결과
1. [특징 1]
2. [특징 2]
3. [특징 3]

### 🏆 추천 맞춤형 헤드라인 TOP 5
1. [헤드라인 1]
2. [헤드라인 2]
3. [헤드라인 3]
4. [헤드라인 4]
5. [헤드라인 5]
"""
    # 응답 생성 (여러 모델을 순차적으로 시도하여 에러 방지)
    last_error = None
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
st.title("🔥 네이버 실시간 트렌드 헤드라인 제조기")
st.markdown("네이버 **'많이 본 뉴스(랭킹 뉴스)'** 코너의 실시간 헤드라인을 분석하여, 내 기사에 알맞은 가장 네이버스러운 트렌디한 헤드라인을 뽑아줍니다.")

# 사이드바 (API 키 입력 등 설정)
with st.sidebar:
    st.header("⚙️ 환경 설정")
    api_key = st.text_input("Gemini API Key를 입력하세요", type="password", help="API 키는 저장되지 않으며 1회성으로 사용됩니다.")
    st.markdown("[Google AI Studio](https://aistudio.google.com/app/apikey)에서 무료로 발급받을 수 있습니다.")
    st.markdown("---")
    st.markdown("💡 **이용 가이드**\n1. 본문에 요약하고 싶은 기사를 넣습니다.\n2. '헤드라인 생성하기' 버튼을 누릅니다.")
    st.markdown("<small>✅ 이 앱은 실시간 네이버 랭킹 뉴스의 제목들을 자동으로 크롤링하여 분석 기반 데이터로 사용합니다.</small>", unsafe_allow_html=True)

# 메인 입력 창
article_input = st.text_area("작성하신 기사 본문이나 뼈대가 되는 핵심 내용을 입력하세요.", height=250, placeholder="대통령실은 오늘 브리핑을 통해 경제 회복 방안을...")

# 실행 버튼
if st.button("🚀 나만의 헤드라인 자동 생성하기", type="primary"):
    if not api_key:
        st.error("앗! 왼쪽 사이드바에서 Gemini API Key를 먼저 입력해주세요.")
    elif not article_input.strip():
        st.warning("기사 내용을 입력해야 헤드라인을 만들어 드릴 수 있어요!")
    else:
        with st.spinner("🔍 네이버 '많이 본 뉴스' 실시간 트렌드를 분석하고 헤드라인을 생성 중입니다..."):
            try:
                # 1. 네이버 랭킹 뉴스 수집 
                trends = get_naver_ranking_headlines()
                
                # 2. Gemini를 통한 트렌드 분석 및 결과 생성
                result = generate_headlines(api_key, article_input, trends)
                
                # 3. 결과 출력
                st.success("✨ 한국인 입맛에 딱 맞는 맞춤형 헤드라인 생성이 완료되었습니다!")
                st.markdown("---")
                st.markdown(result)
                
                with st.expander("실시간으로 스크래핑한 오늘의 네이버 랭킹 뉴스 보기"):
                    for t in trends:
                        st.write(f"- {t}")
                        
            except Exception as e:
                st.error(f"오류가 발생했습니다. API 키가 정확한지 확인해주세요.\n\n상세 오류: {e}")
