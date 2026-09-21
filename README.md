# 🛒 ShopSphere — DevOps E-Commerce Platform

ShopSphere is a real-world **E-Commerce Backend + DevOps project** built to demonstrate practical Cloud and DevOps engineering skills.

## 🚀 Project Overview

ShopSphere provides:

* Product Management
* Product Search & Filtering
* Pagination & Sorting
* Inventory Management
* Low Stock Monitoring
* Inventory Risk Analysis
* Inventory Reports
* REST API using FastAPI
* React/Vite Dashboard
* Git & GitHub version control
* Automated CI using GitHub Actions

## 🏗️ Technology Stack

### Backend

* Python
* FastAPI
* SQLAlchemy
* Pydantic
* SQLite
* Uvicorn

### Frontend

* React
* Vite
* JavaScript
* CSS

### DevOps

* Git
* GitHub
* GitHub Actions
* CI/CD concepts
* Docker
* Kubernetes
* Terraform

## 📁 Project Structure

```text
shopsphere/
│
├── backend/
│   ├── main.py
│   ├── models.py
│   ├── schemas.py
│   ├── database.py
│   └── create_tables.py
│
├── frontend/
│   ├── src/
│   │   ├── App.jsx
│   │   └── App.css
│   ├── package.json
│   └── vite.config.js
│
├── .github/
│   └── workflows/
│       └── ci.yml
│
├── .gitignore
└── README.md
```

## 🔌 Backend API

The backend runs using FastAPI.

Local API:

```text
http://127.0.0.1:8000
```

Swagger API documentation:

```text
http://127.0.0.1:8000/docs
```

## 💻 Frontend

The React/Vite frontend runs locally at:

```text
http://localhost:5173
```

The dashboard provides:

* Dashboard
* Products
* Inventory
* Low Stock
* Risk Analysis
* Reports

## 📊 Inventory Analytics

ShopSphere includes inventory analytics such as:

* Total Products
* Total Stock
* Inventory Value
* Stock Risk Levels
* Critical Stock Detection
* High Risk Detection
* Medium Risk Detection
* Low Risk Detection
* Restocking Recommendations
* Inventory Risk Ranking

## 🔄 CI Pipeline

GitHub Actions automatically performs:

### Backend Check

* Checkout repository
* Setup Python
* Install dependencies
* Compile `main.py`

### Frontend Build

* Checkout repository
* Setup Node.js
* Install dependencies using `npm ci`
* Build React/Vite application

Workflow file:

```text
.github/workflows/ci.yml
```

## 🧪 CI Status

The GitHub Actions CI pipeline is configured for the `main` branch.

Every push and pull request to `main` triggers the CI workflow.

## 🛠️ Run Backend Locally

Open CMD:

```cmd
cd C:\Users\lenovo\OneDrive\Desktop\shopsphere\backend
```

Activate virtual environment:

```cmd
venv\Scripts\activate.bat
```

Start FastAPI:

```cmd
python -m uvicorn main:app --reload
```

## 🛠️ Run Frontend Locally

Open another CMD window:

```cmd
cd C:\Users\lenovo\OneDrive\Desktop\shopsphere\frontend
```

Install dependencies:

```cmd
npm install
```

Start frontend:

```cmd
npm run dev
```

## 🎯 DevOps Skills Demonstrated

This project demonstrates practical experience with:

* Linux/Windows command-line workflow
* Git
* GitHub
* Git branching concepts
* Version control
* REST APIs
* Backend development
* Frontend development
* CI pipelines
* GitHub Actions
* Automated builds
* Application testing
* Docker
* Kubernetes
* Terraform
* Cloud deployment concepts
* Infrastructure as Code
* Monitoring and operational thinking

## 📌 Project Goal

The goal of ShopSphere is to build a production-style application while learning how developers and DevOps engineers:

1. Build an application
2. Manage source code with Git
3. Push code to GitHub
4. Automate validation with CI
5. Containerize applications
6. Deploy applications
7. Manage infrastructure
8. Monitor application health

## 👨‍💻 Author

** MD Sameer **

ShopSphere — E-Commerce DevOps Project