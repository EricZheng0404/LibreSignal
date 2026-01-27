# LibreSignal 🚦

A practice framework for CodeSignal's Industry Coding Framework (ICF) assessments.

## 🎯 Purpose

This repository provides a realistic simulation environment to prepare for **CodeSignal's Industry Coding Framework (ICF)** assessments. It mirrors the actual test format with multi-level coding problems where each subsequent level builds upon the previous one.

## 💡 Inspiration

I've long observed that coding assessments—whether CodeSignal, LeetCode, or others—ultimately come down to **practice**. However, CodeSignal's platform doesn't offer practice tests that closely resemble their actual assessments.

After reading [How hackable are automated coding assessments?](https://yanirseroussi.com/2023/05/26/how-hackable-are-automated-coding-assessments/), I came to a deep realization: **CodeSignal is no different than the SAT**. More practice will definitively boost your score. This repo exists to fill that gap—giving you a realistic practice environment so you can walk into your assessment with confidence.

## 📊 Scoring & What You Need to Pass

### Score to Percentile Conversion

CodeSignal provides a [conversion table](https://support.codesignal.com/hc/en-us/articles/13260678794775-Converting-Historical-Coding-Score-Thresholds-to-Assessment-Score) to translate your score to a percentile ranking.

### My Experience

I passed the screening for a well-funded fintech startup with a score of **480**, which corresponds to the **82nd percentile**. Based on this, here's a general guideline:

| Score | Percentile | Likelihood of Passing |
|-------|------------|----------------------|
| < 450 | < 70% | May struggle with competitive companies |
| 480 | ~82% | Passed startup screening |
| **500+** | **~85%+** | **Safe target for most companies** |

**🎯 Aim for 500+ to confidently pass most company screenings.**

### 💡 Pro Tip: Modularity Matters

CodeSignal's ICF assessments evaluate **modularity** as a scoring factor. Demonstrate your understanding of **SOLID principles**:

- **Encapsulate your data in classes** — Don't just use dictionaries everywhere
- **Think about extensibility** — Each level builds on the previous one
- **Use proper OOP patterns** — Not only does this showcase your software engineering skills, but it makes Levels 3 and 4 significantly easier

For example, instead of storing account data in a simple dict, create an `Account` class with methods for deposit, withdraw, and transaction history. When you reach Level 3 (scheduled payments) and Level 4 (account merging), you'll thank yourself.

## 🚀 Usage

### Prerequisites

- Python 3.10+
- pip

### Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/LibreSignal.git
   cd LibreSignal
   ```

2. **Create a virtual environment** (recommended)
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On macOS/Linux
   # or
   .venv\Scripts\activate     # On Windows
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

### Implementing Your Solution

1. Navigate to the question folder (e.g., `Questions/bank_system/`)
2. Read the problem description in the level markdown files (`level1.md`, `level2.md`, etc.)
3. Implement your solution in `simulation.py`
4. **Start with Level 1 and progress sequentially** — just like the real test!

### Running Tests

Each level has its own test suite. Run tests for a specific level from the <u>**root directory**</u>:

```bash
# Test Level 1
pytest Questions/bank_system/test_bank_system.py::TestLevel1 -v

# Test Level 2
pytest Questions/bank_system/test_bank_system.py::TestLevel2 -v

# Test Level 3
pytest Questions/bank_system/test_bank_system.py::TestLevel3 -v

# Test Level 4
pytest Questions/bank_system/test_bank_system.py::TestLevel4 -v

# Run all tests
pytest Questions/bank_system/test_bank_system.py -v
```

## 📁 Project Structure

```
LibreSignal/
├── README.md
├── requirements.txt
└── Questions/
    └── bank_system/
        ├── level1.md          # Level 1 requirements
        ├── level2.md          # Level 2 requirements
        ├── level3.md          # Level 3 requirements
        ├── level4.md          # Level 4 requirements
        ├── simulation.py      # Your implementation goes here
        ├── simulation_solution.py  # Reference solution
        └── test_bank_system.py     # Test suite
```

## 📚 Official Documentation

For a deeper understanding of how CodeSignal's ICF works, refer to the official technical brief:

📄 [Industry Coding Skills Evaluation Framework Technical Brief](https://discover.codesignal.com/rs/659-AFH-023/images/Industry-Coding-Skills-Evaluation-Framework-CodeSignal-Skills-Evaluation-Lab-Short.pdf)

## ⏱️ Test Day Tips

1. **Read ALL levels first** — Understanding what's coming helps you design a modular solution from the start
2. **Don't over-engineer Level 1** — But do set up proper data structures
3. **Test frequently** — Run the test suite after implementing each method
4. **Manage your time** — ~70 minutes total, so roughly 15-20 min per level
5. **Partial credit exists** — If stuck on Level 4, make sure Levels 1-3 are solid

## 🤝 Contributing

Found a bug? Have a new question to add? Contributions are welcome!

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/new-question`)
3. Commit your changes (`git commit -m 'Add new question set'`)
4. Push to the branch (`git push origin feature/new-question`)
5. Open a Pull Request

## 📝 License

This project is open source and available under the [MIT License](LICENSE).

---

**Good luck with your assessment!** 🍀

*Remember: It's just practice. The more you do, the better you get.*

---

**Last Updated:** January 27, 2026  
*Made with ❤️ in Boston*
