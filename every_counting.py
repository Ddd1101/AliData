from datetime import datetime, date, timedelta

if __name__ == "__main__":
    todayTmp = datetime.strptime(str(date.today()), "%Y-%m-%d")
    startDateTimeTmp = todayTmp + timedelta(days=-1)
    endDateTimeTmp = todayTmp + timedelta(days=0)

    print(startDateTimeTmp, endDateTimeTmp)
