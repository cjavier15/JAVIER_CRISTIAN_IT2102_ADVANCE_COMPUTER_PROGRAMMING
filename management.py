import customtkinter as ctk
import pymysql
from datetime import datetime
from tkinter import messagebox
from PIL import Image, ImageTk
from tabulate import tabulate
import calendar
import os
from tkinter import ttk
import time 

def connect_community_reports():
    return pymysql.connect(
        host="localhost",
        user="root",
        password="",
        database="waste_managementDB"
    )

# Function to submit a report
def submit_report(report_type, report_location):
    try:
        conn = connect_community_reports()
        cursor = conn.cursor()
        report_time = datetime.now()
        cursor.execute(
            "INSERT INTO reports (report_type, report_location, report_time, status) VALUES (%s, %s, %s, 'pending')",
            (report_type, report_location, report_time)
        )
        conn.commit()
        messagebox.showinfo("Success", "Report submitted successfully!")
    except pymysql.MySQLError as err:
        messagebox.showerror("Database Error", f"Error: {err}")
    finally:
        conn.close()

# Function to view reports
def view_reports():
    conn = None
    try:
        conn = connect_community_reports()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM reports WHERE status='pending'")
        reports = cursor.fetchall()
        return reports
    except pymysql.MySQLError as err:
        messagebox.showerror("Database Error", f"Error: {err}")
        return []
    finally:
        if conn is not None:
            conn.close()

# Function to mark a report as solved
def solve_report(report_id):
    try:
        conn = connect_community_reports()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM reports WHERE id=%s", (report_id,))
        report = cursor.fetchone()
        
        if report:
            # Move the report to the solved_reports table
            solved_time = datetime.now()
            cursor.execute(
                "INSERT INTO solved_reports (report_type, report_location, report_time, solved_time) VALUES (%s, %s, %s, %s)",
                (report[1], report[2], report[3], solved_time)
            )
            conn.commit()
            
            # Update the report status to 'solved'
            cursor.execute("UPDATE reports SET status='solved' WHERE id=%s", (report_id,))
            conn.commit()
            
    except pymysql.MySQLError as err:
        messagebox.showerror("Database Error", f"Error: {err}")
    finally:
        conn.close()

class WasteManagementSystem:
    def __init__(self, root):
        self.root = root
        self.root.title("Waste Management System")
        self.root.geometry("800x600")
        self.current_user_role = None  # Track the current user's role
        self.history = []

        self.conn = connect_community_reports()
      
        # Initialize frames
        self.frames = {}
        self.current_frame = None

        self.setup_frames()
        self.display_frame("login")

    def setup_frames(self):
            self.frames["login"] = LoginFrame(self.root, self)
            self.frames["admin_dashboard"] = AdminDashboardFrame(self.root, self)
            self.frames["user_dashboard"] = UserDashboardFrame(self.root, self)
            self.frames["waste_tracking"] = WasteTrackingFrame(self.root, self)
            self.frames["register"] = RegistrationFrame(self.root, self)
            self.frames["community_reporting"] = CommunityReportingFrame(self.root, self)

    def display_frame(self, frame_name, data=None):
        if self.current_frame:
            self.current_frame.pack_forget()
            self.history.append(self.current_frame)

        self.current_frame = self.frames[frame_name]
        self.current_frame.pack(expand=True, fill='both', padx=20, pady=20)
        if hasattr(self.current_frame, 'setup') and data:
            self.current_frame.setup(data)

    def set_user_role(self, role):
        self.current_user_role = role  # Set the current user's role

    def logout(self):
        self.current_user_role = None  # Clear user role
        self.frames["login"].clear_input_fields()  # Clear input fields
        self.display_frame("login")  # Redirect to login frame

class LoginFrame(ctk.CTkFrame):
    def __init__(self, master, controller):
        super().__init__(master)
        self.controller = controller
        self.pack(expand=True, fill="both")
        self.pack_propagate(False)
        self.center_frame = ctk.CTkFrame(self)
        self.center_frame.place(relx=0.5, rely=0.5, anchor='center')
        self.setup_login_frame(controller)

    def setup_login_frame(self, controller):
        self.controller = controller

        # Create selection frame
        self.selection_frame = ctk.CTkFrame(self.center_frame)
        ctk.CTkLabel(self.selection_frame, text="Welcome to Waste Management System!", font=("Helvetica", 24)).pack(pady=10)
        ctk.CTkButton(self.selection_frame, text="Admin Login", command=self.display_admin_login).pack(pady=10)
        ctk.CTkButton(self.selection_frame, text="User Login", command=self.display_user_login).pack(pady=10)
        self.selection_frame.pack(pady=20, padx=20, expand=True)

        # Create frames for admin and user login
        self.admin_frame = ctk.CTkFrame(self.center_frame)
        self.user_frame = ctk.CTkFrame(self.center_frame)

        # Admin login components
        ctk.CTkLabel(self.admin_frame, text="Admin Login", font=("Helvetica", 18)).pack(pady=10)
        ctk.CTkLabel(self.admin_frame, text="Password:").pack()
        self.admin_password = ctk.CTkEntry(self.admin_frame, show="*")
        self.admin_password.pack()
        ctk.CTkButton(self.admin_frame, text="Login", command=self.process_admin_login).pack(pady=10)
        ctk.CTkButton(self.admin_frame, text="Back", command=self.display_selection).pack()

        # User login components
        ctk.CTkLabel(self.user_frame, text="User Login", font=("Helvetica", 18)).pack(pady=10)
        ctk.CTkLabel(self.user_frame, text="Username:").pack()
        self.username = ctk.CTkEntry(self.user_frame)
        self.username.pack()
        ctk.CTkLabel(self.user_frame, text="Password:").pack()
        self.password = ctk.CTkEntry(self.user_frame, show="*")
        self.password.pack()
        ctk.CTkButton(self.user_frame, text="Login", command=self.process_user_login).pack(pady=10)

        # Registration button
        ctk.CTkButton(self.user_frame, text="Register", command=lambda: self.controller.display_frame("register")).pack(pady=5)
        ctk.CTkButton(self.user_frame, text="Back", command=self.display_selection).pack()

    def clear_input_fields(self):
        self.admin_password.delete(0, ctk.END)  # Clear admin password field
        self.username.delete(0, ctk.END)  # Clear username field
        self.password.delete(0, ctk.END)  # Clear password field

    def display_selection(self):
        self.admin_frame.pack_forget()
        self.user_frame.pack_forget()
        self.selection_frame.pack()

    def display_admin_login(self):
        self.selection_frame.pack_forget()
        self.user_frame.pack_forget()
        self.admin_frame.pack(pady=20, padx=20, expand=True)

    def display_user_login(self):
        self.selection_frame.pack_forget()
        self.admin_frame.pack_forget()
        self.user_frame.pack(pady=20, padx=20, expand=True)

    def process_admin_login(self):
        if self.admin_password.get() == "admin":  # Replace with actual admin authentication
            messagebox.showinfo("Success", "Admin login successful!")
            self.controller.set_user_role("admin")  # Set role to admin
            self.controller.display_frame("admin_dashboard")  # Redirect to admin dashboard
        else:
            messagebox.showerror("Error", "Invalid admin password!")

    def process_user_login(self):
        username = self.username.get()
        password = self.password.get()

        cursor = self.controller.conn.cursor()
        try:
            cursor.execute("SELECT * FROM users WHERE username=%s AND password=%s", (username, password))
            user = cursor.fetchone()

            if user:
                messagebox.showinfo("Success", "User login successful!")
                self.controller.set_user_role("user")  # Set role to user
                self.controller.display_frame("user_dashboard")  # Redirect to user dashboard
            else:
                messagebox.showerror("Error", "Invalid credentials!")
        except pymysql.MySQLError as err:
            messagebox.showerror("Database Error", f"Error: {err}")
        finally:
            cursor.close()

class RegistrationFrame(ctk.CTkFrame):
    def __init__(self, master, controller):
        super().__init__(master)
        self.controller = controller
        self.setup_registration_frame()

    def setup_registration_frame(self):
        ctk.CTkLabel(self, text="Register", font=("Helvetica", 24)).pack(pady=10)
        
        # Username
        ctk.CTkLabel(self, text="Username:").pack()
        self.username = ctk.CTkEntry(self)
        self.username.pack()
        
        # Email
        ctk.CTkLabel(self, text="Email:").pack()
        self.email = ctk.CTkEntry(self)
        self.email.pack()
        
        # Password
        ctk.CTkLabel(self, text="Password:").pack()
        self.password = ctk.CTkEntry(self, show="*")
        self.password.pack()
        
        # Register button
        ctk.CTkButton(self, text="Register", command=self.process_registration).pack(pady=10)
        
        # Back to Login link
        ctk.CTkButton(self, text="Back to Login", command=lambda: self.controller.display_frame("login")).pack()

    def process_registration(self):
        username = self.username.get()
        email = self.email.get()
        password = self.password.get()
        
        cursor = self.controller.conn.cursor()
        try:
            cursor.execute("INSERT INTO users (username, email, password, role) VALUES (%s, %s, %s, 'user')",
                           (username, email, password))
            self.controller.conn.commit()
            messagebox.showinfo("Success", "Registration successful!")
            self.controller.display_frame("login")
        except pymysql.MySQLError:
            messagebox.showerror("Error", "Username already exists!")
        finally:
            cursor.close()

class DashboardFrame(ctk.CTkFrame):
    def setup_dashboard_frame(self, master, controller):
        super().__init__(master)
        self.controller = controller
        self.setup_dashboard_frame()
        
        ctk.CTkLabel(self, text="Dashboard", font=("Helvetica", 24)).pack(pady=10)
        
        # Add buttons for navigation
        ctk.CTkButton(self, text="Waste Tracking", 
                 command=lambda: controller.display_frame("waste_tracking")).pack(pady=5)
        ctk.CTkButton(self, text="Collection Schedule", 
                 command=lambda: controller.display_frame("schedule")).pack(pady=5)
        ctk.CTkButton(self, text="Segregation Guide", 
                 command=lambda: controller.display_frame("segregation")).pack(pady=5)
        ctk.CTkButton(self, text="Recycling", 
                 command=lambda: controller.display_frame("recycling")).pack(pady=5)
        ctk.CTkButton(self, text="Community Reporting", 
                 command=lambda: controller.display_frame("reporting")).pack(pady=5)

class WasteTrackingFrame(ctk.CTkFrame):
    def __init__(self, master, controller):
        super().__init__(master)
        self.controller = controller
        self.setup_waste_tracking_frame()

    def setup_waste_tracking_frame(self):
        ctk.CTkLabel(self, text="Waste Tracking", font=("Helvetica", 24)).pack(pady=10)

        # Add buttons for viewing reports
        ctk.CTkButton(self, text="View Current Reports", command=self.view_current_reports).pack(pady=5)
        ctk.CTkButton(self, text="View Solved Reports", command=self.view_solved_reports).pack(pady=5)

        # Back to Dashboard Button
        ctk.CTkButton(self, text="Back to Dashboard", command=lambda: self.controller.display_frame("user_dashboard")).pack(pady=5)

    def view_current_reports(self):
        reports = self.fetch_current_reports()  # Fetch current reports from the database
        self.display_reports(reports, "Current Reports")

    def view_solved_reports(self):
        solved_reports = self.fetch_solved_reports()  # Fetch solved reports from the database
        report_window = ctk.CTkToplevel(self)  # Create a new window for displaying reports
        report_window.title("Solved Reports")

        # Create a Treeview widget
        columns = ("Type", "Location", "Time", "Time Solved")
        tree = ttk.Treeview(report_window, columns=columns, show='headings')
        tree.pack(pady=10)

        # Define headings
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, anchor='center')

        # Insert data into the treeview
        for report in solved_reports:
            tree.insert("", "end", values=(report[1], report[2], report[3], report[4]))

        # Get the total count of solved reports
        total_count = self.get_solved_reports_count()

        # Create a label to display the total count
        total_count_label = ctk.CTkLabel(report_window, text=f"Total Solved Reports: {total_count}", font=("Helvetica", 16))
        total_count_label.pack(pady=10)

        # Add a scrollbar
        scrollbar = ttk.Scrollbar(report_window, orient="vertical", command=tree.yview)
        tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side='right', fill='y')

    def fetch_current_reports(self):
        conn = None
        try:
            conn = connect_community_reports()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM reports")  # Fetch all current reports
            return cursor.fetchall()
        except pymysql.MySQLError as err:
            messagebox.showerror("Database Error", f"Error: {err}")
            return []
        finally:
            if conn is not None:
                conn.close()

    def fetch_solved_reports(self):
        conn = None
        try:
            conn = connect_community_reports()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM solved_reports")  # Fetch all solved reports
            return cursor.fetchall()
        except pymysql.MySQLError as err:
            messagebox.showerror("Database Error", f"Error: {err}")
            return []
        finally:
            if conn is not None:
                conn.close()

    def display_reports(self, reports, title):
        report_window = ctk.CTkToplevel(self)  # Create a new window for displaying reports
        report_window.title(title)

        # Prepare data for tabulation
        headers = ["Type", "Location", "Time"]
        table = [list(report[1:]) for report in reports]  # Exclude the report ID

        # Create a label to display the formatted table
        report_label = ctk.CTkLabel(report_window, text=tabulate(table, headers, tablefmt="grid"))
        report_label.pack(pady=10)
            
        if title == "Current Reports":
            for report in reports:
                ctk.CTkButton(report_window, text="Mark as Solved", command=lambda r=report: self.solve_report(r[0], report_window)).pack()

    def get_solved_reports_count(self):
        conn = None
        try:
            conn = connect_community_reports()
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM solved_reports")  # Count all solved reports
            count = cursor.fetchone()[0]  # Fetch the count from the result
            return count
        except pymysql.MySQLError as err:
            messagebox.showerror("Database Error", f"Error: {err}")
            return 0
        finally:
            if conn is not None:
                conn.close()

class ScheduleFrame(ctk.CTkFrame):
    def setup_schedule_frame(self, master, controller):
        super().__init__(master)
        self.controller = controller
        self.setup_schedule_frame()
        
        ctk.CTkLabel(self, text="Schedule Frame", font=("Helvetica", 24)).pack(pady=10)
        
        # Add buttons for navigation
        ctk.CTkButton(self, text="Back to Dashboard", 
                 command=lambda: controller.display_frame("dashboard")).pack(pady=5)

class SegregationFrame(ctk.CTkFrame):
    def setup_segregation_frame(self, master, controller):
        super().__init__(master)
        self.controller = controller
        self.setup_segregation_frame()
        
        ctk.CTkLabel(self, text="Segregation Frame", font=("Helvetica", 24)).pack(pady=10)
        
        # Add buttons for navigation
        ctk.CTkButton(self, text="Back to Dashboard", 
                 command=lambda: controller.display_frame("dashboard")).pack(pady=5)

class RecyclingFrame(ctk.CTkFrame):
    def setup_recycling_frame(self, master, controller):
        super().__init__(master)
        self.controller = controller
        self.setup_recycling_frame()
        
        ctk.CTkLabel(self, text="Recycling Frame", font=("Helvetica", 24)).pack(pady=10)
        
        # Add buttons for navigation
        ctk.CTkButton(self, text="Back to Dashboard", 
                 command=lambda: controller.display_frame("dashboard")).pack(pady=5)

class CommunityReportingFrame(ctk.CTkFrame):
    def __init__(self, master, controller):
        super().__init__(master)
        self.controller = controller
        self.setup_community_reporting_frame()

    def setup_community_reporting_frame(self):
        ctk.CTkLabel(self, text="Community Reporting", font=("Helvetica", 24)).pack(pady=10)

        if self.controller.current_user_role == "user":
            # User report submission
            self.report_type_var = ctk.StringVar()
            self.report_location_var = ctk.StringVar()

            ctk.CTkLabel(self, text="Report Type:").pack()
            ctk.CTkOptionMenu(self, variable=self.report_type_var, values=["improper waste disposal", "waste overflow", "hazardous waste", "other reports"]).pack()

            ctk.CTkLabel(self, text="Report Location:").pack()
            ctk.CTkEntry(self, textvariable=self.report_location_var).pack()

            ctk.CTkButton(self, text="Submit Report", command=self.submit_report).pack(pady=5)
        else:
            ctk.CTkLabel(self, text="Admins cannot submit reports.").pack(pady=10)

        # Admin report management
        ctk.CTkButton(self, text="View Reports", command=self.view_reports).pack(pady=5)

    def submit_report(self):
        report_type = self.report_type_var.get()
        report_location = self.report_location_var.get()
        if report_type and report_location:
            submit_report(report_type, report_location)  # Call the function to submit the report
            messagebox.showinfo("Success", "Report submitted successfully!")
            self.prompt_next_action()
        else:
            messagebox.showerror("Error", "Please fill in all fields.")

    def prompt_next_action(self):
        if messagebox.askyesno("Continue", "Do you want to submit another report?"):
            self.report_type_var.set("")
            self.report_location_var.set("")
        else:
            self.controller.display_frame("user_dashboard")

    def view_reports(self):
        reports = view_reports()  # Call the function to retrieve reports
        for report in reports:
            # Display each report and provide a button to mark as solved
            report_frame = ctk.CTkFrame(self)
            report_frame.pack(pady=5)
            ctk.CTkLabel(report_frame, text=f"Type: {report[1]}, Location: {report[2]}, Time: {report[3]}").pack()
            ctk.CTkButton(report_frame, text="Mark as Solved", command=lambda r=report: self.solve_report(r[0])).pack()

    def solve_report(self, report_id):
        solve_report(report_id)  # Call the function to solve the report
        messagebox.showinfo("Success", "Report marked as solved!")
        self.view_reports()  # Refresh the report list

class UserDashboardFrame(ctk.CTkFrame):
    def __init__(self, master, controller):
        super().__init__(master)
        self.controller = controller
        self.setup_user_dashboard_frame(master, controller)
        
    def setup_user_dashboard_frame(self, parent, controller):
        self.controller = controller
        self.current_window = None
        
        ctk.CTkLabel(self, text="User Dashboard", font=("Helvetica", 24)).pack(pady=10)

        # Waste Tracking Section
        ctk.CTkButton(self, text="Waste Tracking", command=self.open_waste_tracking_options).pack(pady=5)

        # Collection Schedule Section
        ctk.CTkButton(self, text="Collection Schedule", command=self.open_collection_schedule).pack(pady=5)

        # Segregation Guide Section
        ctk.CTkButton(self, text="Segregation Guide", command=self.open_segregation_guide).pack(pady=5)

        # Recycling Section
        ctk.CTkButton(self, text="Recycling", command=self.open_recycling_window).pack(pady=5)

        # Community Reporting Section
        ctk.CTkLabel(self, text="Submit a Report", font=("Helvetica", 18)).pack(pady=10)
        self.report_type_var = ctk.StringVar()
        self.report_location_var = ctk.StringVar()

        ctk.CTkLabel(self, text="Report Type:").pack()
        ctk.CTkOptionMenu(self, variable=self.report_type_var, values=["improper waste disposal", "waste overflow", "hazardous waste", "other reports"]).pack()

        ctk.CTkLabel(self, text="Report Location:").pack()
        ctk.CTkEntry(self, textvariable=self.report_location_var).pack()

        ctk.CTkButton(self, text="Submit Report", command=self.submit_report).pack(pady=5)

        # Logout Button
        ctk.CTkButton(self, text="Logout", command=self.controller.logout).pack(pady=5)

    def open_waste_tracking_options(self):
        options_window = ctk.CTkToplevel(self)
        options_window.title("Waste Tracking Options")

        ctk.CTkLabel(options_window, text="Choose an option:", font=("Helvetica", 18)).pack(pady=10)

        ctk.CTkButton(options_window, text="View Current Reports", command=self.view_current_reports).pack(pady=5)

        ctk.CTkButton(options_window, text="View Solved Reports", command=self.view_solved_reports).pack(pady=5)

        ctk.CTkButton(options_window, text="Back", command=options_window.destroy).pack(pady=5)

    def view_current_reports(self):
        reports = self.fetch_current_reports()  # Fetch current reports from the database
        self.display_reports(reports, "Current Reports")

    def view_solved_reports(self):
        solved_reports = self.fetch_solved_reports()  # Fetch solved reports from the database
        report_window = ctk.CTkToplevel(self)
        report_window.title("Solved Reports")
        
        columns = ("Type", "Location", "Time", "Time Solved")
        tree = ttk.Treeview(report_window, columns=columns, show='headings')
        tree.pack(pady=10)

        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, anchor='center')

        for report in solved_reports:
            tree.insert("", "end", values=(report[1], report[2], report[3], report[4]))

        total_count = self.get_solved_reports_count()

        total_count_label = ctk.CTkLabel(report_window, text=f"Total Solved Reports: {total_count}", font=("Helvetica", 16))
        total_count_label.pack(pady=10)

        scrollbar = ttk.Scrollbar(report_window, orient="vertical", command=tree.yview)
        tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side='right', fill='y')

    def fetch_current_reports(self):
        conn = None
        try:
            conn = connect_community_reports()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM reports")  # Fetch all current reports
            return cursor.fetchall()
        except pymysql.MySQLError as err:
            messagebox.showerror("Database Error", f"Error: {err}")
            return []
        finally:
            if conn is not None:
                conn.close()

    def fetch_solved_reports(self):
        conn = None
        try:
            conn = connect_community_reports()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM solved_reports")  # Fetch all solved reports
            return cursor.fetchall()
        except pymysql.MySQLError as err:
            messagebox.showerror("Database Error", f"Error: {err}")
            return []
        finally:
            if conn is not None:
                conn.close()

    def get_solved_reports_count(self):
        conn = None
        try:
            conn = connect_community_reports()
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM solved_reports")
            return cursor.fetchone()[0]
        except pymysql.MySQLError as err:
            messagebox.showerror("Database Error", f"Error: {err}")
            return 0
        finally:
            if conn is not None:
                conn.close()

    def display_reports(self, reports, title):
        report_window = ctk.CTkToplevel(self)
        report_window.title(title)

        main_frame = ctk.CTkFrame(report_window)
        main_frame.pack(pady=10, padx=10, fill='x')

        if title == "Current Reports":
            columns = ("Type", "Location", "Time", "Status")
        else:
            columns = ("Type", "Location", "Time", "Time Solved")

        tree = ttk.Treeview(report_window, columns=columns, show='headings')
        tree.pack(pady=10)

        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, anchor='center')

        for report in reports:
            if title == "Current Reports":
                status = 'Pending'  # You can adjust this based on your logic
                tree.insert("", "end", values=(report[1], report[2], report[3], status))
            else:
                tree.insert("", "end", values=(report[1], report[2], report[3], report[4] if len(report) > 4 else ""))

        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=tree.yview)
        tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side='right', fill='y')

    def submit_report(self):
        report_type = self.report_type_var.get()
        report_location = self.report_location_var.get()
        if report_type and report_location:
            submit_report(report_type, report_location)  # Call the function to submit the report
            messagebox.showinfo("Success", "Report submitted successfully!")
            self.report_type_var.set("")  # Clear the input fields
            self.report_location_var.set("")
        else:
            messagebox.showerror("Error", "Please fill in all fields.")
    
    def open_collection_schedule(self):
        self.schedule_window = ctk.CTkToplevel(self)
        self.schedule_window.geometry("1000x650")

        self.current_month = datetime.now().month
        self.current_year = datetime.now().year

        button_frame = ctk.CTkFrame(self.schedule_window)
        button_frame.pack(side=ctk.TOP, fill=ctk.X, pady=20)

        previous_button = ctk.CTkButton(button_frame, text="Previous Month", command=self.previous_month)
        previous_button.pack(side=ctk.LEFT, padx=20, expand=True)

        next_button = ctk.CTkButton(button_frame, text="Next Month", command=self.next_month)
        next_button.pack(side=ctk.RIGHT, padx=20, expand=True)

        self.month_year_label = ctk.CTkLabel(self.schedule_window, font=("Helvetica", 24))
        self.month_year_label.pack(pady=20)

        self.schedule_frame = ctk.CTkFrame(self.schedule_window)
        self.schedule_frame.pack(pady=20)

        self.display_schedule()

        ctk.CTkLabel(self.schedule_window, text="Collection Time: 6 AM Onwards", font=("Helvetica", 20)).pack(pady=10)

    def display_schedule(self):
        for widget in self.schedule_frame.winfo_children():
            widget.destroy()

        self.month_year_label.configure(text=f"{calendar.month_name[self.current_month]} {self.current_year}")

        days_in_month = calendar.monthrange(self.current_year, self.current_month)[1]
        first_weekday = calendar.monthrange(self.current_year, self.current_month)[0]

        days_of_week = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        for day in days_of_week:
            ctk.CTkLabel(self.schedule_frame, text=day, font=("Helvetica", 18), width=100).grid(row=0, column=days_of_week.index(day), padx=10, pady=10)

        day_counter = 1
        for row in range(1, 7):
            for col in range(7):
                if row == 1 and col < first_weekday:
                    ctk.CTkLabel(self.schedule_frame, text="", width=100).grid(row=row, column=col, padx=10, pady=10)
                elif day_counter <= days_in_month:
                    day_label = ctk.CTkLabel(self.schedule_frame, text=str(day_counter), font=("Helvetica", 18), width=100, height=50)
                    if col in [0, 2, 4]:
                        day_label.configure(fg_color="grey")
                    day_label.grid(row=row, column=col, padx=10, pady=10)
                    day_counter += 1

    def previous_month(self):
        if self.current_month == 1:
            self.current_month = 12
            self.current_year -= 1
        else:
            self.current_month -= 1
        self.display_schedule()

    def next_month(self):
        if self.current_month == 12:
            self.current_month = 1
            self.current_year += 1
        else:
            self.current_month += 1
        self.display_schedule()

    def open_segregation_guide(self):
        guide_window = ctk.CTkToplevel(self)
        guide_window.title("Segregation Guide")

        image_path = os.path.join("gui", "segregation.png")
        try:
            image = Image.open(image_path)

            max_width = 800
            max_height = 600
            image.thumbnail((max_width, max_height), Image.LANCZOS)

            photo = ImageTk.PhotoImage(image)

            image_label = ctk.CTkLabel(guide_window, image=photo)
            image_label.image = photo
            image_label.pack()

        except Exception as e:
            messagebox.showerror("Error", f"Could not load image: {e}")

    def open_recycling_window(self):
        recycling_window = ctk.CTkToplevel(self)
        recycling_window.title("Recycling Tips")

        recycling_image_path = os.path.join("gui", "recycling.png")
        try:
            recycling_image = Image.open(recycling_image_path)

            max_width = 800
            max_height = 600
            recycling_image.thumbnail((max_width, max_height), Image.LANCZOS)

            recycling_photo = ImageTk.PhotoImage(recycling_image)

            recycling_label = ctk.CTkLabel(recycling_window, image=recycling_photo)
            recycling_label.image = recycling_photo
            recycling_label.pack()

            ready_button = ctk.CTkButton(recycling_window, text="Ready to Recycle?", command=self.show_recycling_options)
            ready_button.pack(pady=10)

        except Exception as e:
            messagebox.showerror("Error", f"Could not load recycling image: {e}")
    
    def show_recycling_options(self):
        options_window = ctk.CTkToplevel(self)
        options_window.title("Recycling Options")

        ctk.CTkLabel(options_window, text="Let us Recycle for a Better Tomorrow!", font=("Helvetica", 18)).pack(pady=10)
        ctk.CTkLabel(options_window, text="Please choose below what to create and save the environment!", font=("Helvetica", 14)).pack(pady=5)

        items = [
            {
                "name": "Bottle Cap Planter",
                "image": "Bottle Cap Planter.png",
                "images": ["BC2.png", "BC3.png", "BC4.png", "BC5.png"],
                "description": (
                    "What you'll need:\n"
                    "- An empty metal container; a coffee canister, tin etc\n"
                    "- Bottle caps collected from glass bottles of beer, cider etc. How many you need will depend on the size of your container\n"
                    "- A hot glue gun and glue\n"
                    "- Spray paint\n\n"
                    "Steps:\n"
                    "- Make sure your metal container and bottle caps are clean and dry.\n"
                    "- Starting at the bottom, simply fix the bottle caps to the container with hot glue. I used the join on the back on my container to line them up.\n"
                    "- Once all the bottle caps are fixed on and the glue is dry you can spray the planter any colour you like."
                )
            },
            {
                "name": "Book Page Gift Bags",
                "image": "Book Page Gift Bags.png",
                "images": ["BP2.png", "BP3.png", "BP4.png", "BP5.png"],
                "description": (
                    "What you'll need:\n"
                    "- An old damaged book\n"
                    "- Scissors or a guillotine\n"
                    "- Stamps in Christmassy designs and Ink\n"
                    "- A sewing machine and thread\n"
                    "- Alphabet stamps - for personalisation\n"
                    "- A hole punch\n"
                    "- Ribbon\n\n"
                    "Steps:\n"
                    "- Trim 2 pages to the size you want with scissors or the guillotine and then sew around 3 sides leaving the top open.\n"
                    "- Next, stamp a design on the bag, you can do just one or two but you can cover the whole thing if that takes your fancy.\n"
                    "- Take the hole punch and punch two holes at the top of the bag.\n"
                    "- Pop the gift in and then seal the bag by threading a length of ribbon through the holes and tying in a bow. And you are done!"
                )
            },

            {
                "name": "T-shirt Gift Bag",
                "image": "T-Shirt Gift Bag.png",
                "images": ["GB2.png", "GB3.png", "GB4.png", "GB5.png", "GB6.png"],
                "description": (
                    "What you'll need:\n"
                    "- An old T Shirt\n"
                    "- Scissors\n"
                    "- A sewing machine and thread\n"
                    "- Ribbon\n\n"
                    "Steps:\n"
                    "- Cut a rectangle from the 'good' section of the shirt. - You want to remove the neck and sleeves and any part that is damaged or holey. You are cutting through both layers of fabric.\n"
                    "- Place your 2 pieces of fabric right sides together and pin in place. Use A LOT of pins. T shirt fabric tends to move and stretch so a lot of pins will really help with this.\n"
                    "- Stitch around 3 sides, leaving the top edge open. Remember to do a few back stitches at the beginning and end of your stitches to make it secure.\n"
                    "- Turn the bag the right way out and that's it - you're done already! \n"
                    "- Pop your gift inside and tie the top with a length of ribbon."
                )
            }
        ]

        max_size = (200, 200)

        for item in items:
            frame = ctk.CTkFrame(options_window)
            frame.pack(side=ctk.LEFT, padx=10, pady=10)

            item_image_path = os.path.join("gui", item["image"])
            try:
                item_image = Image.open(item_image_path)
                item_image.thumbnail(max_size)
                item_photo = ImageTk.PhotoImage(item_image)

                item_label = ctk.CTkLabel(frame, image=item_photo)
                item_label.image = item_photo
                item_label.pack()

                create_button = ctk.CTkButton(frame, text=f"Create {item['name']}", command=lambda i=item: self.create_item(i))
                create_button.pack(pady=5)

            except Exception as e:
                messagebox.showerror("Error", f"Could not load image {item_image_path}: {e}")

    def create_item(self, item):
        creation_window = ctk.CTkToplevel(self)
        creation_window.title(f"Create {item['name']}")

        self.show_creation_steps(creation_window, item["images"], item["description"])

    def show_creation_steps(self, window, image_names, description):
        description_frame = ctk.CTkFrame(window)
        description_frame.pack(pady=10)

        description_label = ctk.CTkLabel(description_frame, text=description, justify=ctk.LEFT)
        description_label.pack()

        image_frame = ctk.CTkFrame(window)
        image_frame.pack(pady=10)

        max_size = (200, 200)

        for image_name in image_names:
            image_path = os.path.join("gui", image_name)
            try:
                image = Image.open(image_path)
                image.thumbnail(max_size)
                photo = ImageTk.PhotoImage(image)

                image_label = ctk.CTkLabel(image_frame, image=photo)
                image_label.image = photo
                image_label.pack(side=ctk.LEFT, padx=5)

            except Exception as e:
                messagebox.showerror("Error", f"Could not load image {image_name}: {e}")

        finish_button = ctk.CTkButton(window, text="Finish", command=window.destroy)
        finish_button.pack(pady=10)

def process_user_login(self):
    username = self.username.get()
    password = self.password.get()

    cursor = self.controller.conn.cursor()
    try:
        cursor.execute("SELECT * FROM users WHERE username=%s AND password=%s", (username, password))
        user = cursor.fetchone()

        if user:
            messagebox.showinfo("Success", "User login successful!")
            self.controller.set_user_role("user")  # Set role to user
            self.controller.display_frame("user_dashboard")  # Redirect to user dashboard
        else:
            messagebox.showerror("Error", "Invalid credentials!")
    except pymysql.MySQLError as err:
        messagebox.showerror("Database Error", f"Error: {err}")
    finally:
        cursor.close()

def logout(self):
    self.controller.set_user_role(None)  # Clear user role
    self.controller.frames["login"].clear_input_fields()  # Clear input fields
    self.controller.display_frame("login")  # Redirect to login frame

class AdminDashboardFrame(ctk.CTkFrame):
    def __init__(self, master, controller):
        super().__init__(master)
        self.controller = controller
        self.setup_admin_dashboard_frame()

    def setup_admin_dashboard_frame(self):
        ctk.CTkLabel(self, text="Admin Dashboard", font=("Helvetica", 24)).pack(pady=10)

        ctk.CTkButton(self, text="View Current Reports", command=self.view_current_reports).pack(pady=5)

        ctk.CTkButton(self, text="View Solved Reports", command=self.view_solved_reports).pack(pady=5)

        ctk.CTkButton(self, text="Logout", command=self.logout).pack(pady=5)

    def view_current_reports(self):
        reports = self.fetch_current_reports()  # Fetch current reports from the database
        self.display_reports(reports, "Current Reports")

    def view_solved_reports(self):
        solved_reports = self.fetch_solved_reports()  # Fetch solved reports from the database
        self.display_solved_reports(solved_reports)

    def fetch_current_reports(self):
        conn = None
        try:
            conn = connect_community_reports()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM reports WHERE status != 'solved'")  # Fetch all current (not solved) reports
            return cursor.fetchall()
        except pymysql.MySQLError as err:
            messagebox.showerror("Database Error", f"Error: {err}")
            return []
        finally:
            if conn is not None:
                conn.close()

    def fetch_solved_reports(self):
        conn = None
        try:
            conn = connect_community_reports()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM solved_reports")  # Fetch all solved reports
            return cursor.fetchall()
        except pymysql.MySQLError as err:
            messagebox.showerror("Database Error", f"Error: {err}")
            return []
        finally:
            if conn is not None:
                conn.close()

    def get_solved_reports_count(self):
        conn = None
        try:
            conn = connect_community_reports()
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM solved_reports")
            return cursor.fetchone()[0]
        except pymysql.MySQLError as err:
            messagebox.showerror("Database Error", f"Error: {err}")
            return 0
        finally:
            if conn is not None:
                conn.close()

    def display_reports(self, reports, title):
        report_window = ctk.CTkToplevel(self)  # Create a new window for displaying reports
        report_window.title(title)

        main_frame = ctk.CTkFrame(report_window)
        main_frame.pack(pady=10, padx=10, fill='x')

        if title == "Current Reports":
            columns = ("Report ID", "Type", "Location", "Time", "Status")
        else:
            columns = ("Type", "Location", "Time", "Time Solved")

        tree = ttk.Treeview(main_frame, columns=columns, show='headings')
        tree.pack(side='left', fill='both', expand=True)

        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, anchor='center')

        for report in reports:
            if title == "Current Reports":
                status = 'Pending' if report[4] != 'solved' else 'Solved'
                tree.insert("", "end", values=(report[0], report[1], report[2], report[3], status))
            else:
                tree.insert("", "end", values=(report[1], report[2], report[3], report[4] if len(report) > 4 else ""))

        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=tree.yview)
        tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side='right', fill='y')

        if title == "Current Reports":
            tree.bind("<Double-1>", lambda event: self.change_status(tree, event))

        done_button = ctk.CTkButton(report_window, text="Done", command=lambda: self.update_solved_reports(tree, report_window))
        done_button.pack(pady=10)

    def change_status(self, tree, event):
        selected_item = tree.focus()
        values = tree.item(selected_item, 'values')
        if values and values[4] == 'Pending':
            new_values = list(values)
            new_values[4] = 'Solved'
            tree.item(selected_item, values=new_values)

    def update_solved_reports(self, tree, report_window):
        for item_id in tree.get_children():
            values = tree.item(item_id, 'values')
            if values[4] == 'Solved':
                self.solve_report(values[0])

        report_window.destroy()
        self.view_current_reports()

    def display_solved_reports(self, solved_reports):
        report_window = ctk.CTkToplevel(self)
        report_window.title("Solved Reports")
        
        columns = ("Type", "Location", "Time", "Time Solved")
        tree = ttk.Treeview(report_window, columns=columns, show='headings')
        tree.pack(pady=10)

        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, anchor='center')

        for report in solved_reports:
            tree.insert("", "end", values=(report[1], report[2], report[3], report[4]))

        total_count = self.get_solved_reports_count()

        total_count_label = ctk.CTkLabel(report_window, text=f"Total Solved Reports: {total_count}", font=("Helvetica", 16))
        total_count_label.pack(pady=10)

        scrollbar = ttk.Scrollbar(report_window, orient="vertical", command=tree.yview)
        tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side='right', fill='y')

    def solve_report(self, report_id):
        try:
            conn = connect_community_reports()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM reports WHERE report_id=%s", (report_id,))
            report = cursor.fetchone()

            if report:
                solved_time = datetime.now()
                cursor.execute(
                    "INSERT INTO solved_reports (report_type, report_location, report_time, solved_time) VALUES (%s, %s, %s, %s)",
                    (report[1], report[2], report[3], solved_time)
                )
                conn.commit()

                cursor.execute("DELETE FROM reports WHERE report_id=%s", (report_id,))
                conn.commit()

                messagebox.showinfo("Success", "Report marked as solved!")
        except pymysql.MySQLError as err:
            messagebox.showerror("Database Error", f"Error: {err}")
        finally:
            if conn is not None:
                conn.close()

    def logout(self):
        self.controller.set_user_role(None)
        self.controller.frames["login"].clear_input_fields()
        self.controller.display_frame("login")

if __name__ == "__main__":
    print("\n==============================")
    print("\n Starting the application...")
    print("\n==============================")
    time.sleep(3)
    root = ctk.CTk()
    app = WasteManagementSystem(root)
    root.mainloop()
