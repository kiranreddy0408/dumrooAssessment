# 🧠 Dumroo AI Admin Panel

An intelligent, role-based dashboard to **query educational insights using natural language**. Built for Dumroo's ethical and personalized education platform, this project leverages LLMs, FastAPI, PostgreSQL, and Streamlit to enable grade/class/region-scoped admins to ask simple questions and receive:
- SQL-powered answers
- Visualizations (Bar, Line, Pie, etc.)
- AI-generated insights


## 🔍 Key Features

- ✅ **Natural Language to SQL**: Ask plain English questions, get structured data.
- 📈 **Interactive Visualizations**: Bar, Pie, Line charts powered by **Plotly**.
- 💡 **AI-Generated Insights**: Summarized explanations for every query.
- 🔒 **Role-Based Access Control**: Admins see data only for assigned `grade`, `class`, and `region`.
- 🧠 **Query Memory**: View history of all past queries and visualizations.
- ⚡ **Built using FastAPI + LangChain + Gemini + Streamlit**.

---

## 🖼️ Interface Preview
<img width="2876" height="1629" alt="image" src="https://github.com/user-attachments/assets/f46c16d0-f25a-4af1-bb7b-9d63da5f3e97" />



---

## 🗂️ Tech Stack

| Layer       | Tech                                |
|-------------|-------------------------------------|
| Backend     | FastAPI, LangChain, SQLAlchemy      |
| LLM         | Google Gemini (LangChain Wrapper)   |
| Database    | PostgreSQL                          |
| Frontend UI | Streamlit                           |
| Charts      | Plotly (HTML Embed in Streamlit)    |

---

## 🚀 How to Run the Project

### ⚙️ 1. Clone the Repository

```bash
git clone https://github.com/your-username/dumroo-ai-admin.git
cd dumroo-ai-admin
```
### 🔧 2. Backend Setup (FastAPI)
```bash

cd backend
python -m venv venv
venv\Scripts\activate  # On Windows
pip install -r requirements.txt
```

### Setup Environment Variables
```bash
cp env .env
```
### Run FastAPI server
```bash
uvicorn main:app --reload
This will start FastAPI at: http://localhost:8000
```
### Insert dummy data
```bash
python db_insertion.py
```

### 🌐 3. Frontend Setup (Streamlit)
```bash
cd ../frontend
streamlit run ui.py
This opens the dashboard at: http://localhost:8501
```

## 🤖 Sample Queries to Try

⚠️ Ensure that admin_id=1 or a valid ID matching your region/class/grade is used.

📌 1. Show total number of quizzes and average score per subject for Grade 8

<img width="2879" height="1615" alt="image" src="https://github.com/user-attachments/assets/0239f7d9-76ec-44df-a00b-690fcec66a00" />


📌 2. Show the trend of average quiz scores in Math for Grade 10 over the past 4 weeks

<img width="2879" height="1630" alt="image" src="https://github.com/user-attachments/assets/9c6c7505-875e-4236-90be-672dd7e385bb" />


📌 3.  Compare the number of homework submissions vs. pending submissions for Grade 6

<img width="2879" height="1630" alt="image" src="https://github.com/user-attachments/assets/cfe85a79-48e2-4076-9964-807d87acca23" />


📂 Project Structure
```
dumroo-ai-admin/
├── backend/
│   ├── main.py
│   ├── models.py
│   ├── schemas.py
│   ├── db.py
│   ├── db_insertion.py
│   ├── services/
│   │   └── llm_agent.py
│   └── static/ (plotly charts)
│
├── frontend/
│   └── ui.py
│
├── .env
├── requirements.txt
└── README.md
```
