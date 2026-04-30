from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import CrackRequest, RequestStatus
from .serializers import (
    CrackHashRequestSerializer,
    CrackStatusQuerySerializer,
    CrackRequestListItemSerializer,
)

from .services import create_request_with_parts

from drf_spectacular.utils import extend_schema


class CrackHashView(APIView):
    @extend_schema(
        request=CrackHashRequestSerializer,
        responses={201: None},
    )
    def post(self, request):
        serializer = CrackHashRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        req = create_request_with_parts(
            hash_value=serializer.validated_data["hash"],
            max_length=serializer.validated_data["maxLength"],
        )
        return Response({"requestId": str(req.id)}, status=status.HTTP_201_CREATED)


class CrackStatusView(APIView):
    @extend_schema(
        parameters=[CrackStatusQuerySerializer],
        responses={200: None},
    )
    def get(self, request):
        q = CrackStatusQuerySerializer(data=request.query_params)
        q.is_valid(raise_exception=True)

        req = get_object_or_404(CrackRequest, id=q.validated_data["requestId"])

        if req.status == RequestStatus.READY:
            words = list(req.results.values_list("word", flat=True))
            return Response({"status": "READY", "data": words}, status=status.HTTP_200_OK)

        if req.status == RequestStatus.ERROR:
            return Response({"status": "ERROR", "data": None}, status=status.HTTP_200_OK)

        return Response({"status": "IN_PROGRESS", "data": None}, status=status.HTTP_200_OK)
    

class CrackRequestsView(APIView):

    @extend_schema(
        request=None,
        responses={200: CrackRequestListItemSerializer(many=True)},
    )
    def get(self, request):
        requests = CrackRequest.objects.all().order_by("-created_at")

        serializer = CrackRequestListItemSerializer(requests, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)
    


class CrackRequestDeleteView(APIView):

    @extend_schema(
        request=None,
        responses={204: None},
    )
    def delete(self, request, request_id):
        crack_request = get_object_or_404(
            CrackRequest,
            id=request_id,
        )

        crack_request.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)