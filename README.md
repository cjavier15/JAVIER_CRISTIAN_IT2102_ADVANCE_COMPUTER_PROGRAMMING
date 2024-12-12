# Waste Management System
Final Project | Cristian Javier | Advance Computer Porgramming | IT-2102 

## I. Project Overview
The Waste Management System is a Python-based desktop application that facilitates effective waste management through features like:
- User and admin roles for different functionalities.
- Waste tracking and reporting.
- Viewing and solving waste-related issues.
- Community reporting of waste management problems.
- User registration and login system.

The application is built to streamline waste management processes, enhance community involvement, and promote sustainable waste practices.

---

## II. Python Concepts and Libraries Applied
The project leverages several Python concepts and libraries:

### Core Python Concepts
- **Object-Oriented Programming (OOP):** Used to create modular and reusable code through classes like `WasteManagementSystem`, `LoginFrame`, and others.
- **Database Management:** SQL queries are integrated with Python for data manipulation and retrieval.

### Libraries
- **CustomTkinter:** For creating a modern and responsive Graphical User Interface (GUI).
- **Pillow (PIL):** For handling image-related features, such as displaying segregation and recycling images.
- **pymysql:** For connecting and managing a MySQL database backend.
- **Datetime:** For managing and displaying time-related features, like report submission time.
- **Tabulate:** For formatting and displaying tabular data.
- **Calendar:** To display and navigate the waste collection schedule.

---

## III. Sustainable Development Goal (SDG)
### Chosen SDGs:

#### **Goal 11 - Sustainable Cities and Communities**
- Addressing improper waste management in communities.
- Encouraging citizen participation in reporting waste issues.
- Promoting recycling and proper waste segregation practices.

#### **Goal 6 - Clean Water and Sanitation**
- Reduces water contamination for water supplies in the community.
- Proper water consumption practices.
- Promoting water intake to be clean and safe.

#### **Goal 13 - Climate Action**
- Promotes actions that reduce waste-related carbon footprints.
- Encouraging citizen participation in caring for the planet.
- Encourages people to take more action in reducing waste pollution on the environment.

The application includes specific features like recycling tips, a segregation guide, and reporting functionality to engage users in sustainable waste practices.

---

## IV. Instructions for Running the Program
### Prerequisites
1. **Python Environment:** Ensure Python 3.8 or later is installed.
2. **Required Libraries:** Install the necessary Python libraries by running:
   ```bash
   pip install customtkinter pymysql Pillow tabulate
   ```
3. **Database Setup:**
   - Set up a MySQL database with the name `waste_managementDB`.
   - Import the required tables and schema from the provided SQL file (if available).
   - Update database connection credentials in the `connect_community_reports` function as needed.

### Running the Application
1. Navigate to the directory containing `management.py`.
2. Run the program:
   ```bash
   python management.py
   ```
3. The application will launch, displaying the login interface.

### User Guide
- **Admin Login:** Use the pre-configured admin credentials.
- **User Login/Registration:** Register as a new user or log in using existing credentials.
- **Key Functionalities:**
  - Community reporting
  - Viewing reports
  - Waste tracking
  - Progress report by the local government
  - User-friendly interface 

---

#Author
-[@cjavier15](https://github.com/cjavier15)


