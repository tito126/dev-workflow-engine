from datetime import datetime, timedelta

now = datetime.now()
start = now - timedelta(minutes=10)

print(f'Start: {start.strftime("%Y-%m-%d %H:%M:%S")}')
print(f'End: {now.strftime("%Y-%m-%d %H:%M:%S")}')
print(f'--start "{start.strftime("%Y-%m-%d %H:%M:%S")}" --end "{now.strftime("%Y-%m-%d %H:%M:%S")}"')
