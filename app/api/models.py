import uuid

from django.db import models


class RequestStatus(models.TextChoices):
    IN_PROGRESS = "IN_PROGRESS"
    READY = "READY"
    ERROR = "ERROR"


class PartStatus(models.TextChoices):
    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    DONE = "DONE"
    FAILED = "FAILED"


class CrackRequest(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    hash = models.CharField(
        max_length=32,
        db_index=True,
    )

    max_length = models.PositiveIntegerField()

    status = models.CharField(
        max_length=20,
        choices=RequestStatus.choices,
        default=RequestStatus.IN_PROGRESS,
        db_index=True,
    )

    part_count = models.PositiveIntegerField()

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    deadline_at = models.DateTimeField()

    class Meta:
        indexes = [
            models.Index(fields=["status"]),
            models.Index(fields=["hash"]),
        ]

    def __str__(self) -> str:
        return f"{self.id}:{self.status}"


class CrackPart(models.Model):
    request = models.ForeignKey(
        CrackRequest,
        on_delete=models.CASCADE,
        related_name="parts",
    )

    part_number = models.PositiveIntegerField()

    part_count = models.PositiveIntegerField()

    status = models.CharField(
        max_length=20,
        choices=PartStatus.choices,
        default=PartStatus.PENDING,
        db_index=True,
    )

    attempts = models.PositiveIntegerField(
        default=0,
    )

    class Meta:
        indexes = [
            models.Index(fields=["request"]),
            models.Index(fields=["status"]),
        ]

    def __str__(self) -> str:
        return f"{self.request_id}:{self.part_number}/{self.part_count}"


class CrackResult(models.Model):
    request = models.ForeignKey(
        CrackRequest,
        on_delete=models.CASCADE,
        related_name="results",
    )

    word = models.CharField(
        max_length=255,
    )

    class Meta:
        indexes = [
            models.Index(fields=["request"]),
            models.Index(fields=["word"]),
        ]

    def __str__(self) -> str:
        return f"{self.request_id}:{self.word}"