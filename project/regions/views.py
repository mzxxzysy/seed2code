from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

QUESTIONS = [
    {
        "question": "봄, 여름, 가을, 겨울 중 어느 계절을 좋아하시나요?",
        "choices": [
            {"text": "봄", "scores": {"청송": 2, "곡성": 2}},
            {"text": "여름", "scores": {"곡성": 4}},
            {"text": "가을", "scores": {"청송": 4}},
            {"text": "겨울", "scores": {"청송": 3, "곡성": 1}},
        ],
    },
    {
        "question": "식탁 위에 음식이 즐비해 있습니다. 가장 먼저 먹고 싶은 음식은?",
        "choices": [
            {"text": "사과", "scores": {"청송": 4}},
            {"text": "밤", "scores": {}},
            {"text": "인삼", "scores": {}},
            {"text": "매운탕", "scores": {"곡성": 4}},
        ],
    },
        {
        "question": "오늘은 놀러가는 날! 어디가 더 끌리나요?",
        "choices": [
            {"text": "바다", "scores": {}},
            {"text": "산", "scores": {"청송": 4, "곡성": 1}},
            {"text": "계곡", "scores": {"청송": 4, "곡성": 3}},
            {"text": "강", "scores": {"곡성": 4}},
        ],
    },
    {
        "question": "가장 흥미롭고 궁금한 단어를 선택하세요!",
        "choices": [
            {"text": "산소", "scores": {"청송": 3}},
            {"text": "기차", "scores": {"곡성": 4}},
            {"text": "장미", "scores": {"곡성": 2}},
            {"text": "버들", "scores": {"청송": 4}},
        ],
    },
    {
        "question": "자신과 어울리는 사자성어는 어떤 것인가요?",
        "choices": [
            {"text": "상부상조", "scores": {"청송": 1, "곡성": 1}},
            {"text": "금상첨화", "scores": {"청송": 4}},
            {"text": "유유자적", "scores": {"곡성": 4}},
            {"text": "일석이조", "scores": {"청송": 1, "곡성": 1}},
        ],
    },
]

@login_required
def test(request, question_number):
    current_question = question_number - 1
    scores = request.session.get('scores', {"청송": 0, "곡성": 0})

    if request.method == "POST":
        print(question_number)
        selected_choice = request.POST.get("choice")
        if selected_choice:
            choice = QUESTIONS[current_question]["choices"][int(selected_choice)]
            for region, score in choice["scores"].items():
                scores[region] += score

        current_question += 1
        if current_question >= len(QUESTIONS):
            recommended_region = max(scores, key=scores.get)
            request.session.pop('scores', None)
            return render(request, 'regions/result.html', {'recommended_region': recommended_region})

        return redirect('regions:test', question_number=current_question + 1)

    question = QUESTIONS[current_question]
    return render(request, 'regions/test.html', {'question': question, 'current_question': question_number})

