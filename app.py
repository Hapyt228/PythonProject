# app.py

from flask import Flask, render_template, request, redirect, url_for
from test_data import test_data

app = Flask(__name__)

# Генерация списка для главной страницы
tests = [{"id": k, "title": v["title"]} for k, v in test_data.items()]


# --- 2. ГЛАВНАЯ СТРАНИЦА (/) ---
@app.route('/')
def index():
    return render_template('index.html', tests=tests)


# --- 3. СТРАНИЦА ТЕСТА (/test/ID) ---
@app.route('/test/<int:test_id>', methods=['GET', 'POST'])
def run_test(test_id):
    if test_id not in test_data:
        return "Тест не найден", 404

    current_test = test_data[test_id]

    if request.method == 'POST':
        total_score = 0
        user_answers = request.form

        for question in current_test["questions"]:
            q_id = question["id"]
            user_choice_key = user_answers.get(f'question_{q_id}')

            if user_choice_key:
                chosen_option = question["options"].get(user_choice_key)

                # Защита от потенциальной ошибки типа, если в данных points строка, а не число
                points = chosen_option.get("points", 0) if chosen_option else 0
                if isinstance(points, str):
                    try:
                        points = int(points)
                    except ValueError:
                        points = 0  # В случае ошибки присваиваем 0

                total_score += points

        return redirect(url_for('show_result',
                                score=total_score,
                                total=current_test["max_score"],
                                test_id=test_id
                                ))

    return render_template('test_form.html', test=current_test)


# --- 4. СТРАНИЦА РЕЗУЛЬТАТОВ (/result) ---
@app.route('/result')
def show_result():
    score = request.args.get('score', type=int)
    total = request.args.get('total', type=int)
    test_id = request.args.get('test_id', type=int)

    percentage = round((score / total) * 100) if total else 0
    recommendation_text = ""

    if test_id in test_data and "recommendations" in test_data[test_id]:
        recommendations = test_data[test_id]["recommendations"]

        # Сортируем рекомендации по max_score на всякий случай
        recommendations.sort(key=lambda x: x["max_score"])

        for tier in recommendations:
            if score <= tier["max_score"]:
                recommendation_text = tier["text"]
                break

        # Если счет выше самого высокого порога, берем последнюю рекомендацию
        if not recommendation_text and recommendations:
            recommendation_text = recommendations[-1]["text"]

    return render_template('result.html',
                           score=score,
                           total=total,
                           percentage=percentage,
                           recommendation=recommendation_text)


if __name__ == '__main__':
    app.run(debug=True)