from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

QUESTIONS = [
    {
        "question": "봄, 여름, 가을, 겨울 중 어느 계절을 좋아하시나요?",
        "choices": [
            {"text": "봄", "scores": {"경상북도 청송군": 2, "전라남도 곡성군": 2}},
            {"text": "여름", "scores": {"전라남도 곡성군": 4}},
            {"text": "가을", "scores": {"경상북도 청송군": 4}},
            {"text": "겨울", "scores": {"경상북도 청송군": 3, "전라남도 곡성군": 1}},
        ],
    },
    {
        "question": "식탁 위에 음식이 즐비해 있습니다. 가장 먼저 먹고 싶은 음식은?",
        "choices": [
            {"text": "사과", "scores": {"경상북도 청송군": 4}},
            {"text": "밤", "scores": {}},
            {"text": "인삼", "scores": {}},
            {"text": "매운탕", "scores": {"전라남도 곡성군": 4}},
        ],
    },
        {
        "question": "오늘은 놀러가는 날! 어디가 더 끌리나요?",
        "choices": [
            {"text": "바다", "scores": {}},
            {"text": "산", "scores": {"경상북도 청송군": 4, "전라남도 곡성군": 1}},
            {"text": "계곡", "scores": {"경상북도 청송군": 4, "전라남도 곡성군": 3}},
            {"text": "강", "scores": {"전라남도 곡성군": 4}},
        ],
    },
    {
        "question": "가장 흥미롭고 궁금한 단어를 선택하세요!",
        "choices": [
            {"text": "산소", "scores": {"경상북도 청송군": 3}},
            {"text": "기차", "scores": {"전라남도 곡성군": 4}},
            {"text": "장미", "scores": {"전라남도 곡성군": 2}},
            {"text": "버들", "scores": {"경상북도 청송군": 4}},
        ],
    },
    {
        "question": "자신과 어울리는 사자성어는 어떤 것인가요?",
        "choices": [
            {"text": "상부상조", "scores": {"경상북도 청송군": 1, "전라남도 곡성군": 1}},
            {"text": "금상첨화", "scores": {"경상북도 청송군": 4}},
            {"text": "유유자적", "scores": {"전라남도 곡성군": 4}},
            {"text": "일석이조", "scores": {"경상북도 청송군": 1, "전라남도 곡성군": 1}},
        ],
    },
]

@login_required
def test(request, question_number):
    custom_user = request.user.customuser

    current_question = question_number - 1
    scores = request.session.get('scores', {"경상북도 청송군": 100, "전라남도 곡성군": 0})

    if request.method == "POST":
        selected_choice = request.POST.get("choice")
        if selected_choice:
            choice = QUESTIONS[current_question]["choices"][int(selected_choice)]
            for region, score in choice["scores"].items():
                scores[region] += score

        current_question += 1
        if current_question >= len(QUESTIONS):
            recommended_region = max(scores, key=scores.get)
            request.session.pop('scores', None)

            context = {
                'recommended_region': recommended_region,
                'custom_user': custom_user
            }

            return render(request, 'regions/result.html', context)

        return redirect('regions:test', question_number=current_question + 1)

    question = QUESTIONS[current_question]
    return render(request, 'regions/test.html', {'question': question, 'current_question': question_number})

