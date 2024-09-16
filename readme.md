# Inventory Management System (IMS) - Purchase Order Workflow

This project is a fully functional **Inventory Management System (IMS)** with a **Purchase Order Workflow**. The web application was built using **React** for the frontend and **Flask** with a **SQLite** backend. It allows users to manage suppliers, create and track purchase orders, and manage inventory levels with ease. The goal of the project was to build an inventory system that facilitates the creation and management of purchase orders in a way that closely aligns with the workflows found in real-world Inventory Management Systems like ShipStation.

## Table of Contents

- [Project Goals](#project-goals)
- [Features](#features)
- [Technology Stack](#technology-stack)
- [Installation and Setup](#installation-and-setup)
- [Running the Application](#running-the-application)
- [Usage](#usage)
- [Future Enhancements](#future-enhancements)
- [License](#license)

---

## Project Goals

The primary objective of this project was to create a system that mirrors the purchase order workflows found in professional-grade IMS platforms like ShipStation. We aimed to build a user-friendly, responsive web application that allows users to:

- Manage suppliers.
- Create and duplicate purchase orders.
- Automatically handle purchase order approvals.
- Manage inventory levels.
- Generate PDF purchase orders for suppliers and send them via email.
- Reflect a modern and professional design, inspired by ShipStation's UI/UX.

---

## Features

### 1. **Supplier Management**
   - Add, view, and delete suppliers.
   - Store supplier contact information such as name, email, phone number, and address.

### 2. **Purchase Order Workflow**
   - Create purchase orders for multiple products.
   - Select existing suppliers or add new ones directly during the order process.
   - Duplicate existing purchase orders for faster workflow.
   - Automatically track approval status for purchase orders.
   - Generate PDF versions of the purchase orders and send them via email to suppliers.

### 3. **Inventory Management**
   - Manage product SKUs and inventory levels.
   - Set reorder points and automatic reordering thresholds.

### 4. **Comprehensive UI**
   - Built with Material-UI, with a theme inspired by ShipStation's color scheme.
   - Responsive design that works well across various devices.

### 5. **Notifications**
   - Email notifications for important events, such as order approval.

---

## Technology Stack

### Frontend:
- **React** with **Material-UI** for building the UI.
- **Axios** for making API requests to the backend.
- **Framer-Motion** for smooth animations.
- **React-Toastify** for in-app notifications.

### Backend:
- **Flask** as the web framework.
- **SQLite** as the database.
- **SQLAlchemy** for ORM (Object-Relational Mapping).
- **Flask-Mail** for sending email notifications.
- **ReportLab** for generating PDF documents.

---

## Installation and Setup

### Prerequisites
- [Node.js](https://nodejs.org/) (version 14.x or above)
- [Python 3.7+](https://www.python.org/)
- [pip](https://pip.pypa.io/en/stable/installing/)
- [Flask](https://flask.palletsprojects.com/en/2.0.x/installation/)

### 1. Clone the Repository

Setup
```bash
git clone https://github.com/your-username/inventory-management-system.git
cd inventory-management-system
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
cd ../frontend
npm install
```

Running The Application
```bash
flask db init
flask db migrate -m "Initial migration"
flask db upgrade
flask run

cd frontend
npm start
```


---

### **Explanation of the Structure:**
- **Project Goals**: Outlines the purpose and goal of the project.
- **Features**: Lists the key functionalities of the system.
- **Technology Stack**: Summarizes the technologies used in both the frontend and backend.
- **Installation and Setup**: Provides step-by-step instructions on how to set up and run the application.
- **Usage**: Explains how to use the different features of the application.
- **Future Enhancements**: Lists potential future improvements.
- **License**: Mentions the licensing information.

This `README.md` should help any developer or user get started with your project and understand its purpose and functionality.

Let me know if you'd like to add or modify any section!
