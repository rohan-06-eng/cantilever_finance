import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import sqlite3
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# Helper function to get current date
def get_current_date():
    return datetime.now().strftime("%Y-%m-%d")

# Function to connect to the database
def connect_db():
    return sqlite3.connect('finance.db')

def create_tables():
    conn = connect_db()
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS income (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            amount REAL NOT NULL,
            source TEXT NOT NULL,
            date TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            amount REAL NOT NULL,
            category TEXT NOT NULL,
            date TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS savings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            amount REAL NOT NULL,
            date TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS goals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            description TEXT NOT NULL,
            target_amount REAL NOT NULL,
            target_date TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')
    conn.commit()
    conn.close()

# GUI Class
class FinanceApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Personal Finance Management System")
        create_tables()
        self.create_login_page()

    def create_login_page(self):
        self.clear_screen()
        frame = tk.Frame(self.root, padx=20, pady=20)
        frame.pack(pady=50)

        tk.Label(frame, text="Username", font=("Helvetica", 16)).pack(pady=10)
        self.username_entry = tk.Entry(frame, font=("Helvetica", 16), width=40)
        self.username_entry.pack(pady=5, padx=10)

        tk.Label(frame, text="Password", font=("Helvetica", 16)).pack(pady=10)
        self.password_entry = tk.Entry(frame, show="*", font=("Helvetica", 16), width=40)
        self.password_entry.pack(pady=5, padx=10)

        tk.Button(frame, text="Login", command=self.login, bg="#4CAF50", fg="white", font=("Helvetica", 14), width=25).pack(pady=10)
        tk.Button(frame, text="Register", command=self.register, bg="#2196F3", fg="white", font=("Helvetica", 14), width=25).pack(pady=5)

    def clear_screen(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    def login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()

        conn = connect_db()
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
        user = c.fetchone()
        conn.close()

        if user:
            self.user_id = user[0]
            self.create_main_dashboard()
        else:
            messagebox.showerror("Login Error", "Invalid username or password")

    def register(self):
        username = self.username_entry.get()
        password = self.password_entry.get()

        conn = connect_db()
        c = conn.cursor()
        try:
            c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
            conn.commit()
            messagebox.showinfo("Registration Successful", "You can now log in")
        except sqlite3.IntegrityError:
            messagebox.showerror("Registration Error", "Username already exists")
        conn.close()

    def create_main_dashboard(self):
        self.clear_screen()
        self.tab_control = ttk.Notebook(self.root)

        self.income_tab = ttk.Frame(self.tab_control)
        self.expenses_tab = ttk.Frame(self.tab_control)
        self.savings_tab = ttk.Frame(self.tab_control)
        self.report_tab = ttk.Frame(self.tab_control)
        self.goals_tab = ttk.Frame(self.tab_control)

        self.tab_control.add(self.income_tab, text='Income')
        self.tab_control.add(self.expenses_tab, text='Expenses')
        self.tab_control.add(self.savings_tab, text='Savings')
        self.tab_control.add(self.report_tab, text='Report')
        self.tab_control.add(self.goals_tab, text='Goals')

        self.tab_control.pack(expand=1, fill='both')

        self.create_income_tab()
        self.create_expenses_tab()
        self.create_savings_tab()
        self.create_report_tab()
        self.create_goals_tab()

    def create_income_tab(self):
        tk.Label(self.income_tab, text="Amount", font=("Helvetica", 14)).pack(pady=10)
        self.amount_entry_income = tk.Entry(self.income_tab, font=("Helvetica", 14), width=40)
        self.amount_entry_income.pack(pady=5, padx=10)

        tk.Label(self.income_tab, text="Source", font=("Helvetica", 14)).pack(pady=10)
        self.source_var = tk.StringVar(self.income_tab)
        self.source_var.set("Select Source")  # default value
        income_sources = [
            "Salary/Wages", "Bonuses", "Freelance/Contract Work", "Investments",
            "Rental Income", "Interest/Dividends", "Gifts/Grants", "Other Income"
        ]
        self.source_menu = tk.OptionMenu(self.income_tab, self.source_var, *income_sources)
        self.source_menu.config(font=("Helvetica", 14), width=40)
        self.source_menu.pack(pady=5, padx=10)

        tk.Label(self.income_tab, text="Date", font=("Helvetica", 14)).pack(pady=10)
        self.date_entry_income = tk.Entry(self.income_tab, font=("Helvetica", 14), width=40)
        self.date_entry_income.insert(0, get_current_date())
        self.date_entry_income.pack(pady=5, padx=10)

        tk.Button(self.income_tab, text="Add Income", command=self.add_income, bg="#4CAF50", fg="white", font=("Helvetica", 14), width=25).pack(pady=10)
        tk.Button(self.income_tab, text="Delete Selected", command=self.delete_income, bg="#F44336", fg="white", font=("Helvetica", 14), width=25).pack(pady=5)

        # Income Table
        columns = ("ID", "Amount", "Source", "Date")
        self.income_table = ttk.Treeview(self.income_tab, columns=columns, show='headings')
        for col in columns:
            self.income_table.heading(col, text=col)
            self.income_table.column(col, width=150, anchor='center')
        self.income_table.pack(pady=10, fill=tk.BOTH, expand=True)
        self.update_income_table()

    def create_expenses_tab(self):
        tk.Label(self.expenses_tab, text="Amount", font=("Helvetica", 14)).pack(pady=10)
        self.amount_entry_expense = tk.Entry(self.expenses_tab, font=("Helvetica", 14), width=40)
        self.amount_entry_expense.pack(pady=5, padx=10)

        tk.Label(self.expenses_tab, text="Category", font=("Helvetica", 14)).pack(pady=10)
        self.category_var = tk.StringVar(self.expenses_tab)
        self.category_var.set("Select Category")  # default value
        expense_categories = [
            "Housing", "Transportation", "Food", "Health", "Entertainment",
            "Education", "Personal Care", "Debt Payments", "Savings/Investments", "Miscellaneous"
        ]
        self.category_menu = tk.OptionMenu(self.expenses_tab, self.category_var, *expense_categories)
        self.category_menu.config(font=("Helvetica", 14), width=40)
        self.category_menu.pack(pady=5, padx=10)

        tk.Label(self.expenses_tab, text="Date", font=("Helvetica", 14)).pack(pady=10)
        self.date_entry_expense = tk.Entry(self.expenses_tab, font=("Helvetica", 14), width=40)
        self.date_entry_expense.insert(0, get_current_date())
        self.date_entry_expense.pack(pady=5, padx=10)

        tk.Button(self.expenses_tab, text="Add Expense", command=self.add_expense, bg="#F44336", fg="white", font=("Helvetica", 14), width=25).pack(pady=10)
        tk.Button(self.expenses_tab, text="Delete Selected", command=self.delete_expense, bg="#F44336", fg="white", font=("Helvetica", 14), width=25).pack(pady=5)

        # Expense Table
        columns = ("ID", "Amount", "Category", "Date")
        self.expense_table = ttk.Treeview(self.expenses_tab, columns=columns, show='headings')
        for col in columns:
            self.expense_table.heading(col, text=col)
            self.expense_table.column(col, width=150, anchor='center')
        self.expense_table.pack(pady=10, fill=tk.BOTH, expand=True)
        self.update_expense_table()

    def create_savings_tab(self):
        tk.Label(self.savings_tab, text="Amount", font=("Helvetica", 14)).pack(pady=10)
        self.amount_entry_saving = tk.Entry(self.savings_tab, font=("Helvetica", 14), width=40)
        self.amount_entry_saving.pack(pady=5, padx=10)

        tk.Label(self.savings_tab, text="Date", font=("Helvetica", 14)).pack(pady=10)
        self.date_entry_saving = tk.Entry(self.savings_tab, font=("Helvetica", 14), width=40)
        self.date_entry_saving.insert(0, get_current_date())
        self.date_entry_saving.pack(pady=5, padx=10)

        tk.Button(self.savings_tab, text="Add Saving", command=self.add_saving, bg="#4CAF50", fg="white", font=("Helvetica", 14), width=25).pack(pady=10)
        tk.Button(self.savings_tab, text="Delete Selected", command=self.delete_saving, bg="#F44336", fg="white", font=("Helvetica", 14), width=25).pack(pady=5)

        # Savings Table
        columns = ("ID", "Amount", "Date")
        self.saving_table = ttk.Treeview(self.savings_tab, columns=columns, show='headings')
        for col in columns:
            self.saving_table.heading(col, text=col)
            self.saving_table.column(col, width=150, anchor='center')
        self.saving_table.pack(pady=10, fill=tk.BOTH, expand=True)
        self.update_saving_table()

    def create_report_tab(self):
        tk.Label(self.report_tab, text="Income vs. Expense", font=("Helvetica", 16)).pack(pady=10)

        # Create a figure and axis for the pie chart
        fig, ax = plt.subplots(figsize=(8, 6), subplot_kw=dict(aspect="equal"))
        self.pie_chart_canvas = FigureCanvasTkAgg(fig, master=self.report_tab)
        self.pie_chart_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        self.update_pie_chart()

    def create_goals_tab(self):
        tk.Label(self.goals_tab, text="Set Your Financial Goals", font=("Helvetica", 16)).pack(pady=10)

        # Add placeholder for goals input
        tk.Label(self.goals_tab, text="Goal Description", font=("Helvetica", 14)).pack(pady=10)
        self.goal_entry = tk.Entry(self.goals_tab, font=("Helvetica", 14), width=40)
        self.goal_entry.pack(pady=5, padx=10)

        tk.Label(self.goals_tab, text="Target Amount", font=("Helvetica", 14)).pack(pady=10)
        self.target_amount_entry = tk.Entry(self.goals_tab, font=("Helvetica", 14), width=40)
        self.target_amount_entry.pack(pady=5, padx=10)

        tk.Label(self.goals_tab, text="Target Date", font=("Helvetica", 14)).pack(pady=10)
        self.target_date_entry = tk.Entry(self.goals_tab, font=("Helvetica", 14), width=40)
        self.target_date_entry.pack(pady=5, padx=10)
        self.target_date_entry.insert(0, get_current_date())

        tk.Button(self.goals_tab, text="Add Goal", command=self.add_goal, bg="#4CAF50", fg="white", font=("Helvetica", 14), width=25).pack(pady=10)

    def update_pie_chart(self):
        conn = connect_db()
        c = conn.cursor()

        # Get total income and expenses for pie chart
        c.execute("SELECT SUM(amount) FROM income WHERE user_id=?", (self.user_id,))
        total_income = c.fetchone()[0] or 0
        c.execute("SELECT SUM(amount) FROM expenses WHERE user_id=?", (self.user_id,))
        total_expenses = c.fetchone()[0] or 0

        conn.close()

        # Data for pie chart
        labels = 'Income', 'Expenses'
        sizes = [total_income, total_expenses]
        colors = ['#4CAF50', '#F44336']
        explode = (0.1, 0)  # explode 1st slice

        ax = self.pie_chart_canvas.figure.axes[0]
        ax.clear()
        ax.pie(sizes, explode=explode, labels=labels, colors=colors, autopct='%1.1f%%',
               shadow=True, startangle=140)
        ax.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.

        self.pie_chart_canvas.draw()

    def add_goal(self):
        description = self.goal_entry.get()
        target_amount = self.target_amount_entry.get()
        target_date = self.target_date_entry.get()

        if description and target_amount and target_date:
            conn = connect_db()
            c = conn.cursor()
            c.execute("INSERT INTO goals (user_id, description, target_amount, target_date) VALUES (?, ?, ?, ?)",
                      (self.user_id, description, target_amount, target_date))
            conn.commit()
            conn.close()
            messagebox.showinfo("Goal Added", "Your financial goal has been added")
        else:
            messagebox.showwarning("Input Error", "Please fill in all fields")

    # Database operations
    def add_income(self):
        amount = self.amount_entry_income.get()
        source = self.source_var.get()
        date = self.date_entry_income.get()

        if amount and source and date:
            conn = connect_db()
            c = conn.cursor()
            c.execute("INSERT INTO income (user_id, amount, source, date) VALUES (?, ?, ?, ?)", (self.user_id, amount, source, date))
            conn.commit()
            conn.close()
            self.update_income_table()
            self.update_pie_chart()
        else:
            messagebox.showwarning("Input Error", "Please fill in all fields")

    def add_expense(self):
        amount = self.amount_entry_expense.get()
        category = self.category_var.get()
        date = self.date_entry_expense.get()

        if amount and category and date:
            conn = connect_db()
            c = conn.cursor()
            c.execute("INSERT INTO expenses (user_id, amount, category, date) VALUES (?, ?, ?, ?)", (self.user_id, amount, category, date))
            conn.commit()
            conn.close()
            self.update_expense_table()
            self.update_pie_chart()
        else:
            messagebox.showwarning("Input Error", "Please fill in all fields")

    def add_saving(self):
        amount = self.amount_entry_saving.get()
        date = self.date_entry_saving.get()

        if amount and date:
            conn = connect_db()
            c = conn.cursor()
            c.execute("INSERT INTO savings (user_id, amount, date) VALUES (?, ?, ?)", (self.user_id, amount, date))
            conn.commit()
            conn.close()
            self.update_saving_table()
        else:
            messagebox.showwarning("Input Error", "Please fill in all fields")

    def delete_income(self):
        selected_item = self.income_table.selection()
        if selected_item:
            item_id = self.income_table.item(selected_item, 'values')[0]
            conn = connect_db()
            c = conn.cursor()
            c.execute("DELETE FROM income WHERE id=?", (item_id,))
            conn.commit()
            conn.close()
            self.update_income_table()
            self.update_pie_chart()
        else:
            messagebox.showwarning("Selection Error", "Please select an item to delete")

    def delete_expense(self):
        selected_item = self.expense_table.selection()
        if selected_item:
            item_id = self.expense_table.item(selected_item, 'values')[0]
            conn = connect_db()
            c = conn.cursor()
            c.execute("DELETE FROM expenses WHERE id=?", (item_id,))
            conn.commit()
            conn.close()
            self.update_expense_table()
            self.update_pie_chart()
        else:
            messagebox.showwarning("Selection Error", "Please select an item to delete")

    def delete_saving(self):
        selected_item = self.saving_table.selection()
        if selected_item:
            item_id = self.saving_table.item(selected_item, 'values')[0]
            conn = connect_db()
            c = conn.cursor()
            c.execute("DELETE FROM savings WHERE id=?", (item_id,))
            conn.commit()
            conn.close()
            self.update_saving_table()
        else:
            messagebox.showwarning("Selection Error", "Please select an item to delete")

    def update_income_table(self):
        for row in self.income_table.get_children():
            self.income_table.delete(row)

        conn = connect_db()
        c = conn.cursor()
        c.execute("SELECT id, amount, source, date FROM income WHERE user_id=?", (self.user_id,))
        rows = c.fetchall()
        conn.close()

        for row in rows:
            self.income_table.insert('', 'end', values=row)

    def update_expense_table(self):
        for row in self.expense_table.get_children():
            self.expense_table.delete(row)

        conn = connect_db()
        c = conn.cursor()
        c.execute("SELECT id, amount, category, date FROM expenses WHERE user_id=?", (self.user_id,))
        rows = c.fetchall()
        conn.close()

        for row in rows:
            self.expense_table.insert('', 'end', values=row)

    def update_saving_table(self):
        for row in self.saving_table.get_children():
            self.saving_table.delete(row)

        conn = connect_db()
        c = conn.cursor()
        c.execute("SELECT id, amount, date FROM savings WHERE user_id=?", (self.user_id,))
        rows = c.fetchall()
        conn.close()

        for row in rows:
            self.saving_table.insert('', 'end', values=row)

# Initialize the application
if __name__ == "__main__":
    root = tk.Tk()
    app = FinanceApp(root)
    root.mainloop()