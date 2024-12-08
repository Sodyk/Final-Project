import tkinter as tk
from tkinter import ttk, filedialog
from database import add_rug, session, Rug, Customer
import datetime
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
from tkcalendar import DateEntry
from tkinter import messagebox

class MainWindow:
    def __init__(self, root):
        self.root = root
        self.root.title("Rug Store Tracker")

       
        columns = ("Customer", "Type", "Size", "Due Date", "Status", "Price", "Photo")
        self.tree = ttk.Treeview(root, columns=columns, show="headings")
        self.tree.heading("Customer", text="Customer")
        self.tree.heading("Type", text="Type")
        self.tree.heading("Size", text="Size")
        self.tree.heading("Due Date", text="Due Date")
        self.tree.heading("Status", text="Status")
        self.tree.heading("Price", text="Price ($)")
        self.tree.heading("Photo", text="Photo")
        self.tree.pack(fill=tk.BOTH, expand=True)

       
        self.tree.bind("<Double-1>", self.on_treeview_double_click)
        
        tk.Button(root, text="Add New Job", command=self.open_input_form).pack(side=tk.LEFT)
        tk.Button(root, text="Refresh", command=self.load_jobs).pack(side=tk.LEFT)
        tk.Button(root, text="Show Income and Job Trends", command=self.show_graphs).pack(side=tk.LEFT)

        self.create_search_frame()
        self.load_jobs()
        
       
    def open_analytics_window(self):
        AnalyticsWindow(self)
    
    def open_input_form(self):
        InputForm(self)

    def load_jobs(self):
        
        for row in self.tree.get_children():
            self.tree.delete(row)

      
        jobs = session.query(Rug).all()
        color = {"Not Ready": "gray", "Cleaning": "blue", "Ready": "green"}
        for job in jobs:
            self.tree.insert("", "end", text=job.id, values=(
                job.customer.name,
                job.type,
                job.size,
                job.due_date,
                job.status,
                job.price,
                job.photo_path
            ), tags=(color,))
        self.tree.tag_configure("gray", foreground="gray")
        self.tree.tag_configure("blue", foreground="blue")
        self.tree.tag_configure("green", foreground="green")
        
    def create_search_frame(self):
        search_frame = ttk.LabelFrame(self.root, text="Search by Customer", padding=10)
        search_frame.pack(fill=tk.X, pady=10)

        ttk.Label(search_frame, text="Customer Name:").pack(side=tk.LEFT, padx=5)
        self.search_var = tk.StringVar()
        ttk.Entry(search_frame, textvariable=self.search_var).pack(side=tk.LEFT, padx=5)

        search_button = ttk.Button(search_frame, text="Search", command=self.search_by_customer)
        search_button.pack(side=tk.LEFT, padx=10)

    def search_by_customer(self):
        customer_name = self.search_var.get()
        customers = session.query(Customer).filter(Customer.name.ilike(f"%{customer_name}%")).all()
        rugs = [rug for customer in customers for rug in customer.rugs]
        self.update_jobs_table(rugs)

    def on_treeview_double_click(self, event):
        selected_item = self.tree.selection()
        if selected_item:
            item = self.tree.item(selected_item)
            rug_id = item["text"]
            self.open_status_editor(rug_id)

    def open_status_editor(self, rug_id):
        rug = session.query(Rug).get(rug_id)
        if not rug:
            messagebox.showerror("Error", "Rug not found!")
            return

        editor_window = tk.Toplevel(self.root)
        editor_window.title("Update Status")

        ttk.Label(editor_window, text=f"Updating Status for Rug ID: {rug_id}").pack(pady=10)

        status_var = tk.StringVar(value=rug.status)
        status_dropdown = ttk.Combobox(
            editor_window,
            textvariable=status_var,
            values=["Not Ready", "Cleaning", "Ready"],
            state="readonly"
        )
        status_dropdown.pack(pady=10)

        def save_status():
            rug.status = status_var.get()
            session.commit()
            self.load_jobs()
            editor_window.destroy()

        ttk.Button(editor_window, text="Save", command=save_status).pack(pady=10)

  
    def update_jobs_table(self, jobs):
        for row in self.tree.get_children():
            self.tree.delete(row)

        for job in jobs:
            color = {"Not Ready": "gray", "Cleaning": "blue", "Ready": "green"}.get(job.status, "black")
            self.tree.insert("", "end", text=job.id, values=(
                job.customer.name,
                job.type,
                job.size,
                job.due_date,
                job.status,
                job.price,
                job.photo_path
            ), tags=(color,))
        
        self.tree.tag_configure("gray", foreground="gray")
        self.tree.tag_configure("blue", foreground="blue")
        self.tree.tag_configure("green", foreground="green")

    def show_graphs(self):
     
        jobs = session.query(Rug).all()

 
        data = {}
        for job in jobs:
            date = job.due_date
            if date not in data:
                data[date] = {"income": 0, "job_count": 0}
            data[date]["income"] += job.price
            data[date]["job_count"] += 1

        dates = sorted(data.keys())
        incomes = [data[date]["income"] for date in dates]
        job_counts = [data[date]["job_count"] for date in dates]

    
        graph_window = tk.Toplevel(self.root)
        graph_window.title("Income and Job Trends")

      
        figure, axes = plt.subplots(2, 1, figsize=(8, 6), sharex=True)

       
        axes[0].plot(dates, incomes, marker='o', color='green')
        axes[0].set_title("Income Per Day")
        axes[0].set_ylabel("Income ($)")
        axes[0].grid(True)

      
        axes[1].plot(dates, job_counts, marker='o', color='blue')
        axes[1].set_title("Number of Jobs Per Day")
        axes[1].set_xlabel("Date")
        axes[1].set_ylabel("Number of Jobs")
        axes[1].grid(True)

       
        canvas = FigureCanvasTkAgg(figure, master=graph_window)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

     
        tk.Button(graph_window, text="Close", command=graph_window.destroy).pack(pady=10)


class InputForm:
    def __init__(self, main_window):
        self.main_window = main_window

       
        self.window = tk.Toplevel(main_window.root)
        self.window.title("Add New Job")

     
        tk.Label(self.window, text="Customer Name").grid(row=0, column=0)
        self.customer_name = tk.Entry(self.window)
        self.customer_name.grid(row=0, column=1)

        tk.Label(self.window, text="Contact Info").grid(row=1, column=0)
        self.contact_info = tk.Entry(self.window)
        self.contact_info.grid(row=1, column=1)

        tk.Label(self.window, text="Rug Type").grid(row=2, column=0)
        self.rug_type = tk.Entry(self.window)
        self.rug_type.grid(row=2, column=1)

        tk.Label(self.window, text="Size").grid(row=3, column=0)
        self.size = tk.Entry(self.window)
        self.size.grid(row=3, column=1)

        tk.Label(self.window, text="Price").grid(row=4, column=0)
        self.price = tk.Entry(self.window)
        self.price.grid(row=4, column=1)

        tk.Label(self.window, text="Received Date (YYYY-MM-DD)").grid(row=5, column=0)
        self.received_date = tk.Entry(self.window)
        self.received_date.grid(row=5, column=1)

        tk.Label(self.window, text="Due Date (YYYY-MM-DD)").grid(row=6, column=0)
        self.due_date = tk.Entry(self.window)
        self.due_date.grid(row=6, column=1)

        tk.Label(self.window, text="Photo (Optional)").grid(row=7, column=0)
        self.photo_path = tk.Entry(self.window)
        self.photo_path.grid(row=7, column=1)
        tk.Button(self.window, text="Browse", command=self.browse_photo).grid(row=7, column=2)

        tk.Button(self.window, text="Add Job", command=self.add_job).grid(row=8, column=0, columnspan=2)

    def browse_photo(self):
        file_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.jpg *.png")])
        self.photo_path.insert(0, file_path)

    def add_job(self):
      
        add_rug(
            customer_name=self.customer_name.get(),
            contact_info=self.contact_info.get(),
            rug_type=self.rug_type.get(),
            size=self.size.get(),
            price=float(self.price.get()),
            received_date=datetime.datetime.strptime(self.received_date.get(), "%Y-%m-%d").date(),
            due_date=datetime.datetime.strptime(self.due_date.get(), "%Y-%m-%d").date(),
            photo_path=self.photo_path.get() if self.photo_path.get() else None
        )
        self.main_window.load_jobs()
        self.window.destroy()




if __name__ == "__main__":
    root = tk.Tk()
    app = MainWindow(root)
    root.mainloop()
