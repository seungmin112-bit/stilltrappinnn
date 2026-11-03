
print("===== 수면 습관 분석 및 개선 프로그램 =====")

sleep_records = []

while True:
    print("\n1. 수면 기록 입력")
    print("2. 수면 기록 및 평균 확인")
    print("3. 프로그램 종료")

    choice = input("메뉴를 선택하세요: ")

    if choice == "1":
        print("\n[수면 기록 입력]")

        day = input("날짜를 입력하세요: ")
        sleep = int(input("취침 시간(0~23시): "))
        wake = int(input("기상 시간(0~23시): "))

        # 수면 시간 계산
        if wake > sleep:
            total = wake - sleep
        else:
            total = (24 - sleep) + wake

        print("\n총 수면 시간:", total, "시간")

        # 수면 상태 분석 및 개선 조언
        if total < 7:
            print("수면 상태: 수면 시간이 부족합니다.")
            print("개선 조언: 조금 더 일찍 잠자리에 들어보세요.")
        elif total <= 9:
            print("수면 상태: 적절한 수면 시간입니다.")
            print("개선 조언: 현재의 수면 습관을 유지해 보세요.")
        else:
            print("수면 상태: 비교적 긴 수면 시간입니다.")
            print("개선 조언: 일정한 취침 및 기상 시간을 유지해 보세요.")

        # 기록 저장
        sleep_records.append([day, total])
        print("수면 기록이 저장되었습니다.")

    elif choice == "2":
        print("\n[수면 기록 및 평균 분석]")

        if len(sleep_records) == 0:
            print("저장된 수면 기록이 없습니다.")
        else:
            for record in sleep_records:
                print(record[0], ":", record[1], "시간")

            average = sum(record[1] for record in sleep_records) / len(sleep_records)

            print("\n기록한 날짜:", len(sleep_records), "일")
            print("평균 수면 시간:", round(average, 1), "시간")

            if average < 7:
                print("전체 분석: 평균 수면 시간이 부족합니다.")
                print("조언: 수면 시간을 조금씩 늘려보세요.")
            elif average <= 9:
                print("전체 분석: 평균 수면 시간이 적절합니다.")
            else:
                print("전체 분석: 평균 수면 시간이 비교적 깁니다.")

    elif choice == "3":
        print("프로그램을 종료합니다.")
        break

    else:
        print("잘못된 입력입니다. 다시 선택하세요.")
