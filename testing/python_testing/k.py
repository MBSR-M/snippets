from datetime import datetime, timedelta

global change_file_name, changed_date


def call_dates():
    print(f"File name: {change_file_name}, Date: {changed_date}")


def main():
    call_dates()
    pass


if __name__ == '__main__':
    start_date = datetime.strptime('2025-01-01', '%Y-%m-%d')
    for i in range(31):
        current_date = start_date + timedelta(days=i)
        change_file_name = current_date.strftime('%Y%m%d')
        changed_date = current_date.strftime('%Y-%m-%d')
        current_month = (datetime.now().replace(month=1).strftime("%Y%m"))
        print('Current month', current_month)
        main()
    for j in range(19, 32):
        print(j)

