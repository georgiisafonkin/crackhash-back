from celery import shared_task

@shared_task
def crack_hash(hash, maxLength):
    return hash
