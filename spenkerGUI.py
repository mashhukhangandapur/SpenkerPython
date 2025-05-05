import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from tkcalendar import DateEntry

# ----------------- Database Setup -----------------
conn = sqlite3.connect("spenker.db")
cursor = conn.cursor()
cursor.execute('''
    CREATE TABLE IF NOT EXISTS expenses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        amount REAL,
        category TEXT,
        note TEXT,
        date TEXT
    )
''')
conn.commit()

# ----------------- GUI App -----------------
class ExpenseApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Spenker - Expense Tracker")
        self.root.geometry("600x750")
        self.root.config(bg="#1f1c2c")

        # Style setup
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TButton",
                        padding=6,
                        font=('Helvetica', 12, 'bold'),
                        background="#e94057",
                        foreground="white")
        style.map("TButton",
                  background=[("active", "#8a2387")])

        # Title & Total
        self.title = tk.Label(root, text="💸 Spenker", font=("Helvetica", 24, "bold"),
                              bg="#1f1c2c", fg="#ffffff")
        self.title.pack(pady=10)

        self.total_label = tk.Label(root, text="Total: ₹0.00", font=("Helvetica", 16),
                                    bg="#1f1c2c", fg="#f9f9f9")
        self.total_label.pack(pady=5)

        # Top Category Label
        self.top_category_label = tk.Label(root, text="", font=("Helvetica", 12, "italic"),
                                           bg="#1f1c2c", fg="#ffffff")
        self.top_category_label.pack(pady=5)

        # Entry Frame
        self.entry_frame = tk.Frame(root, bg="#2f2a45")
        self.entry_frame.pack(pady=20, padx=20, fill="x")

        # Entry fields
        self.amount_entry = self.create_entry("Amount (e.g. 150.50)")

        # Category Combobox with editable option
        self.category_var = tk.StringVar()
        self.category_combo = ttk.Combobox(self.entry_frame, textvariable=self.category_var, font=("Helvetica", 14))
        self.category_combo['values'] = ("Food", "Transport", "Health", "Utilities", "Entertainment", "Shopping", "Other")
        self.category_combo.set("Select or Type Category")
        self.category_combo.pack(pady=5, padx=10, fill="x")

        self.note_entry = self.create_entry("Note (optional)")

        # Date picker
        self.date_entry = DateEntry(self.entry_frame, date_pattern='yyyy-mm-dd', font=("Helvetica", 14))
        self.date_entry.pack(pady=5, padx=10, fill="x")

        # Button Frame (horizontal)
        self.button_frame = tk.Frame(self.entry_frame, bg="#2f2a45")
        self.button_frame.pack(pady=10)

        ttk.Button(self.button_frame, text="Add", command=self.add_expense).pack(side="left", padx=5)
        ttk.Button(self.button_frame, text="Update", command=self.update_expense).pack(side="left", padx=5)
        ttk.Button(self.button_frame, text="Delete Selected", command=self.delete_selected).pack(side="left", padx=5)
        ttk.Button(self.button_frame, text="Delete All", command=self.delete_all).pack(side="left", padx=5)

        # Treeview for expenses
        columns = ("Amount", "Category", "Date", "Note")
        self.tree = ttk.Treeview(root, columns=columns, show="headings", selectmode="browse")
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, anchor=tk.CENTER)

        self.tree.tag_configure("bold", font=("Helvetica", 11, "bold"))
        self.tree.tag_configure("hover", background="#554870")
        self.tree.bind("<Motion>", self.on_hover)
        self.tree.pack(padx=20, pady=10, fill="both", expand=True)

        self.last_hover = None
        self.update_expense_list()

    def create_entry(self, placeholder):
        entry = tk.Entry(self.entry_frame, font=("Helvetica", 14), fg='grey')
        entry.insert(0, placeholder)
        entry.bind("<FocusIn>", lambda e, ent=entry, ph=placeholder: self.clear_placeholder(ent, ph))
        entry.bind("<FocusOut>", lambda e, ent=entry, ph=placeholder: self.add_placeholder(ent, ph))
        entry.pack(pady=5, padx=10, fill="x")
        return entry

    def clear_placeholder(self, entry, placeholder):
        if entry.get() == placeholder:
            entry.delete(0, tk.END)
            entry.config(fg='black')

    def add_placeholder(self, entry, placeholder):
        if entry.get() == "":
            entry.insert(0, placeholder)
            entry.config(fg='grey')

    def on_hover(self, event):
        row_id = self.tree.identify_row(event.y)
        if self.last_hover != row_id:
            for item in self.tree.get_children():
                self.tree.item(item, tags=("bold",))
            if row_id:
                self.tree.item(row_id, tags=("bold", "hover"))
            self.last_hover = row_id

    def add_expense(self):
        try:
            amount_text = self.amount_entry.get()
            if amount_text in ("", "Amount (e.g. 150.50)"):
                amount = None
            else:
                amount = float(amount_text)

            category = self.category_var.get()
            note = self.note_entry.get()
            date = self.date_entry.get_date().strftime("%Y-%m-%d")

            if amount is None or category in ("", "Select or Type Category"):
                messagebox.showerror("Missing Info", "Please enter all required fields.")
                return

            if amount <= 0:
                messagebox.showerror("Invalid", "Amount must be a positive number.")
                return

            cursor.execute("INSERT INTO expenses (amount, category, note, date) VALUES (?, ?, ?, ?)",
                           (amount, category, note, date))
            conn.commit()
            self.clear_fields()
            self.update_expense_list()
        except ValueError:
            messagebox.showerror("Invalid", "Amount must be a number.")

    def update_expense(self):
        selected = self.tree.focus()
        if not selected:
            messagebox.showwarning("Select", "Please select an item to update.")
            return

        try:
            amount_text = self.amount_entry.get()
            if amount_text in ("", "Amount (e.g. 150.50)"):
                amount = None
            else:
                amount = float(amount_text)

            category = self.category_var.get()
            note = self.note_entry.get()
            date = self.date_entry.get_date().strftime("%Y-%m-%d")

            if amount is None or category in ("", "Select or Type Category"):
                messagebox.showerror("Missing Info", "Please enter all required fields.")
                return

            if amount <= 0:
                messagebox.showerror("Invalid", "Amount must be a positive number.")
                return

            cursor.execute("UPDATE expenses SET amount=?, category=?, note=?, date=? WHERE id=?",
                           (amount, category, note, date, selected))
            conn.commit()
            self.clear_fields()
            self.update_expense_list()
        except ValueError:
            messagebox.showerror("Invalid", "Amount must be a number.")

    def delete_selected(self):
        selected = self.tree.focus()
        if not selected:
            messagebox.showwarning("Select", "Please select an item to delete.")
            return

        if messagebox.askyesno("Confirm", "Are you sure you want to delete the selected expense?"):
            cursor.execute("DELETE FROM expenses WHERE id=?", (selected,))
            conn.commit()
            self.update_expense_list()

    def delete_all(self):
        if messagebox.askyesno("Confirm", "Delete ALL expenses?"):
            cursor.execute("DELETE FROM expenses")
            conn.commit()
            self.update_expense_list()

    def clear_fields(self):
        for entry, placeholder in [
            (self.amount_entry, "Amount (e.g. 150.50)"),
            (self.note_entry, "Note (optional)")
        ]:
            entry.delete(0, tk.END)
            entry.insert(0, placeholder)
            entry.config(fg='grey')

        self.category_combo.set("Select or Type Category")
        self.date_entry.set_date(self.date_entry._date.today())

    def update_expense_list(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        cursor.execute("SELECT id, amount, category, date, note FROM expenses ORDER BY id DESC")
        expenses = cursor.fetchall()

        total = 0
        for row in expenses:
            id, amount, category, date, note = row
            total += amount
            self.tree.insert("", "end", iid=id, values=(f"₹{amount:.2f}", category, date, note), tags=("bold",))

        self.total_label.config(text=f"Total: ₹{total:.2f}")

        # Update top category
        cursor.execute("SELECT category, SUM(amount) FROM expenses GROUP BY category ORDER BY SUM(amount) DESC LIMIT 1")
        top_category = cursor.fetchone()
        if top_category:
            top_cat_text = f"Most Spent On: {top_category[0]} (₹{top_category[1]:.2f})"
        else:
            top_cat_text = "No expenses recorded yet."

        self.top_category_label.config(text=top_cat_text)

# ------------------ Run App ------------------
if __name__ == "__main__":
    root = tk.Tk()
    app = ExpenseApp(root)
    root.mainloop()
