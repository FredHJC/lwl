import requests
import re
url = 'https://m.weibo.cn/api/comments/show?id=4467107636950632&page=1'
headers = {'Cookies':'your cookie',
'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.181 Safari/537.36'}
clean = re.compile('<.*?>')
last_id = ''

counter=0
while True:
  try:
    j = requests.get(url, headers=headers).json()
    latest_comment = j['data']['data'][0]
    latest_id = latest_comment['id']
    if (latest_id != last_id):
      last_id = latest_id
      comment_text = re.sub(clean, '', latest_comment['text'])
      comment_user = re.sub(clean, '', latest_comment['user']['screen_name'])
      print(comment_text + '   [' + comment_user + '] ')
      counter+=1
  except:
    continue