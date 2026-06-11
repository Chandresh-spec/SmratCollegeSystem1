# Smart College System (SmratCollegeSystem1)

A comprehensive college management and learning platform powered by modern web technologies and Artificial Intelligence. This system bridges the gap between students and faculties by providing an intuitive platform for resource sharing, announcements, and AI-assisted learning.

## ✨ Key Features

### 1. Role-Based Access Control
* Distinct dashboards and functionalities for **Students** and **Teachers/Faculty**.
* Secure authentication system using Django REST Framework and JWT.

### 2. Lumi AI Assistant (RAG Chat)
* A smart AI tutor built directly into the platform.
* Teachers can upload PDF notes and study materials for their subjects.
* **Retrieval-Augmented Generation (RAG)**: The system extracts text from PDFs, chunks it, and indexes it using **FAISS** vector search. When a student asks a question, Lumi searches the notes and uses an LLM to generate an accurate, context-aware answer.

### 3. Anonymous Doubt Clearing
* Subject-specific chatrooms for every class.
* Students can ask questions using anonymous aliases, removing the fear of judgment and encouraging open participation.
* Teachers can reply to these doubts in real-time.

### 4. General AI Chat
* An integrated general-purpose AI chatbot for answering standard queries outside of the uploaded notes.

### 5. Resource Management
* Centralized hub for academic resources.
* Users can easily upload, manage, and download study materials (PDFs).

### 6. Notice Board System
* Digital notice board for college-wide announcements and important updates.

### 7. Academic Management
* Organizes learning materials based on Semesters, Subjects, and Faculties.

## 🛠️ Technology Stack

* **Backend**: Python, Django, Django REST Framework
* **Database**: PostgreSQL (Production) / SQLite (Development)
* **AI & Machine Learning**: 
  * `Transformers` & `Sentence-Transformers` (Hugging Face)
  * `FAISS` (Vector Database for RAG)
  * `PyPDF` (Document parsing)
  * `PyTorch`
* **Frontend**: HTML5, Vanilla CSS, JavaScript

## 🚀 Getting Started

### Prerequisites
* Python 3.9+
* pip (Python Package Installer)

### Installation
1. Clone the repository and navigate to the project directory:
   ```bash
   cd SmratCollegeSystem1
   ```
2. Create and activate a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows use: .venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Set up the environment variables (copy `.env.example` to `.env` and fill in the details).
5. Run database migrations:
   ```bash
   cd Home
   python manage.py makemigrations
   python manage.py migrate
   ```
6. Start the development server:
   ```bash
   python manage.py runserver
   ```
