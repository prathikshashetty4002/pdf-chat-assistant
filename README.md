# 📚 PDF Chat Assistant (GenAI)

A Streamlit-based application that allows users to chat with PDF documents using a large language model.

## 🚀 Features
- Upload any PDF
- Ask natural language questions
- Context-aware answers from document content
- Chat-style interface
- Built using LLM APIs and Streamlit

## 🛠 Tech Stack
- Python
- Streamlit
- PyPDF2
- Groq LLM API

## 📌 How it works
1. Extracts text from PDF
2. Splits text into chunks
3. Sends context + user query to LLM
4. Displays AI response in chat format

## ▶️ Run Locally
```bash
pip install -r requirements.txt
streamlit run app.py
