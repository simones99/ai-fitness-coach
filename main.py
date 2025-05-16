from parser.csv_parser import parse_csv_file
from utils.stats_utils import analyze_workout_data, format_stats_for_ai
from model.recommender import ask_local_llm
import tkinter as tk
from tkinter import ttk, Tk, StringVar, Frame, filedialog, Radiobutton


def main():
    def proceed():
        file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
        if not file_path:
            print("❌ No file selected.")
            return

        try:
            workout_data = parse_csv_file(file_path)
            stats = analyze_workout_data(
                workout_data,
                user_gender=int(gender_var.get()),
                weight_kg=float(weight_kg_var.get()),
                height_cm=float(height_cm_var.get()),
                age=int(age_var.get())
            )
            print(f"Workout summary: {stats}")

            prompt = format_stats_for_ai(stats)
            print("\nAsking AI:\n", prompt)

            suggestion = ask_local_llm(prompt)
            print("\nSuggested workout:\n", suggestion)
        except Exception as e:
            print(f"Error during processing: {e}")

    root = Tk()
    root.title("Enter Your Info")

    age_var = StringVar()
    gender_var = StringVar(value="0")
    weight_kg_var = StringVar()
    height_cm_var = StringVar()

    frame = ttk.Frame(root, padding="10")
    frame.grid()

    tk.Label(frame, text="Gender:").grid(row=0, column=0, sticky="w")
    tk.Radiobutton(frame, text="Male", variable=gender_var, value="0").grid(row=0, column=1, sticky="w")
    tk.Radiobutton(frame, text="Female", variable=gender_var, value="1").grid(row=0, column=2, sticky="w")

    tk.Label(frame, text="Weight (kg):").grid(row=1, column=0, sticky="w")
    ttk.Entry(frame, width=10, textvariable=weight_kg_var).grid(row=1, column=1, columnspan=2, sticky="w")

    tk.Label(frame, text="Height (cm):").grid(row=2, column=0, sticky="w")
    ttk.Entry(frame, width=10, textvariable=height_cm_var).grid(row=2, column=1, columnspan=2, sticky="w")

    tk.Label(frame, text="Age:").grid(row=3, column=0, sticky="w")
    ttk.Entry(frame, width=10, textvariable=age_var).grid(row=3, column=1, columnspan=2, sticky="w")

    ttk.Button(frame, text="Continue", command=proceed).grid(row=4, column=0, columnspan=3, pady=10)

    root.mainloop()


if __name__ == "__main__":
    main()