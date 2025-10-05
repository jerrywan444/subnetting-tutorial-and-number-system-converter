# 🧮 Number System + Network Visual Tutor  
### A Modern Educational GUI for Teaching Number Systems & Subnetting  
> _Built with Python, ttkbootstrap, and customtkinter — designed for clarity, simplicity, and visual learning._

---

## 📘 Overview

**Number System + Network Visual Tutor** is a modern, interactive Python desktop application that helps students **see** how number system conversions and IP subnetting actually work — step by step, visually, and in plain English.

It’s built for both **learners** and **teachers**, with animated explanations, Simple English mode, and exportable PDF handouts for classroom or self-study.

---

## 🌟 Features

### 🔢 Number System Converter
- Convert between **Decimal**, **Binary**, **Octal**, and **Hexadecimal**
- Step-by-step calculation breakdowns
- Toggle **Simple English Mode** for analogy-based explanations  
- Export conversion explanations as **PDF handouts**

### 🌐 Network Subnet Visual Tutor
- **IPv4 Subnet → Hosts** visual breakdown (bitwise AND animation)
- **Hosts → Subnet** calculator
- Visualized **network/broadcast/host** bit grouping
- Animated step-by-step logic
- **Replay**, **Speed**, and **Simple English Mode**
- **Export to PDF** for printable visual summaries  
- **IPv6-ready** (architecture supports future visualization)

---

## 🧠 Learning Modes

| Mode | Description |
|------|--------------|
| 💻 **Technical Mode** | Shows full binary breakdowns, bitwise AND/OR, and math logic |
| 🗣️ **Simple English Mode** | Converts logic into real-world analogies (“Subnet = Building, Hosts = Rooms”) |

---

## 🖥️ Tech Stack

| Component | Purpose |
|------------|----------|
| **Python 3.10+** | Core language |
| **ttkbootstrap** | Modern dark UI (Superhero theme) |
| **customtkinter** | Rounded, responsive widgets |
| **reportlab** | PDF generation |
| **Pillow** *(optional)* | For embedding visuals into exported PDFs |

---

## 🧩 Project Structure

Number-Network-Visual-Tutor/
│
├── main.py # Main GUI launcher
├── assets/ # Optional icons, images, and PDFs
├── README.md # This file
├── requirements.txt # Dependency list
└── LICENSE # MIT License file


---

## ⚙️ Installation

### 🐍 Requirements
```bash
Python 3.10+
pip install ttkbootstrap customtkinter reportlab pillow
python main.py

📄 Example Explanation Outputs
Decimal → Binary

Step 1: 25 ÷ 2 = 12 remainder 1
Step 2: 12 ÷ 2 = 6 remainder 0
Step 3: 6 ÷ 2 = 3 remainder 0
Step 4: 3 ÷ 2 = 1 remainder 1
Step 5: 1 ÷ 2 = 0 remainder 1
✅ Binary Result: 11001

Subnet Example
Input: 172.54.1.0/26

1) Prefix length: /26 → Host bits = 6  
2) Netmask: 255.255.255.192  
3) Network: 172.54.1.0  
4) Broadcast: 172.54.1.63  
5) Total hosts: 64, Usable: 62  
✅ First usable: 172.54.1.1 → Last usable: 172.54.1.62

💾 PDF Export Example

Teachers and students can generate a handout-style PDF of the explanation:

📄 Subnetting Steps for 172.54.1.0_26.pdf

Includes:

Step-by-step logic

Simple English explanations (if enabled)

Optional screenshot of the animation canvas"


🚀 Future Plans
| Feature                           | Status            |
| --------------------------------- | ----------------- |
| IPv6 Visualization                | 🔜 Planned        |
| Binary Arithmetic (Bitwise Tutor) | 🔜 Planned        |
| Step Replay Speed Slider          | ✅ Done            |
| Export to HTML                    | 🔜 Planned        |
| Classroom Quiz Mode               | 🧠 Research Stage |

💖 Credits

Built with passion by Ofori Akwasi, inspired by a mission to make technical education visual, friendly, and inclusive for everyone.

“If you can’t explain it simply, you don’t understand it well enough.”
— Albert Einstein

⭐ Show Your Support

If you find this project useful, please:

🌟 Star the repository

🍴 Fork it to share

💬 Give feedback or feature suggestions

Together, we can make computer science simpler, visual, and fun for everyone!
