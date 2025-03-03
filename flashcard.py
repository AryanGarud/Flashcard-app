import sqlite3
import tkinter as tk
from tkinter import messagebox, simpledialog, ttk
import logging
import pandas as pd

# Setup Logging
logging.basicConfig(filename="flashcard_logs.txt", level=logging.INFO, format="%(asctime)s - %(message)s")

# Database Setup
conn = sqlite3.connect("flashcards.db")
cursor = conn.cursor()
cursor.execute('''CREATE TABLE IF NOT EXISTS flashcards (id INTEGER PRIMARY KEY, question TEXT, answer TEXT)''')
cursor.execute('''CREATE TABLE IF NOT EXISTS quiz_results (id INTEGER PRIMARY KEY, score INTEGER, total INTEGER, date TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
conn.commit()

# Colors & Fonts
BG_COLOR = "#F8F9FA"
BTN_COLOR = "#4CAF50"
BTN_HOVER = "#45A049"
TEXT_COLOR = "#333333"
FONT = ("Arial", 12)

# Root Window
root = tk.Tk()
root.title("Flashcard App")
root.geometry("450x500")
root.config(bg=BG_COLOR)

# Function to style buttons
def create_button(master, text, command):
    btn = tk.Button(master, text=text, command=command, font=FONT, bg=BTN_COLOR, fg="white",
                    activebackground=BTN_HOVER, relief="flat", width=25, height=2)
    btn.pack(pady=5)
    return btn

# Flashcard Functions
def add_flashcard():
    add_window = tk.Toplevel(root)
    add_window.title("Add Flashcard")
    add_window.geometry("400x250")
    add_window.config(bg=BG_COLOR)

    tk.Label(add_window, text="Question:", font=FONT, bg=BG_COLOR).pack(pady=5)
    question_entry = tk.Entry(add_window, width=40, font=FONT)
    question_entry.pack(pady=5)

    tk.Label(add_window, text="Answer:", font=FONT, bg=BG_COLOR).pack(pady=5)
    answer_entry = tk.Entry(add_window, width=40, font=FONT)
    answer_entry.pack(pady=5)

    def save_flashcard():
        question = question_entry.get()
        answer = answer_entry.get()
        if question and answer:
            cursor.execute("INSERT INTO flashcards (question, answer) VALUES (?, ?)", (question, answer))
            conn.commit()
            logging.info(f"Added Flashcard: {question} -> {answer}")
            messagebox.showinfo("Success", "Flashcard added!")
            add_window.destroy()
        else:
            messagebox.showerror("Error", "Both fields are required!")

    create_button(add_window, "Save", save_flashcard)

def view_flashcards():
    view_window = tk.Toplevel(root)
    view_window.title("View Flashcards")
    view_window.geometry("400x300")
    view_window.config(bg=BG_COLOR)

    text_area = tk.Text(view_window, width=50, height=15, font=FONT, bg="white", fg=TEXT_COLOR)
    text_area.pack(pady=10)

    cursor.execute("SELECT * FROM flashcards")
    flashcards = cursor.fetchall()
    
    for fc in flashcards:
        text_area.insert(tk.END, f"{fc[0]}. {fc[1]} - {fc[2]}\n")

def delete_flashcard():
    delete_window = tk.Toplevel(root)
    delete_window.title("Delete Flashcard")
    delete_window.geometry("300x200")
    delete_window.config(bg=BG_COLOR)

    tk.Label(delete_window, text="Enter Flashcard ID:", font=FONT, bg=BG_COLOR).pack(pady=5)
    id_entry = tk.Entry(delete_window, font=FONT, width=20)
    id_entry.pack(pady=5)

    def delete():
        flash_id = id_entry.get()
        if flash_id.isdigit():
            cursor.execute("DELETE FROM flashcards WHERE id = ?", (flash_id,))
            conn.commit()
            logging.info(f"Deleted Flashcard ID: {flash_id}")
            messagebox.showinfo("Success", "Flashcard deleted!")
            delete_window.destroy()
        else:
            messagebox.showerror("Error", "Invalid ID!")

    create_button(delete_window, "Delete", delete)

# Quiz Functions
def start_quiz():
    cursor.execute("SELECT * FROM flashcards")
    flashcards = cursor.fetchall()
    if not flashcards:
        messagebox.showinfo("No Flashcards", "No flashcards available for quiz.")
        return

    quiz_window = tk.Toplevel(root)
    quiz_window.title("Quiz Mode")
    quiz_window.geometry("400x300")
    quiz_window.config(bg=BG_COLOR)

    score = 0
    index = 0

    question_label = tk.Label(quiz_window, text=flashcards[index][1], font=("Arial", 14, "bold"), bg=BG_COLOR, fg=TEXT_COLOR)
    question_label.pack(pady=10)

    answer_entry = tk.Entry(quiz_window, width=40, font=FONT)
    answer_entry.pack(pady=10)

    score_label = tk.Label(quiz_window, text=f"Score: {score}", font=FONT, bg=BG_COLOR, fg=TEXT_COLOR)
    score_label.pack(pady=10)

    def next_question():
        nonlocal index, score
        user_answer = answer_entry.get().strip().lower()
        correct_answer = flashcards[index][2].strip().lower()
        if user_answer == correct_answer:
            score += 1
        index += 1

        if index < len(flashcards):
            question_label.config(text=flashcards[index][1])
            answer_entry.delete(0, tk.END)
            score_label.config(text=f"Score: {score}")
        else:
            cursor.execute("INSERT INTO quiz_results (score, total) VALUES (?, ?)", (score, len(flashcards)))
            conn.commit()
            logging.info(f"Quiz Taken: Score {score}/{len(flashcards)}")
            messagebox.showinfo("Quiz Finished", f"Your Score: {score}/{len(flashcards)}")
            quiz_window.destroy()

    create_button(quiz_window, "Submit & Next", next_question)

# Reporting
def generate_report():
    df = pd.read_sql_query("SELECT * FROM quiz_results", conn)
    report = df.to_string(index=False) if not df.empty else "No quiz history yet."
    
    report_window = tk.Toplevel(root)
    report_window.title("Quiz Report")
    report_window.geometry("400x300")
    report_window.config(bg=BG_COLOR)

    text_area = tk.Text(report_window, width=50, height=15, font=FONT, bg="white", fg=TEXT_COLOR)
    text_area.pack(pady=10)
    text_area.insert(tk.END, report)

# GUI Components
tk.Label(root, text="📚 Flashcard App", font=("Arial", 16, "bold"), bg=BG_COLOR, fg=TEXT_COLOR).pack(pady=10)
create_button(root, "➕ Add Flashcard", add_flashcard)
create_button(root, "📖 View Flashcards", view_flashcards)
create_button(root, "🗑 Delete Flashcard", delete_flashcard)
create_button(root, "🎯 Start Quiz", start_quiz)
create_button(root, "📊 Generate Report", generate_report)
create_button(root, "❌ Exit", root.quit)

root.mainloop()
conn.close()
