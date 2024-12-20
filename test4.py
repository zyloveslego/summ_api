import threading
import json
import requests


# url1 = 'http://wangserver.ddns.net:9013/ai_search/'
url1 = 'http://127.0.0.1:8000/ai_search/'
url1 = "http://127.0.0.1:8000/detectai/ai_detect"


data = {
    # 'message': 'large language model',
    'message': 'add keywords, survey',
    'searchId': 'abv',
    'text': 'this is the first test text.'
}


r = requests.post(url1, data=data)
print(r.text)


# import requests
# from pprint import pprint
#
# # with 0 indicating the maximum confidence that the text is human-written.
# # and 1 indicating the maximum confidence that the text is AI-generated.
#
# response = requests.post(
#     "https://api.sapling.ai/api/v1/aidetect",
#     json={
#         "key": "",
#         "text": "Text to run detection on. The limit is currently 50,000 characters. If latency is high or requests time out, we recommend adapting this script. Please contact us if you need to run the system on longer inputs. We can also provide suggestions on how to chunk your text into smaller pieces and then combine detection results."
#     }
# )
#
# pprint(response.json())

# # python -m pip install sapling-py
#
# from sapling import SaplingClient
# from pprint import pprint
#
# api_key =''
# client = SaplingClient(api_key=api_key)
# detection_scores = client.aidetect('This is sample text.', sent_scores=True)
# pprint(detection_scores)
