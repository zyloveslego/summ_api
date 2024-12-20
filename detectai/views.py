from django.shortcuts import render
from django.http import JsonResponse
from rest_framework.decorators import api_view
from django.views.decorators.csrf import csrf_exempt
import requests


@csrf_exempt
@api_view(['POST'])
def sapling_detect(request):
    text = request.data.get("text")
    response = requests.post(
        "https://api.sapling.ai/api/v1/aidetect",
        json={
            "key": "",
            "text": text
        }
    )

    # print(response_data)

    return JsonResponse(response.json())