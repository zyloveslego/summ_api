# api_ctrl_center
### url：/my_summ::
```javascript
  data = {'text': text}
  response = requests.post(url, data=data).json()
  sentence_rank = response['sentence_rank']
  # json dict structure
  # {'sentence':
  #   [
  #       [sentence_index(int), sentence(str), sentence_score(float), sentence_rank(int)],
  #       ...
  #   ]
  # }
```
