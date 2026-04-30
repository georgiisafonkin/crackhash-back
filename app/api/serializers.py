import re
from rest_framework import serializers


MD5_RE = re.compile(r"^[a-fA-F0-9]{32}$")


class CrackHashRequestSerializer(serializers.Serializer):
    hash = serializers.CharField(max_length=32, min_length=32)
    maxLength = serializers.IntegerField(min_value=1, max_value=10)

    def validate_hash(self, value: str) -> str:
        if not MD5_RE.fullmatch(value):
            raise serializers.ValidationError("hash must be a valid 32-char MD5 hex string")
        return value.lower()


class CrackHashAcceptedSerializer(serializers.Serializer):
    requestId = serializers.UUIDField()


class CrackStatusQuerySerializer(serializers.Serializer):
    requestId = serializers.UUIDField()


class CrackStatusResponseSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=["IN_PROGRESS", "READY", "ERROR"])
    data = serializers.ListField(child=serializers.CharField(), allow_null=True)


class CrackRequestListItemSerializer(serializers.Serializer):
    requestId = serializers.UUIDField(source="id")
    hash = serializers.CharField()
    status = serializers.ChoiceField(
        choices=["IN_PROGRESS", "READY", "ERROR"]
    )
    maxLength = serializers.IntegerField(source="max_length")
    createdAt = serializers.DateTimeField(source="created_at")