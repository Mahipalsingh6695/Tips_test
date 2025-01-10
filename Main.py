import sqlite3
import json
from datetime import datetime
import streamlit as st
import os  # Added os import for platform checking and directory creation


def lock_screen():
    """Lock input to ensure users can't switch away (Windows only)."""
    if os.name == 'nt':  # If on Windows
        import ctypes
        ctypes.windll.user32.BlockInput(True)


def unlock_screen():
    """Unlock input when the quiz is over (Windows only)."""
    if os.name == 'nt':
        import ctypes
        ctypes.windll.user32.BlockInput(False)


# Database functions
def fetch_questions():
    conn = sqlite3.connect("test_exam.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id, question, option_a, option_b, option_c, option_d FROM questions")
    questions = cursor.fetchall()
    conn.close()
    return questions


def conduct_test(answers):
    conn = sqlite3.connect("test_exam.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id, correct_option FROM questions")
    correct_answers = {row[0]: row[1] for row in cursor.fetchall()}
    conn.close()

    score = 0
    for q_id, user_answer in answers.items():
        if correct_answers.get(q_id) == user_answer:
            score += 1

    return score, len(correct_answers)


def save_results(username, answers, score, total_questions):
    result_data = {
        "username": username,
        "score": score,
        "total_questions": total_questions,
        "answers": answers,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

    # Save the results to a file in the 'results' folder
    file_name = f"results/{username}_test_results.json"
    with open(file_name, "w") as f:
        json.dump(result_data, f, indent=4)

    return file_name


# Streamlit app with screen locking
def main():
    # Lock the screen initially
    lock_screen()

    st.title("Simple Test Exam System")
    st.warning("Input has been locked to prevent switching during the test. Complete the test to unlock!")

    username = st.text_input("Enter your name:", value="")

    if username:
        st.write(f"Welcome, {username}! Please answer the questions below.")

        questions = fetch_questions()
        user_answers = {}

        with st.form("test_form"):
            for q in questions:
                q_id, question, a, b, c, d = q
                st.write(f"### {question}")
                user_answers[q_id] = st.radio(
                    label=f"Options for Question {q_id}",
                    options=["a", "b", "c", "d"],
                    format_func=lambda x: {
                        "a": f"a) {a}",
                        "b": f"b) {b}",
                        "c": f"c) {c}",
                        "d": f"d) {d}"
                    }.get(x, x),
                    key=f"question_{q_id}"
                )

            submitted = st.form_submit_button("Submit Test")

            if submitted:
                score, total_questions = conduct_test(user_answers)
                save_results(username, user_answers, score, total_questions)

                # Unlock the screen after submission
                unlock_screen()

                st.success(f"Test completed! Your score: {score}/{total_questions}")
                st.write("Your answers have been saved locally.")
                st.info("The input has been unlocked. Thank you for completing the test!")


if __name__ == "__main__":
    # Ensure results folder exists
    if not os.path.exists("results"):
        os.mkdir("results")

    try:
        # Run the main function
        main()
    finally:
        # Ensure screen unlock even if there's an error
        unlock_screen()
