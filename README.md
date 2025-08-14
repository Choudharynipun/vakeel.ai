# ⚖️ Vakeel.ai – Next-Generation Legal AI Platform

> **Private. Local. Intelligent.**  
> AI-powered legal document analysis, powered by LLaMA2-7B, OCR, and Retrieval-Augmented Generation — running entirely on your machine.

---

## 🚀 Overview

**Vakeel.ai** is a **privacy-first legal AI assistant** designed to analyze legal documents with cutting-edge AI technology — **without sending a single byte to the cloud**.  
Whether you're a lawyer, law student, or researcher, Vakeel.ai delivers fast, accurate, and contextual insights from your legal documents and a built-in legal knowledge base.

---

## ✨ Features

### 🔒 100% Local Processing
- Runs **LLaMA2-7B** model entirely on your machine.
- No cloud. No third parties. Your data stays with you.

### 📄 Multi-Format Document Support
- **PDF, JPG, PNG, TIFF, BMP** supported.
- Built-in **OCR engine** to handle both digital and scanned documents.
- **50MB file size limit**.

### 📚 RAG Pipeline with ChromaDB
- **Retrieval-Augmented Generation** for accurate, contextual answers.
- **BGE-M3 reranker** for enhanced semantic search.
- **Vector search** for meaning-based legal queries.

### ⚖️ Pre-Loaded Legal Knowledge Base
- bharatiya-nagarik-suraksha-sanhita-2023
- contract-act
- cpc-bare-act
- crpc-bare-act-1973
- dissolution-of-muslim-marriage-act
- hindu-adoption-and-maintenance-act
- negotiable-instruments-act-1881
- the-bharatiya-sakshya-adhiniyam-2023

### 🔍 Semantic Search
- Finds relevant legal precedents, clauses, and sections **based on meaning, not just keywords**.

### ⚡ Fast Response Time
- Optimized inference for **sub-2 second** responses.
- Includes **confidence scoring** and **source citations**.

---

## 🛠 How It Works

### **1. Upload Your Document**
- Drag & drop or browse to upload.
- Supported formats: **PDF, JPG, PNG, TIFF, BMP** (Max 50MB).
- OCR automatically processes scanned documents.

### **2. Ask Your Question**
- Ask about your document’s contents or general legal queries.
- The AI analyzes using the RAG pipeline + legal knowledge base.

### **3. Get AI-Powered Analysis**
- Detailed, accurate responses.
- **Source citations**, **confidence scores**, and **processing time** included.
- All processing happens **locally**.

---

## 📦 Tech Stack

| Component              | Technology Used |
|------------------------|-----------------|
| **LLM**               | LLaMA2-7B (optimized for local inference) |
| **Database**          | ChromaDB (vector store) |
| **Reranker**          | BGE-M3 |
| **OCR Engine**        | Tesseract / PaddleOCR |
| **Backend**           | Python (PyTorch, Transformers) |
| **Frontend**          | Web-based UI |

---

## 🔐 Privacy First

> Your documents never leave your machine.  
> Vakeel.ai is designed from the ground up for complete privacy and confidentiality.

---

## 📥 Installation

### Prerequisites
- Python 3.10+
- NVIDIA GPU (recommended) with CUDA support for best performance
- [Git](https://git-scm.com/)

### Steps
```bash
# Clone the repository
git clone https://github.com/Choudharynipun/vakeel.ai.git
cd vakeel.ai

# Install dependencies
pip install -r requirements.txt

# (Optional) Install GPU-accelerated PyTorch
pip install torch --index-url https://download.pytorch.org/whl/cu121

# Run the app
python app.py


🎯 Usage

Open the app in your browser.

Upload your legal document.

Ask questions or run legal queries.

Receive AI-powered, locally processed answers instantly.

📈 System Information Displayed in App

Status: Healthy/Unhealthy

Documents Loaded: X

Uptime

Model Parameters: 7B


Processing Speed: 

📬 Contact

Author: Nipun Choudhary
Email: nipunchoudhary44@gmail.com

🛡 License

© 2025 Nipun Choudhary. All rights reserved.

Disclaimer:
Vakeel.ai is designed for informational purposes only and does not constitute legal advice. Always consult a qualified lawyer for legal matters.
