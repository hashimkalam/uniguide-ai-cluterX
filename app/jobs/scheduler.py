from apscheduler.schedulers.background import BackgroundScheduler
# import asyncio

def refresh_job():
    print("refresh job called")

def start_scheduler():
    sched = BackgroundScheduler()
    sched.add_job(refresh_job, 'interval', hours=24, id='refresh_discover')
    sched.start()
