
import streamlit as st
import pandas as pd
import xml.etree.ElementTree as ET
from datetime import datetime

st.set_page_config(
    page_title="Apple Watch 수면 분석",
    page_icon="🌙",
    layout="wide"
)

st.title("🌙 Apple Watch 수면 습관 분석")
st.write("애플워치의 수면 기록을 활용하여 나의 수면 습관을 분석합니다.")

# 데이터 저장 공간
if "records" not in st.session_state:
    st.session_state.records = []

if "apple_records" not in st.session_state:
    st.session_state.apple_records = []

st.divider()

# 애플워치 데이터 가져오기
st.header("⌚ Apple Watch 연동")

st.write("""
아이폰 건강 앱에서 내보낸 건강 데이터의
export.xml 파일을 업로드하세요.
""")

uploaded_file = st.file_uploader(
    "Apple 건강 데이터 업로드",
    type=["xml"]
)

def read_apple_sleep(file):
    root = ET.fromstring(file)
    sleep_data = {}

    sleep_values = [
        "HKCategoryValueSleepAnalysisAsleep",
        "HKCategoryValueSleepAnalysisAsleepCore",
        "HKCategoryValueSleepAnalysisAsleepDeep",
        "HKCategoryValueSleepAnalysisAsleepREM",
        "Asleep"
    ]

    for record in root.iter("Record"):

        if record.get("type") != "HKCategoryTypeIdentifierSleepAnalysis":
            continue

        if record.get("value") not in sleep_values:
            continue

        start = datetime.fromisoformat(
            record.get("startDate").replace(" ", "T")
        )

        end = datetime.fromisoformat(
            record.get("endDate").replace(" ", "T")
        )

        if end <= start:
            continue

        day = end.date()

        if day not in sleep_data:
            sleep_data[day] = []

        sleep_data[day].append((start, end))

    results = []

    for day, intervals in sleep_data.items():

        intervals.sort(key=lambda x: x[0])

        merged = []

        for start, end in intervals:

            if not merged or start >= merged[-1][1]:
                merged.append([start, end])
            else:
                merged[-1][1] = max(
                    merged[-1][1], end
                )

        total_seconds = sum(
            (end - start).total_seconds()
            for start, end in merged
        )

        hours = total_seconds / 3600

        results.append({
            "날짜": str(day),
            "수면 시간": round(hours, 2)
        })

    return results


if uploaded_file is not None:

    if st.button("애플워치 수면 기록 불러오기"):

        try:
            data = read_apple_sleep(
                uploaded_file.getvalue()
            )

            st.session_state.apple_records = data

            if data:
                st.success(
                    f"{len(data)}일의 수면 기록을 불러왔습니다!"
                )
            else:
                st.warning("수면 기록을 찾지 못했습니다.")

        except Exception as e:
            st.error("파일을 읽을 수 없습니다. 건강 앱의 export.xml인지 확인하세요.")

# 애플워치 기록 출력
if st.session_state.apple_records:

    st.subheader("⌚ 애플워치 수면 기록")

    apple_df = pd.DataFrame(
        st.session_state.apple_records
    )

    st.dataframe(
        apple_df,
        use_container_width=True
    )

    apple_average = apple_df["수면 시간"].mean()

    st.metric(
        "애플워치 평균 수면 시간",
        f"{apple_average:.1f}시간"
    )

    st.line_chart(
        apple_df.set_index("날짜")[["수면 시간"]]
    )

st.divider()

# 직접 입력 기능
st.header("✏️ 수면 기록 직접 입력")

date = st.date_input("날짜 선택")

col1, col2 = st.columns(2)

with col1:
    sleep_time = st.time_input(
        "취침 시간",
        value=None
    )

with col2:
    wake_time = st.time_input(
        "기상 시간",
        value=None
    )

if st.button("수면 시간 분석하기"):

    if sleep_time is None or wake_time is None:
        st.warning("시간을 모두 입력해 주세요.")

    elif sleep_time == wake_time:
        st.warning("취침 시간과 기상 시간을 다르게 입력하세요.")

    else:
        start = sleep_time.hour * 60 + sleep_time.minute
        end = wake_time.hour * 60 + wake_time.minute

        if end > start:
            minutes = end - start
        else:
            minutes = (1440 - start) + end

        hours = minutes / 60

        st.subheader("📊 수면 분석 결과")

        st.metric("총 수면 시간", f"{hours:.1f}시간")

        if hours < 7:
            st.warning("수면 시간이 부족한 편입니다.")
            st.info("취침 시간을 조금 앞당겨 보세요.")

        elif hours <= 9:
            st.success("적절한 수면 시간입니다!")
            st.info("규칙적인 수면 습관을 유지해 보세요.")

        else:
            st.info("비교적 긴 수면 시간입니다.")
            st.info("일정한 취침 및 기상 시간을 유지해 보세요.")

        record = {
            "날짜": str(date),
            "취침 시간": sleep_time.strftime("%H:%M"),
            "기상 시간": wake_time.strftime("%H:%M"),
            "수면 시간": round(hours, 2)
        }

        st.session_state.records = [
            r for r in st.session_state.records
            if r["날짜"] != str(date)
        ]

        st.session_state.records.append(record)

        st.success("수면 기록이 저장되었습니다!")

st.divider()

# 전체 수면 기록 분석
st.header("📈 전체 수면 습관 분석")

all_records = []

for r in st.session_state.records:
    all_records.append({
        "날짜": r["날짜"],
        "수면 시간": r["수면 시간"]
    })

for r in st.session_state.apple_records:
    all_records.append(r)

if all_records:

    df = pd.DataFrame(all_records)

    # 같은 날짜에 수동 기록과 애플워치 기록이 있으면
    # 애플워치 기록을 우선 사용
    df = df.drop_duplicates(
        subset=["날짜"],
        keep="last"
    )

    df = df.sort_values("날짜")

    st.dataframe(df, use_container_width=True)

    average = df["수면 시간"].mean()

    st.metric(
        "전체 평균 수면 시간",
        f"{average:.1f}시간"
    )

    st.subheader("수면 시간 변화")

    st.line_chart(
        df.set_index("날짜")[["수면 시간"]]
    )

    if average < 7:
        st.warning("평균 수면 시간이 부족한 편입니다.")

    elif average <= 9:
        st.success("평균 수면 시간이 적절한 편입니다.")

    else:
        st.info("평균 수면 시간이 비교적 깁니다.")

else:
    st.info("아직 수면 기록이 없습니다.")

st.divider()

if st.button("전체 기록 삭제"):
    st.session_state.records = []
    st.session_state.apple_records = []
    st.rerun()

st.caption("※ 애플워치 수면 데이터는 건강 앱에서 내보낸 XML 파일을 통해 가져옵니다.")
st.caption("※ 분석 결과는 참고용이며 개인별 수면 필요량은 다를 수 있습니다.")
