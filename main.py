
import streamlit as st
import pandas as pd

# 페이지 설정
st.set_page_config(
    page_title="수면 습관 분석 프로그램",
    page_icon="🌙",
    layout="centered"
)

# 제목
st.title("🌙 수면 습관 분석 프로그램")
st.write("나의 수면 습관을 기록하고 건강한 생활을 만들어 보세요!")

st.divider()

# 수면 기록 저장
if "records" not in st.session_state:
    st.session_state.records = []

# 1. 수면 시간 입력
st.subheader("1. 수면 시간 입력")

date = st.date_input("날짜 선택")

col1, col2 = st.columns(2)

with col1:
    sleep_time = st.time_input(
        "취침 시간",
        value=None,
        key="sleep_time",
        help="클릭하여 취침 시간을 선택하세요."
    )

with col2:
    wake_time = st.time_input(
        "기상 시간",
        value=None,
        key="wake_time",
        help="클릭하여 기상 시간을 선택하세요."
    )

# 2. 수면 시간 분석
if st.button("수면 시간 분석하기", use_container_width=True):

    if sleep_time is None or wake_time is None:
        st.warning("취침 시간과 기상 시간을 모두 입력해 주세요.")

    elif sleep_time == wake_time:
        st.warning("취침 시간과 기상 시간을 다르게 입력해 주세요.")

    else:
        sleep_minutes = sleep_time.hour * 60 + sleep_time.minute
        wake_minutes = wake_time.hour * 60 + wake_time.minute

        if wake_minutes > sleep_minutes:
            total_minutes = wake_minutes - sleep_minutes
        else:
            total_minutes = (24 * 60 - sleep_minutes) + wake_minutes

        total_hours = total_minutes / 60

        # 수면 시간 출력
        st.divider()
        st.subheader("2. 수면 분석 결과")

        st.metric("총 수면 시간", f"{total_hours:.1f}시간")

        # 3. 수면 상태 분석 및 조언
        if total_hours < 7:
            st.error("수면 시간이 부족한 편입니다.")
            st.info("💡 개선 조언: 취침 시간을 조금 앞당겨 보세요.")

        elif total_hours <= 9:
            st.success("적절한 수면 시간입니다!")
            st.info("💡 개선 조언: 현재의 규칙적인 수면 습관을 유지해 보세요.")

        else:
            st.info("비교적 긴 수면 시간입니다.")
            st.info("💡 개선 조언: 일정한 취침 및 기상 시간을 유지해 보세요.")

        # 4. 기록 저장
        record = {
            "날짜": str(date),
            "취침 시간": sleep_time.strftime("%H:%M"),
            "기상 시간": wake_time.strftime("%H:%M"),
            "수면 시간": round(total_hours, 2)
        }

        # 같은 날짜 기록 수정
        st.session_state.records = [
            r for r in st.session_state.records
            if r["날짜"] != str(date)
        ]

        st.session_state.records.append(record)

        st.success("수면 기록이 저장되었습니다!")

# 5. 여러 날의 기록 확인
st.divider()
st.subheader("3. 나의 수면 기록")

if len(st.session_state.records) > 0:

    df = pd.DataFrame(st.session_state.records)
    df = df.sort_values("날짜")

    st.dataframe(df, use_container_width=True)

    # 평균 수면 시간
    average = df["수면 시간"].mean()

    st.metric("평균 수면 시간", f"{average:.1f}시간")

    # 6. 수면 시간 그래프
    st.subheader("4. 수면 시간 변화 그래프")

    chart_df = df.set_index("날짜")[["수면 시간"]]

    st.line_chart(chart_df)

    # 7. 전체 수면 습관 분석
    st.subheader("5. 전체 수면 습관 분석")

    if average < 7:
        st.warning("평균 수면 시간이 부족합니다. 수면 시간을 늘려보세요.")

    elif average <= 9:
        st.success("평균 수면 시간이 적절한 편입니다!")

    else:
        st.info("평균 수면 시간이 비교적 깁니다.")

    # 기록 삭제
    st.divider()

    if st.button("전체 수면 기록 삭제"):
        st.session_state.records = []
        st.rerun()

else:
    st.info("아직 저장된 수면 기록이 없습니다. 수면 시간을 입력해 보세요!")

# 하단 안내
st.divider()

st.caption("🌙 규칙적인 수면 습관은 건강한 생활의 시작입니다.")
st.caption("※ 수면 분석은 참고용이며 개인별 수면 필요량은 다를 수 있습니다.")
