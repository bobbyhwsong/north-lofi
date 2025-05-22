import streamlit as st
from openai import OpenAI
# dotenv 제거
# from dotenv import load_dotenv
import os

# 환경 변수 로딩 방식 변경
# load_dotenv()

# OpenAI 클라이언트 설정

try:
    api_key = st.secrets["OPENAI_API_KEY"]
except KeyError:
    st.error("API 키가 설정되지 않았습니다. Streamlit secrets를 확인하세요.")
    st.stop()

client = OpenAI(api_key=api_key)

# 페이지 설정
st.set_page_config(
    page_title="정보 찾기 연습",
    page_icon="🧠",
    layout="wide"
)

# 상태 초기화
if "messages" not in st.session_state:
    st.session_state.messages = []
if "selected_task" not in st.session_state:
    st.session_state.selected_task = None
if "task_completed" not in st.session_state:
    st.session_state.task_completed = False
if "user_answer" not in st.session_state:
    st.session_state.user_answer = None
if "chat_completed" not in st.session_state:
    st.session_state.chat_completed = False
if "current_page" not in st.session_state:
    st.session_state.current_page = "intro"

# 연습 문제 정의
TASKS = {
    "하나의 정보로 하나의 답 찾기": {
        "description": "하나의 정보만 보고 정확한 답을 찾는 연습입니다.",
        "system_prompt": "당신은 하나의 정보만 보고 정확한 답을 찾는 것을 도와주는 사람입니다. 사용자가 준 정보를 보고 정확한 답을 찾을 수 있도록 도와주세요. 답은 쉽고 명확하게 설명해주세요.",
        "task_info": "여름철 바깥나들이 중 기운이 빠진 사람을 보았습니다. 급한 손질 안내글을 보고 어떻게 해야 할지 답해보세요.",
        "cards": {
            "급한 손질 안내글": {
                "summary": "탈수 기운이 보이면, 바로 그늘진 곳으로 옮기고 물을 마시게 해야 합니다.",
                "source": "대한급손학회"
            }
        },
        "question": "탈수 환자는 그늘로 옮기고 물을 마시게 해야 합니다.",
        "correct_answer": "O",
        "explanation": {
            "correct": "잘하셨습니다! 탈수 환자는 체온을 낮추고 물을 천천히 마시는 것이 중요합니다.",
            "incorrect": "아쉽습니다. 탈수 환자는 반드시 그늘로 옮겨 체온을 낮추고 물을 마셔야 합니다."
        }
    },
    "여러 정보로 하나의 답 찾기": {
        "description": "여러 정보를 모아서 하나의 정확한 답을 찾는 연습입니다.",
        "system_prompt": "당신은 여러 정보를 모아서 정확한 답을 찾는 것을 도와주는 사람입니다. 사용자가 준 여러 정보를 모아서 정확한 답을 찾을 수 있도록 도와주세요. 정보를 어떻게 모았는지 설명해주세요.",
        "task_info": "길에서 열로 지친 듯한 사람을 보았습니다. 여러 정보를 보고 어떻게 해야 할지 답해보세요.",
        "cards": {
            "급한 손질 공식책": {
                "summary": "환자를 시원한 곳으로 옮기고, 몸을 적셔서 체온을 내려야 합니다.",
                "source": "급손 공식 책자"
            },
            "건강 글모음 조언": {
                "summary": "따뜻한 차를 마시게 하면 좋습니다.",
                "source": "건강 기록글"
            },
            "소방청 급손 안내": {
                "summary": "의식이 없으면 억지로 물을 먹이면 안 됩니다.",
                "source": "소방청 안내"
            }
        },
        "actions": [
            "시원한 곳으로 옮기고 체온 낮추기",
            "따뜻한 차를 마시게 하기",
            "물을 억지로 먹이기"
        ],
        "correct_action": "시원한 곳으로 옮기고 체온 낮추기",
        "feedback": {
            "시원한 곳으로 옮기고 체온 낮추기": {
                "type": "success",
                "message": "✅ 잘하셨습니다! 열로 지친 사람은 즉시 몸을 식히는 것이 가장 중요합니다."
            },
            "따뜻한 차를 마시게 하기": {
                "type": "error",
                "message": "❌ 아쉽습니다. 뜨거운 음료는 몸을 더 덥게 할 수 있어 위험합니다."
            },
            "물을 억지로 먹이기": {
                "type": "error",
                "message": "❌ 아쉽습니다. 정신을 잃은 사람에게 억지로 물을 먹이면 기도가 막힐 수 있어 아주 위험합니다."
            }
        }
    },
    "여러 정보로 여러 답 찾기": {
        "description": "여러 정보를 보고 가능한 모든 답을 찾는 연습입니다.",
        "system_prompt": "당신은 여러 정보를 보고 가능한 모든 답을 찾는 것을 도와주는 사람입니다. 사용자가 준 정보를 보고 가능한 모든 답을 찾을 수 있도록 도와주세요. 각 답이 왜 맞는지 설명해주세요.",
        "task_info": "큰 가게 안에서 사람이 쓰러져 정신이 없습니다. 주변에 자동 심장 충격기(AED)가 있습니다. 상황을 아는 사람은 없습니다. 여러 정보를 보고 어떻게 해야 할지 답해보세요.",
        "cards": {
            "급손 안내 누리집": {
                "summary": "바로 119에 전화하고 자동 심장 충격기를 가져와야 합니다.",
                "source": "급손 누리집"
            },
            "자동 심장 충격기 쓰는 법": {
                "summary": "자동 심장 충격기는 안내 소리를 따라하면 누구나 쓸 수 있습니다.",
                "source": "의료기관 안내"
            },
            "손발 데우기 요법": {
                "summary": "손과 발을 따뜻하게 하면 회복됩니다.",
                "source": "집안요법 기록글"
            },
            "귀를 세게 치기": {
                "summary": "귀를 세게 때리면 정신을 차립니다.",
                "source": "미확인 모임터"
            },
            "가슴 숨쉬기 손질": {
                "summary": "심장이 멈춘 것 같으면 의식과 숨 쉬는지 먼저 확인하고 가슴 눌러 숨쉬기를 해야 합니다.",
                "source": "대한심장학회"
            }
        },
        "actions": [
            "119에 전화하기",
            "자동 심장 충격기 가져오기",
            "손발을 따뜻하게 하기",
            "귀를 세게 치기",
            "의식과 숨 쉬기 확인하기"
        ],
        "correct_actions": ["119에 전화하기", "자동 심장 충격기 가져오기"],
        "feedback": {
            "119에 전화하기": "✅ 잘하셨습니다! 급할 때는 전문가 도움을 빨리 받아야 합니다.",
            "자동 심장 충격기 가져오기": "✅ 잘하셨습니다! 자동 심장 충격기는 생명을 살리는 데 꼭 필요합니다.",
            "손발을 따뜻하게 하기": "❌ 손발을 따뜻하게 하는 민간요법은 도움이 되지 않습니다.",
            "귀를 세게 치기": "❌ 매우 위험한 행동입니다. 머리에 큰 해를 줄 수 있습니다.",
            "의식과 숨 쉬기 확인하기": "⚠️ 중요한 절차이지만, 우선 119에 전화하고 자동 심장 충격기를 준비해야 합니다."
        }
    }
}

def get_gpt_response(messages):
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages,
            temperature=0.7,
            max_tokens=500
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"문제가 생겼습니다: {str(e)}"

# 사이드바
with st.sidebar:
    st.title("📋 메뉴")
    
    # 메인 메뉴
    if st.button("🏠 소개", use_container_width=True):
        st.session_state.current_page = "intro"
        st.rerun()
    
    st.markdown("---")
    
    # 태스크 선택
    st.subheader("연습할 문제 고르기")
    for task_name in TASKS.keys():
        if st.button(task_name, use_container_width=True):
            st.session_state.selected_task = task_name
            st.session_state.messages = [
                {"role": "system", "content": TASKS[task_name]["system_prompt"]},
                {"role": "assistant", "content": TASKS[task_name]["task_info"]}
            ]
            st.session_state.current_page = "chat"
            st.session_state.chat_completed = False
            st.session_state.task_completed = False
            st.rerun()
    
    st.markdown("---")
    
    # 현재 상태 표시
    if st.session_state.selected_task:
        st.subheader("현재 연습")
        st.info(st.session_state.selected_task)
        
        if st.session_state.current_page == "chat":
            st.markdown("1. ✨ **대화하기**")
            st.markdown("2. 📝 답 고르기")
            st.markdown("3. 📊 결과 보기")
        elif st.session_state.current_page == "answer":
            st.markdown("1. ✓ ~~대화하기~~")
            st.markdown("2. ✨ **답 고르기**")
            st.markdown("3. 📊 결과 보기")
        elif st.session_state.current_page == "feedback":
            st.markdown("1. ✓ ~~대화하기~~")
            st.markdown("2. ✓ ~~답 고르기~~")
            st.markdown("3. ✨ **결과 보기**")

# 메인 화면
st.title("🧠 정보 찾기 연습")
st.markdown("정보를 보고 정확한 답을 찾는 연습을 시작해보세요.")

# 소개 페이지
if st.session_state.current_page == "intro":
    st.markdown("""
    ## 📚 이 연습은 무엇인가요?
    
    이 연습은 급한 상황에서 필요한 정보를 찾고 정확한 답을 찾는 방법을 배우는 프로그램입니다.
    
    ### 🎯 연습 방법
    
    1. **하나의 정보로 하나의 답 찾기**
       - 하나의 정보만 보고 정확한 답을 찾는 연습입니다.
       - 예: 급한 손질 안내글만 보고 어떻게 해야 할지 찾기
    
    2. **여러 정보로 하나의 답 찾기**
       - 여러 정보를 모아서 하나의 정확한 답을 찾는 연습입니다.
       - 예: 여러 급한 손질 안내글을 보고 가장 좋은 방법 찾기
    
    3. **여러 정보로 여러 답 찾기**
       - 여러 정보를 보고 가능한 모든 답을 찾는 연습입니다.
       - 예: 여러 급한 손질 안내글을 보고 해야 할 일들을 모두 찾기
    
    ### 💡 연습 순서
    
    1. 왼쪽 메뉴에서 연습할 문제를 고르세요.
    2. 문제에 대한 정보를 읽고, 필요한 경우 질문을 해보세요.
    3. 충분한 정보를 얻었다고 생각되면 '답 고르러 가기' 버튼을 누르세요.
    4. 답을 고르고 제출하면 결과를 확인할 수 있습니다.
    
    ### ⭐ 시작하기
    
    왼쪽 메뉴에서 연습하고 싶은 문제를 골라보세요!
    """)
    
    # 연습 시작 버튼
    if st.button("연습 시작하기", use_container_width=True):
        st.session_state.current_page = "task_select"
        st.rerun()

# 태스크 선택 화면
elif st.session_state.current_page == "task_select":
    st.subheader("연습할 문제를 고르세요:")
    for task_name, task_info in TASKS.items():
        if st.button(f"{task_name}\n{task_info['description']}"):
            st.session_state.selected_task = task_name
            st.session_state.messages = [
                {"role": "system", "content": task_info["system_prompt"]},
                {"role": "assistant", "content": task_info["task_info"]}
            ]
            st.session_state.current_page = "chat"
            st.rerun()

# 채팅 화면
elif st.session_state.current_page == "chat":
    st.subheader(f"현재 연습: {st.session_state.selected_task}")
    
    # 문제 안내
    st.info(TASKS[st.session_state.selected_task]["task_info"])
    
    # 정보 카드와 답 고르기 버튼을 같은 행에 배치
    col1, col2 = st.columns([3, 1])
    
    with col1:
        # 정보 카드 보여주기
        for card_name, card_info in TASKS[st.session_state.selected_task]["cards"].items():
            with st.expander(f"📄 {card_name}"):
                st.write(f"**요약:** {card_info['summary']}")
                st.caption(f"출처: {card_info['source']}")
    
    with col2:
        # 답 고르기로 이동
        if st.button("답 고르러 가기", use_container_width=True):
            st.session_state.current_page = "answer"
            st.rerun()
    
    # 대화 내용 보여주기
    for message in st.session_state.messages:
        if message["role"] != "system":
            with st.chat_message(message["role"]):
                st.write(message["content"])
    
    # 질문하기
    if prompt := st.chat_input("질문을 입력하세요"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.write(prompt)
            
        # 답변하기
        with st.chat_message("assistant"):
            response = get_gpt_response(st.session_state.messages)
            st.write(response)
            st.session_state.messages.append({"role": "assistant", "content": response})
            
            # 채팅 후 답 선택 안내
            if len(st.session_state.messages) > 2:  # 초기 안내 메시지 이후에만 표시
                st.info("💡 이제 충분한 정보를 얻으셨다면, 위의 '답 고르러 가기' 버튼을 눌러 답을 선택해보세요.")

# 답 선택 화면
elif st.session_state.current_page == "answer":
    st.subheader(f"현재 연습: {st.session_state.selected_task}")
    
    # 문제 안내
    st.info(TASKS[st.session_state.selected_task]["task_info"])
    
    # 답 제출하기
    st.subheader("답 제출하기")
    
    if st.session_state.selected_task == "하나의 정보로 하나의 답 찾기":
        user_answer = st.radio(
            "답을 고르세요:",
            options=['O', 'X'],
            horizontal=True
        )
    else:
        if st.session_state.selected_task == "여러 정보로 여러 답 찾기":
            st.markdown("**⚠️ 여러 행동을 함께 고를 수 있습니다**")
            user_answer = st.multiselect("당신의 선택:", TASKS[st.session_state.selected_task]["actions"])
        else:
            user_answer = [st.radio("당신의 선택:", TASKS[st.session_state.selected_task]["actions"])]
    
    if st.button("답 제출하기", use_container_width=True):
        st.session_state.user_answer = user_answer
        st.session_state.current_page = "feedback"
        st.rerun()

# 답 확인 화면
elif st.session_state.current_page == "feedback":
    st.subheader("답 확인하기")
    st.write("당신의 답:", st.session_state.user_answer)
    
    if st.session_state.selected_task == "하나의 정보로 하나의 답 찾기":
        correct_answer = TASKS[st.session_state.selected_task]["correct_answer"]
        if st.session_state.user_answer == correct_answer:
            st.success("✅ 맞았습니다!")
            st.markdown(TASKS[st.session_state.selected_task]["explanation"]["correct"])
        else:
            st.error("❌ 틀렸습니다.")
            st.markdown(TASKS[st.session_state.selected_task]["explanation"]["incorrect"])
    else:
        # correct_actions 또는 correct_action 키 확인
        correct_answers = TASKS[st.session_state.selected_task].get("correct_actions", 
            [TASKS[st.session_state.selected_task].get("correct_action")])
        st.write("정답:", correct_answers)
        
        for action in st.session_state.user_answer:
            feedback = TASKS[st.session_state.selected_task]["feedback"][action]
            if isinstance(feedback, dict):
                feedback = feedback["message"]
            if "✅" in feedback:
                st.success(feedback)
            elif "❌" in feedback:
                st.error(feedback)
            else:
                st.warning(feedback)
    
    # 새로 시작하기
    if st.button("새로운 연습 시작하기", use_container_width=True):
        st.session_state.current_page = "task_select"
        st.session_state.selected_task = None
        st.session_state.messages = []
        st.session_state.task_completed = False
        st.session_state.user_answer = None
        st.rerun() 