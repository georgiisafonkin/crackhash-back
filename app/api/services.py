from datetime import timedelta

from django.conf import settings
from django.db import transaction
from django.utils import timezone

from django.db.models import Q

from .models import (
    CrackPart,
    CrackRequest,
    PartStatus,
    RequestStatus,
)
from .tasks import crack_hash_part

def requeue_unfinished_requests() -> None:
    requests = CrackRequest.objects.filter(
        status=RequestStatus.IN_PROGRESS
    )

    for req in requests:
        unfinished_parts = req.parts.filter(
            Q(status=PartStatus.PENDING) |
            Q(status=PartStatus.IN_PROGRESS) |
            Q(status=PartStatus.FAILED)
        ).order_by("part_number")

        for part in unfinished_parts:
            crack_hash_part.delay(
                request_id=str(req.id),
                hash_value=req.hash,
                max_length=req.max_length,
                part_number=part.part_number,
                part_count=part.part_count,
            )

def create_request_with_parts(*, hash_value: str, max_length: int) -> CrackRequest:
    part_count = int(getattr(settings, "CRACKHASH_PART_COUNT", 4))
    timeout_seconds = int(getattr(settings, "CRACKHASH_REQUEST_TIMEOUT_SECONDS", 300))

    with transaction.atomic():
        req = CrackRequest.objects.create(
            hash=hash_value,
            max_length=max_length,
            status=RequestStatus.IN_PROGRESS,
            part_count=part_count,
            deadline_at=timezone.now() + timedelta(seconds=timeout_seconds),
        )

        CrackPart.objects.bulk_create(
            [
                CrackPart(
                    request=req,
                    part_number=i,
                    part_count=part_count,
                )
                for i in range(part_count)
            ]
        )

        transaction.on_commit(lambda: enqueue_request_parts(str(req.id)))

    return req


def enqueue_request_parts(request_id: str) -> None:
    req = CrackRequest.objects.get(id=request_id)
    parts = req.parts.all().order_by("part_number")
    for part in parts:
        crack_hash_part.delay(
            request_id=str(req.id),
            hash_value=req.hash,
            max_length=req.max_length,
            part_number=part.part_number,
            part_count=part.part_count,
        )