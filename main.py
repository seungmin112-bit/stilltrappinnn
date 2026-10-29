
import json
import random
import html
from pathlib import Path
from datetime import date

import streamlit as st
import streamlit.components.v1 as components

# ==================================
# 1. 기본 설정
# ==================================

st.set_page_config(
    page_title="몽글이 키우기",
    page_icon="🐣",
    layout="centered"
)

FILE = Path("pet_data.json")
EXP_PER_LEVEL = 50

ACTIVITIES = {
    "💧 물 마시기": 5,
    "📚 독서하기": 10,
    "🏃 운동하기": 15,
    "🌙 제시간에 자기": 15,
    "🧹 주변 정리하기": 10,
}

DEFAULT = {
    "name": "몽글이",
    "exp": 0,
    "love": 0,
    "hunger": 70,
    "energy": 80,
    "last_day": date.today().isoformat(),
    "records": {},
    "decorations": [],
    "message": "안녕! 나랑 같이 놀자! 💗",
}


def load_data():
    if not FILE.exists():
        return DEFAULT.copy()

    try:
        with FILE.open("r", encoding="utf-8") as f:
            saved = json.load(f)

        data = DEFAULT.copy()
        data.update(saved)

        if (
            not isinstance(data["name"], str)
            or not isinstance(data["exp"], int)
            or isinstance(data["exp"], bool)
            or data["exp"] < 0
            or not isinstance(data["love"], int)
            or isinstance(data["love"], bool)
            or data["love"] < 0
            or not isinstance(data["records"], dict)
            or not isinstance(data["decorations"], list)
        ):
            return DEFAULT.copy()

        data["hunger"] = max(0, min(100, int(data["hunger"])))
        data["energy"] = max(0, min(100, int(data["energy"])))
        return data

    except (OSError, ValueError, TypeError, KeyError):
        return DEFAULT.copy()


def save_data():
    try:
        with FILE.open("w", encoding="utf-8") as f:
            json.dump(
                st.session_state.pet,
                f,
                ensure_ascii=False,
                indent=2
            )
        return True
    except OSError:
        st.error("저장에 실패했어. 파일 권한을 확인해 줘!")
        return False


if "pet" not in st.session_state:
    st.session_state.pet = load_data()

pet = st.session_state.pet

# 날짜가 바뀌면 오늘의 기록을 새로 시작
today = date.today().isoformat()
if pet["last_day"] != today:
    pet["last_day"] = today
    pet["message"] = "새로운 하루다! 오늘도 같이 힘내자! ☀️"
    save_data()


# ==================================
# 2. 펫 상태 계산
# ==================================

def get_level(exp):
    return exp // EXP_PER_LEVEL + 1


def get_stage(level):
    if level == 1:
        return "알", "🥚"
    elif level <= 3:
        return "아기 병아리", "🐣"
    elif level <= 5:
        return "꼬마 새", "🐥"
    elif level <= 8:
        return "행복한 새", "🐤"
    return "전설의 새", "🦜"


def get_mood():
    if pet["hunger"] < 20:
        return "배고파요...", "🥺"
    if pet["energy"] < 20:
        return "졸려요...", "😪"
    if pet["love"] >= 100:
        return "세상에서 네가 제일 좋아!", "🥰"
    if pet["hunger"] >= 60 and pet["energy"] >= 50:
        return "오늘 완전 행복해!", "😆"
    return "너랑 있어서 좋아!", "😊"


def get_today_records():
    records = pet["records"].get(today, [])
    return records if isinstance(records, list) else []


# ==================================
# 3. 행동 처리
# ==================================

def do_action(action):
    old_level = get_level(pet["exp"])

    if action == "feed":
        if pet["hunger"] >= 100:
            pet["message"] = "배가 빵빵해! 조금 쉬었다 먹을래 🍓"
        else:
            pet["hunger"] = min(100, pet["hunger"] + 25)
            pet["love"] += 3
            pet["message"] = random.choice([
                "냠냠! 정말 맛있어! 🍓",
                "간식이다! 사랑해! 💕",
                "꼬르륵 해결! 최고야! 🍎",
            ])

    elif action == "pet":
        pet["love"] += 5
        pet["message"] = random.choice([
            "쓰담쓰담 너무 좋아! 💗",
            "간질간질! 꺄르르! ✨",
            "너의 손길은 최고야! 🥰",
        ])

    elif action == "play":
        if pet["energy"] < 15:
            pet["message"] = "조금 졸려... 쉬고 나서 놀자 😴"
        else:
            pet["energy"] = max(0, pet["energy"] - 15)
            pet["hunger"] = max(0, pet["hunger"] - 5)
            pet["love"] += 8
            pet["exp"] += 5
            pet["message"] = random.choice([
                "우다다다! 잡아 봐! 🎾",
                "너랑 노는 게 제일 좋아! 💖",
                "점프! 빙글! 너무 재밌어! 🎉",
            ])

    elif action == "sleep":
        pet["energy"] = 100
        pet["message"] = "쿨쿨... 푹 자고 에너지 충전 완료! 🌙"

    new_level = get_level(pet["exp"])

    if new_level > old_level:
        pet["message"] = f"✨ 진화 성공! 이제 레벨 {new_level}이야!"
        st.balloons()

    pet["love"] = min(9999, pet["love"])
    pet["exp"] = min(999999, pet["exp"])
    save_data()


# ==================================
# 4. 화면 디자인 및 애니메이션
# ==================================

st.markdown("""
<style>
.stApp {
    background: linear-gradient(180deg, #fff5fb 0%, #f1f7ff 100%);
}
h1, h2, h3 {
    color: #735a92;
}
.pet-room {
    background: linear-gradient(180deg, #fffaff, #e9f8ff);
    border: 3px solid #f2d8f2;
    border-radius: 28px;
    padding: 22px 12px 18px;
    text-align: center;
    box-shadow: 0 8px 24px #d9c7ed55;
}
.pet {
    font-size: 100px;
    display: inline-block;
    animation: bounce 1.2s ease-in-out infinite;
    transform-origin: bottom center;
}
@keyframes bounce {
    0%, 100% { transform: translateY(0) rotate(-3deg); }
    50% { transform: translateY(-20px) rotate(3deg); }
}
.heart {
    display: inline-block;
    font-size: 25px;
    animation: floatheart 1.8s ease-in-out infinite;
}
@keyframes floatheart {
    0%, 100% { transform: translateY(5px); opacity: .5; }
    50% { transform: translateY(-12px); opacity: 1; }
}
.room-deco {
    font-size: 28px;
    margin: 8px;
}
div.stButton > button {
    border-radius: 16px;
    border: 1px solid #ecd8f5;
    background: #fff;
    color: #745b91;
    min-height: 48px;
    font-weight: 600;
}
div.stButton > button:hover {
    background: #ffe8f5;
    border-color: #e9b7d8;
    color: #745b91;
}
</style>
""", unsafe_allow_html=True)


# ==================================
# 5. 게임 화면
# ==================================

st.title("🌷 몽글이의 작은 세상")
st.caption("매일의 작은 습관으로 나만의 펫을 키워 봐!")

with st.expander("✏️ 펫 이름 바꾸기"):
    new_name = st.text_input("새로운 이름", value=pet["name"], max_chars=20)
    if st.button("이름 변경"):
        new_name = new_name.strip()
        if new_name:
            pet["name"] = new_name
            pet["message"] = f"이제 내 이름은 {new_name}! 💕"
            save_data()
            st.rerun()
        else:
            st.warning("이름을 입력해 줘!")

level = get_level(pet["exp"])
stage, emoji = get_stage(level)
mood, mood_emoji = get_mood()

# 펫 방에 장식 표시
decorations = " ".join(pet["decorations"])
safe_name = html.escape(pet["name"])
safe_message = html.escape(pet["message"])

st.markdown(
    f"""
    <div class="pet-room">
        <div class="room-deco">☁️ ✨ {decorations} ✨ ☁️</div>
        <div class="heart">💗</div>
        <div class="pet">{emoji}</div>
        <div class="heart">💕</div>
        <h2>{safe_name}</h2>
        <p>{stage} · 레벨 {level}</p>
        <p>{mood_emoji} {mood}</p>
        <p style="background:#ffffffbb;padding:12px;border-radius:14px;">
            💬 {safe_message}
        </p>
    </div>
    """,
    unsafe_allow_html=True
)

st.write("")

# 상태 막대
c1, c2 = st.columns(2)

with c1:
    st.write("🍓 배부름")
    st.progress(pet["hunger"] / 100)
    st.caption(f"{pet['hunger']} / 100")

with c2:
    st.write("⚡ 에너지")
    st.progress(pet["energy"] / 100)
    st.caption(f"{pet['energy']} / 100")

st.write("💖 친밀도:", pet["love"])
st.progress(min(pet["love"] / 100, 1.0))

current_exp = pet["exp"] % EXP_PER_LEVEL
st.write(f"⭐ 경험치: {current_exp}/{EXP_PER_LEVEL} XP")
st.progress(current_exp / EXP_PER_LEVEL)

st.divider()

st.subheader("🧸 몽글이랑 놀기")

b1, b2 = st.columns(2)
b3, b4 = st.columns(2)

with b1:
    if st.button("🍓 간식 주기", use_container_width=True):
        do_action("feed")
        st.rerun()

with b2:
    if st.button("💗 쓰다듬기", use_container_width=True):
        do_action("pet")
        st.rerun()

with b3:
    if st.button("🎾 같이 놀기", use_container_width=True):
        do_action("play")
        st.rerun()

with b4:
    if st.button("🌙 낮잠 자기", use_container_width=True):
        do_action("sleep")
        st.rerun()


# ==================================
# 6. 생활 습관 미션
# ==================================

st.divider()
st.subheader("🌱 오늘의 생활 습관 미션")
st.write("실천한 습관을 기록하면 몽글이가 경험치를 얻어!")

activity = st.selectbox("완료한 활동", list(ACTIVITIES.keys()))

if st.button("✅ 미션 완료!", use_container_width=True):
    records = get_today_records()
    completed = [
        r.get("name") for r in records
        if isinstance(r, dict)
    ]

    if activity in completed:
        st.warning("오늘 이 미션은 이미 완료했어!")
    else:
        old_level = get_level(pet["exp"])
        pet["exp"] += ACTIVITIES[activity]
        pet["love"] += 2
        pet["hunger"] = max(0, pet["hunger"] - 2)

        records.append({
            "name": activity,
            "points": ACTIVITIES[activity]
        })
        pet["records"][today] = records

        new_level = get_level(pet["exp"])

        if new_level > old_level:
            _, new_emoji = get_stage(new_level)
            pet["message"] = f"우와! {new_emoji} 새로운 모습으로 진화했어!"
            st.balloons()
        else:
            pet["message"] = f"{activity} 성공! 우리 같이 성장했어 🌱"

        if len(records) >= 3 and "🪴" not in pet["decorations"]:
            pet["decorations"].append("🪴")
            pet["message"] += " 방에 새 식물이 생겼어!"

        pet["love"] = min(pet["love"], 9999)
        save_data()
        st.rerun()

today_records = get_today_records()

st.write(f"📅 오늘의 미션: {len(today_records)}개 완료")

if today_records:
    for record in today_records:
        if isinstance(record, dict):
            st.write(
                f"☑️ {record.get('name', '활동')} "
                f"+{record.get('points', 0)} XP"
            )
else:
    st.info("첫 번째 미션을 완료해서 몽글이를 기쁘게 해 줘!")

# ==================================
# 7. 최근 7일 통계
# ==================================

st.divider()
st.subheader("📊 몽글이와 함께한 일주일")

chart = {}

from datetime import timedelta

for i in range(6, -1, -1):
    day = date.today() - timedelta(days=i)
    records = pet["records"].get(day.isoformat(), [])
    chart[day.strftime("%m/%d")] = len(records) if isinstance(records, list) else 0

st.bar_chart(chart)

# ==================================
# 8. 방 꾸미기
# ==================================

st.divider()
st.subheader("🏡 펫의 방 꾸미기")

decor_options = {
    "🌷 꽃": "🌷",
    "⭐ 별": "⭐",
    "🍄 버섯": "🍄",
    "🌈 무지개": "🌈",
    "🪴 식물": "🪴",
}

selected_deco = st.selectbox("장식 선택", list(decor_options.keys()))

if st.button("✨ 방에 장식 놓기"):
    deco = decor_options[selected_deco]

    if deco in pet["decorations"]:
        st.info("이 장식은 이미 방에 있어!")
    else:
        pet["decorations"].append(deco)
        pet["message"] = f"방이 더 예뻐졌어! {deco}"
        save_data()
        st.rerun()

if st.button("🔄 펫 처음부터 다시 키우기"):
    st.session_state.pet = DEFAULT.copy()
    save_data()
    st.rerun()
