
import json
from pathlib import Path
from datetime import date, datetime, timedelta

import streamlit as st

# -------------------------------
# 1. 기본 설정
# -------------------------------

st.set_page_config(
    page_title="내 디지털 펫",
    page_icon="🐣",
    layout="centered"
)

DATA_FILE = Path("pet_data.json")

ACTIVITIES = {
    "💧 물 마시기": 5,
    "📚 독서하기": 10,
    "🏃 운동하기": 15,
    "🌙 정해진 시간에 자기": 15,
    "🧹 주변 정리하기": 10,
}

LEVEL_EXP = 50


# -------------------------------
# 2. 데이터 저장 및 불러오기
# -------------------------------

def default_data():
    return {
        "pet_name": "",
        "exp": 0,
        "activity_log": {}
    }


def load_data():
    """저장된 펫 데이터를 불러온다."""
    if not DATA_FILE.exists():
        return default_data()

    try:
        with DATA_FILE.open("r", encoding="utf-8") as file:
            data = json.load(file)

        if not isinstance(data, dict):
            return default_data()

        if (
            not isinstance(data.get("pet_name", ""), str)
            or not isinstance(data.get("exp", 0), int)
            or isinstance(data.get("exp", 0), bool)
            or data.get("exp", 0) < 0
            or not isinstance(data.get("activity_log", {}), dict)
        ):
            return default_data()

        data.setdefault("pet_name", "")
        data.setdefault("exp", 0)
        data.setdefault("activity_log", {})

        return data

    except (OSError, json.JSONDecodeError, ValueError, TypeError):
        return default_data()


def save_data(data):
    """현재 데이터를 JSON 파일에 저장한다."""
    try:
        with DATA_FILE.open("w", encoding="utf-8") as file:
            json.dump(data, file, ensure_ascii=False, indent=4)
        return True
    except OSError:
        st.error("데이터 저장에 실패했어요. 저장 공간이나 파일 권한을 확인해 주세요.")
        return False


if "data" not in st.session_state:
    st.session_state.data = load_data()

data = st.session_state.data


# -------------------------------
# 3. 레벨 및 성장 단계 계산
# -------------------------------

def calculate_level(exp):
    """경험치를 이용해 레벨을 계산한다."""
    return exp // LEVEL_EXP + 1


def get_growth_stage(level):
    """레벨에 맞는 성장 단계와 펫 이미지를 반환한다."""
    if level == 1:
        return "알", "🥚"
    elif level <= 3:
        return "아기 펫", "🐣"
    elif level <= 6:
        return "청소년 펫", "🐥"
    else:
        return "성체 펫", "🐤"


def get_mood(today_count):
    """오늘 실천한 활동 수에 따라 기분을 정한다."""
    if today_count >= 4:
        return "최고로 행복해요!", "🥰"
    elif today_count >= 2:
        return "기분이 좋아요!", "😊"
    elif today_count == 1:
        return "조금씩 힘이 나요!", "🙂"
    else:
        return "함께 활동하고 싶어요!", "😴"


# -------------------------------
# 4. 화면 제목 및 펫 생성
# -------------------------------

st.title("🐣 내 생활을 먹고 자라는 디지털 펫")
st.caption("작은 습관이 모여 나만의 펫을 성장시켜요!")

st.divider()

if not data["pet_name"]:
    st.subheader("✨ 나만의 펫 만들기")

    with st.form("create_pet_form"):
        pet_name = st.text_input(
            "펫의 이름을 지어 주세요",
            placeholder="예: 콩이"
        )
        create_button = st.form_submit_button(
            "🥚 펫 생성하기",
            use_container_width=True
        )

    if create_button:
        pet_name = pet_name.strip()

        if not pet_name:
            st.warning("펫 이름을 입력해 주세요!")
        elif len(pet_name) > 20:
            st.warning("이름은 20자 이내로 입력해 주세요.")
        else:
            data["pet_name"] = pet_name

            if save_data(data):
                st.success(f"{pet_name}의 탄생을 축하해요!")
                st.rerun()

    st.info("펫을 생성하면 생활 습관 기록을 시작할 수 있어요.")

    st.stop()


# -------------------------------
# 5. 펫 상태 표시
# -------------------------------

today = date.today()
today_key = today.isoformat()

today_records = data["activity_log"].get(today_key, [])
today_count = len(today_records)

level = calculate_level(data["exp"])
stage, pet_emoji = get_growth_stage(level)
mood, mood_emoji = get_mood(today_count)

st.subheader(f"💖 {data['pet_name']}의 보금자리")

st.markdown(
    f"""
    <div style="
        background: linear-gradient(135deg, #fff0f5, #e8f7ff);
        padding: 25px;
        border-radius: 20px;
        text-align: center;
        border: 2px solid #f3d7e5;
    ">
        <div style="font-size: 90px;">{pet_emoji}</div>
        <h2 style="color: #6c5b7b;">{data['pet_name']}</h2>
        <p style="font-size: 18px; color: #555;">
            {stage} · 레벨 {level}
        </p>
        <p style="font-size: 17px;">
            {mood_emoji} {mood}
        </p>
    </div>
    """,
    unsafe_allow_html=True
)

st.write("")

# 다음 레벨까지 필요한 경험치
current_level_exp = data["exp"] % LEVEL_EXP
remaining_exp = LEVEL_EXP - current_level_exp

st.subheader("🌱 성장 현황")

col1, col2, col3 = st.columns(3)

col1.metric("현재 레벨", f"Lv. {level}")
col2.metric("총 경험치", f"{data['exp']} XP")
col3.metric("오늘 실천", f"{today_count}회")

st.progress(current_level_exp / LEVEL_EXP)

if level == 1 and data["exp"] == 0:
    st.caption(f"첫 레벨업까지 {remaining_exp} XP가 필요해요!")
else:
    st.caption(f"다음 레벨까지 {remaining_exp} XP가 필요해요!")

st.divider()


# -------------------------------
# 6. 생활 습관 기록
# -------------------------------

st.subheader("🎯 오늘의 미션")
st.write("실천한 활동을 선택하고 완료 버튼을 눌러 주세요!")

activity = st.selectbox(
    "오늘 실천한 활동",
    list(ACTIVITIES.keys()),
    key="selected_activity"
)

st.caption(f"완료 시 획득 경험치: +{ACTIVITIES[activity]} XP")

if st.button("✨ 활동 완료!", use_container_width=True):
    records = data["activity_log"].setdefault(today_key, [])

    completed_names = [
        record["name"] for record in records
        if isinstance(record, dict) and "name" in record
    ]

    if activity in completed_names:
        st.warning("이 활동은 오늘 이미 기록했어요! 다른 활동에 도전해 봐요.")
    else:
        gained_exp = ACTIVITIES[activity]

        records.append({
            "name": activity,
            "points": gained_exp,
            "time": datetime.now().strftime("%H:%M")
        })

        old_level = calculate_level(data["exp"])
        data["exp"] += gained_exp
        new_level = calculate_level(data["exp"])

        if save_data(data):
            if new_level > old_level:
                st.balloons()
                st.success(
                    f"레벨 업! 🎉 {data['pet_name']}이(가) "
                    f"레벨 {new_level}이 되었어요!"
                )
            else:
                st.success(
                    f"{activity} 성공! "
                    f"{data['pet_name']}이(가) {gained_exp} XP를 얻었어요!"
                )

            st.rerun()


# -------------------------------
# 7. 오늘의 활동 기록
# -------------------------------

st.subheader("📋 오늘의 활동 기록")

today_records = data["activity_log"].get(today_key, [])

if today_records:
    for record in today_records:
        if isinstance(record, dict):
            name = record.get("name", "활동")
            points = record.get("points", 0)
            time = record.get("time", "")
            st.write(f"✅ {name} — +{points} XP ({time})")
else:
    st.info("아직 기록된 활동이 없어요. 첫 미션을 완료해 보세요!")


# -------------------------------
# 8. 최근 7일 통계
# -------------------------------

st.divider()
st.subheader("📊 최근 7일간의 성장 기록")

chart_dates = []
chart_counts = []
total_week_count = 0

for i in range(6, -1, -1):
    day = today - timedelta(days=i)
    day_key = day.isoformat()
    records = data["activity_log"].get(day_key, [])

    count = len([
        record for record in records
        if isinstance(record, dict) and "name" in record
    ])

    chart_dates.append(day.strftime("%m/%d"))
    chart_counts.append(count)
    total_week_count += count

st.bar_chart({
    "날짜": chart_dates,
    "실천 횟수": chart_counts
}, x="날짜", y="실천 횟수")

st.metric("최근 7일 총 실천 횟수", f"{total_week_count}회")

st.divider()


# -------------------------------
# 9. 전체 미션 안내
# -------------------------------

with st.expander("📖 미션별 경험치 확인"):
    for name, points in ACTIVITIES.items():
        st.write(f"{name}: +{points} XP")

    st.caption(
        f"경험치 {LEVEL_EXP} XP를 모을 때마다 레벨이 1 상승해요."
    )

with st.expander("💡 프로그램 이용 안내"):
    st.write("- 하루에 같은 활동은 한 번만 기록할 수 있어요.")
    st.write("- 다른 활동은 각각 기록할 수 있어요.")
    st.write("- 활동 기록과 경험치는 JSON 파일에 저장돼요.")
    st.write("- 펫의 기분은 오늘 실천한 활동 수에 따라 달라져요.")
    st.write("- 최근 7일간의 실천 횟수를 그래프로 확인할 수 있어요.")


# -------------------------------
# 10. 펫 초기화
# -------------------------------

st.divider()

with st.expander("⚙️ 펫 데이터 초기화"):
    st.warning("초기화하면 펫의 이름, 경험치, 활동 기록이 모두 삭제돼요.")

    confirm_reset = st.checkbox(
        "모든 데이터를 삭제하는 것에 동의합니다.",
        key="confirm_reset"
    )

    if st.button("🗑️ 펫 처음부터 다시 키우기"):
        if confirm_reset:
            if save_data(default_data()):
                st.session_state.data = default_data()
                st.success("데이터를 초기화했어요.")
                st.rerun()
        else:
            st.warning("초기화하려면 먼저 확인란에 체크해 주세요.")
