import hashlib

from celery import shared_task
from django.db import transaction
from django.db.utils import OperationalError
from django.utils import timezone

from .models import CrackPart, CrackRequest, CrackResult, PartStatus, RequestStatus

ALPHABET = "abcdefghijklmnopqrstuvwxyz0123456789"
BASE = len(ALPHABET)


def total_candidates(max_length: int) -> int:
    return sum(BASE ** length for length in range(1, max_length + 1))


def index_to_word(index: int, max_length: int) -> str:
    length = 1
    while length <= max_length:
        block_size = BASE ** length
        if index < block_size:
            break
        index -= block_size
        length += 1

    if length > max_length:
        raise ValueError("index is out of range for max_length")

    chars = []
    for _ in range(length):
        chars.append(ALPHABET[index % BASE])
        index //= BASE
    chars.reverse()
    return "".join(chars)


def iter_indices_for_part(total: int, part_number: int, part_count: int):
    index = part_number
    while index < total:
        yield index
        index += part_count


def maybe_finalize_request(request_id):
    request = CrackRequest.objects.get(id=request_id)

    if request.parts.filter(status=PartStatus.FAILED).exists():
        if request.status != RequestStatus.ERROR:
            request.status = RequestStatus.ERROR
            request.save(update_fields=["status"])
        return

    total_parts = request.part_count
    done_parts = request.parts.filter(status=PartStatus.DONE).count()
    if done_parts == total_parts and request.status == RequestStatus.IN_PROGRESS:
        request.status = RequestStatus.READY
        request.save(update_fields=["status"])


@shared_task(bind=True, autoretry_for=(OperationalError,), retry_backoff=True, max_retries=5)
def crack_hash_part(
    self,
    request_id: str,
    hash_value: str,
    max_length: int,
    part_number: int,
    part_count: int,
):
    request = CrackRequest.objects.get(id=request_id)
    part = CrackPart.objects.get(request=request, part_number=part_number)

    if request.status != RequestStatus.IN_PROGRESS:
        return {"requestId": request_id, "partNumber": part_number, "status": "SKIPPED"}

    if part.status == PartStatus.DONE:
        return {"requestId": request_id, "partNumber": part_number, "status": "DONE"}

    part.status = PartStatus.IN_PROGRESS
    part.attempts += 1
    part.save(update_fields=["status", "attempts"])

    try:
        target_hash = hash_value.lower()
        total = total_candidates(max_length)
        found_words = []

        for index in iter_indices_for_part(total, part_number, part_count):
            word = index_to_word(index, max_length)
            digest = hashlib.md5(word.encode("utf-8")).hexdigest()
            if digest == target_hash:
                found_words.append(word)

        with transaction.atomic():
            for word in found_words:
                CrackResult.objects.get_or_create(request=request, word=word)
            part.status = PartStatus.DONE
            part.save(update_fields=["status"])

        maybe_finalize_request(request.id)
        return {
            "requestId": request_id,
            "partNumber": part_number,
            "partCount": part_count,
            "matches": found_words,
            "status": "DONE",
        }
    except Exception:
        part.status = PartStatus.FAILED
        part.save(update_fields=["status"])
        maybe_finalize_request(request.id)
        raise


@shared_task
def mark_expired_requests():
    now = timezone.now()
    expired_requests = CrackRequest.objects.filter(
        status=RequestStatus.IN_PROGRESS,
        deadline_at__lt=now,
    )
    updated = expired_requests.update(status=RequestStatus.ERROR)
    return {"expired": updated}