from celery import shared_task


@shared_task
def user_created():
    print("User created task")
