from django.shortcuts import render
from django.http import JsonResponse
import openai
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt


# Create your views here.
@csrf_exempt
def get_essay_grade(request):
    text = ""
    if request.method == 'POST':
        print(request.POST)
        text = request.POST.get('text')

    if request.method == 'GET':
        return JsonResponse({})
        # pass

    # text = open(
    #     "/Users/zhouyou/Documents/PHD/wangserver/zy/summ_interface/summarization/tests/summ_test/test_data/news_en.txt").read()

    # text = ' Softball has to be one of the single most greatest sports alive; playing softball in college has always been a goal of mine. I love the dirt that sticks to your face, the sweat dripping from your forehead, and the gallons and gallons of water you poor all over yourself to keep cool in the blistering @CAPS2. Although I love softball I feel that the memories you acquire from the times you have with your teammates, are the things you remember the most through out your softball career. I have always had great memories through softball many laughs, tears, and frustrations so when I had the opportunity to play on a top notch team I looked forward to all the many more memories I would have.  Hood @CAPS1 @CAPS2 was my team name, I had played almost four years with this local team. Many of these girls were like sisters to me they had treated me amazingly through out my years playing with them. I felt like I had my set team, I was going to play with these girls all though high school and we would become even closer. As my fifth year now approached I was looking forward to it, but when my dad came up with the idea that maybe I play for a team not as locally, that idea was also very enticing. I now faced a big dilemma either stay with the team I knew so well and continue to play with them until high school ended; or play with a team I knew nothing about, play with girls that might not like me, girls that were so much better then me, and looked down upon me. As I looked at the pros and cons of both teams I decided no; I would stay with the team that I knew so well and I would stay comfortable at where I was at. At that point softball was just around the corner and I began to reanalyze everything. Did I really want to stay and be comfortable? Or maybe challenge myself to become a better player; maybe i could work hard enough, and have college scouts take a look at me and hopefully have me play for them later. I then decided I would take a chance and try for this team.  As my dad and I drove to the field where I would try out for this team, my stomach was in knots. I wanted this team to like me, I was playing all the possible ways in my head I could greet them so i didn\'t sound snobby or a grump. The time moved quickly and I wished it would slow; my heart felt like it was beating a million times per second. I was so nervous my mouth began to feel sticky and have an odd taste to it, soon after my mouth became bone dry no taste, no flavor, just a sticky mess. The car then was stationary my dad looked at me and just said "ready or not here we come". Nervous began to take over my body my arms were shaking uncontrollably and I was second guessing every move I made, I even had troubles removing my seat belt.  As I approached the field it felt like time was in slow motion, walking by I saw all the girls turn there heads to see what new fresh meat had arrived. My first thought was to run; that was it I didn\'t want to go, I was done I wanted home I was ready to start my year with the @CAPS2, I just couldn\'t take it. Then as I walked onto the field they all grew a smile. Each and everyone of them told me their names, there favorite color, and a small fun fact about themselves. I found myself laughing through out my whole try out, there were no awkward moments and I enjoyed my time there. I couldn\'t wait to go back, I now had made new friends, friends I knew I would grow close with. My year with this team was amazing I have friendships with these girls that I never would have discovered if I hadn\'t gone. Those girls are like family, and the coaches even more so. Laughter played a very big role in the decision I made to play with this team, if I had just gone and tried out, and had I not had fun and laughed, I would have decided to play with the @CAPS2. I have had great memories with the @CAPS2, but also softball is all about going out discovering new friendships; therefore, enjoying the sport as well as the people.'

    try:
        # 要加箭头 -> ！！！！！

        # 或者 \n\n###\n\n

        indicator = "\n\n###\n\n"

        text = text + indicator

        openai.api_key = ""

        ft_model = 'ada:ft-librum2:set8-conventions-2023-07-03-20-36-38'
        res = openai.Completion.create(model=ft_model, prompt=text, max_tokens=1, temperature=0)
        conventions = int(res['choices'][0]['text']) / 2

        ft_model = 'ada:ft-librum2:set8-ideasandcontent-2023-07-03-21-42-16'
        res = openai.Completion.create(model=ft_model, prompt=text, max_tokens=1, temperature=0)
        ideasandcontent = int(res['choices'][0]['text']) / 2

        ft_model = 'ada:ft-librum2:set8-organization-2023-07-03-22-48-23'
        res = openai.Completion.create(model=ft_model, prompt=text, max_tokens=1, temperature=0)
        organization = int(res['choices'][0]['text']) / 2

        ft_model = 'ada:ft-librum2:set8-sentencefluency-2023-07-03-23-53-02'
        res = openai.Completion.create(model=ft_model, prompt=text, max_tokens=1, temperature=0)
        sentencefluency = int(res['choices'][0]['text']) / 2

        ft_model = 'ada:ft-librum2:set8-voice-2023-07-04-01-02-55'
        res = openai.Completion.create(model=ft_model, prompt=text, max_tokens=1, temperature=0)
        voice = int(res['choices'][0]['text']) / 2

        ft_model = 'ada:ft-librum2:set8-wordchoice-2023-07-04-02-47-51'
        res = openai.Completion.create(model=ft_model, prompt=text, max_tokens=1, temperature=0)
        wordchoice = int(res['choices'][0]['text']) / 2

        my_response = {}
        # I O V W S C
        score = {
            "ideas and content": ideasandcontent,
            "organizations": organization,
            "voice": voice,
            "word choice": wordchoice,
            "sentence fluency": sentencefluency,
            "conventions": conventions,
        }

        my_response['status'] = 1
        my_response['score'] = score
        my_response['error_info'] = ""

        return JsonResponse(my_response)

    except Exception as E:
        score = {
            "ideas and content": 0,
            "organizations": 0,
            "voice": 0,
            "word choice": 0,
            "sentence fluency": 0,
            "conventions": 0
        }
        my_response = {'status': 0, 'score': score, 'error_info': str(E)}

        return JsonResponse(my_response)

    # pass
