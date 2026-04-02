from celery import shared_task
import hashlib

md5 = hashlib.md5()

@shared_task
def crack_hash(hash, maxLength):
    return hash
