# Smart Excel AI Automation Assistant 🚀

> **B.Tech Computer Science & Artificial Intelligence Capstone Project**  
> An intelligent, machine learning-powered spreadsheet automation assistant that enables natural language Excel editing, automated data cleaning with Isolation Forest anomaly detection, and end-to-end predictive machine learning pipelines.

---

## 📌 1. Project Title
**Smart Excel AI Automation Assistant**

---

## ❓ 2. Problem Statement
In traditional spreadsheet workflows, updating specific data entries across complex Excel workbooks requires users to:
1. Manually open large `.xlsx` or `.xls` files.
2. Search through multiple sheets and locate column/row indices manually.
3. Replace entries cell by cell, raising the risk of accidental overwrites, formatting corruption, or typos.
4. Manually identify data quality anomalies (missing entries, duplicates, irregular casing, numerical outliers).
5. Export data to external tools to train basic predictive machine learning models.

This workflow is time-consuming, prone to human error, and inaccessible to non-technical users.

---

## 💡 3. Proposed Solution
The **Smart Excel AI Automation Assistant** bridges the gap between natural language interaction and spreadsheet management. Users can upload any Excel/CSV dataset and type instructions such as:

> *"Change the department of student 1025 to Artificial Intelligence."*

The application automatically parses the intent, matches informal column names using hybrid TF-IDF and fuzzy matching, locates the exact row record, presents a visual diff preview, and updates the cell after user confirmation—**without ever overwriting the original file**.

Additionally, it features an **Intelligent Data Cleaner** powered by Scikit-Learn's **Isolation Forest** and an **ML Analyzer & Predictor** for automated regression and classification model training.

---

## ✨ 4. Key Features
- 🗣️ **Natural Language Cell Editing**: Enter plain English queries to locate and modify entries.
- 🎯 **Fuzzy Header Resolution**: Maps terms like `"dept"`, `"salary"`, or `"phone"` to exact spreadsheet headers (`"Department"`, `"Annual_Salary"`, `"Phone_Number"`).
- 🛡️ **Non-Destructive File Preservation**: Creates modified `.xlsx` downloads while keeping uploaded original files completely intact.
- 🔍 **Diff Preview & Confirmation Modal**: Shows exact old vs. new values and confidence scores before applying changes.
- 🧹 **Isolation Forest Anomaly Cleaning**: Detects numerical multivariate outliers, missing values, duplicates, and casing inconsistencies.
- 📊 **Automated ML Pipelines**: Auto-profiles dataset features, computes correlation heatmaps, and trains Random Forest, Linear Regression, or Logistic Regression models.
- 📈 **Interactive Inference**: Inputs custom feature values to generate real-time target predictions.
- 📜 **Operation Audit History**: Maintains a complete log of all spreadsheet updates and ML operations.
- 🌐 **Dual Execution Mode**: Operates out-of-the-box in standalone browser mode for GitHub Pages while seamlessly connecting to the Python FastAPI backend (`http://localhost:8000`) when running locally.

---

## 🧩 5. Three Major Modules

### Module 1 — AI Excel Navigator & Updater
- Upload `.xlsx`, `.xls`, and `.csv` files.
- Display sheets, column structures, and sample rows.
- Understand natural language instructions (`UPDATE`, `FIND`, `CLEAN`, `ANALYZE`, `PREDICT`).
- Extract target record identifiers, column headers, and replacement values.
- Present side-by-side diff previews with confidence scores.
- Export modified spreadsheets securely.

### Module 2 — Intelligent Data Cleaner
- **Missing Value Detection**: Detects null cells and imputes numerical features with median and categorical features with mode.
- **Duplicate Row Removal**: Identifies exact and partial row duplicates.
- **Text Normalization**: Trims leading/trailing whitespace and standardizes capitalization (e.g., `'cse'` $\rightarrow$ `'CSE'`).
- **Isolation Forest Outlier Detection**: Flag numerical multivariate anomalies using machine learning.

### Module 3 — ML Analyzer & Predictor
- Automatic detection of dataset dimensions, missing counts, and numerical vs. categorical feature types.
- Feature distribution bar charts and correlation heatmaps.
- Model Selection: **Linear Regression**, **Logistic Regression**, **Random Forest Regressor/Classifier**.
- Automated 80/20 train/test split, feature scaling, and one-hot encoding pipelines.
- Metric evaluation ($R^2$, $RMSE$, $MAE$, $Accuracy$, $Precision$, $Recall$, $F1$).
- Interactive real-time prediction card.

---

## 🤖 6. Machine Learning Techniques
1. **Isolation Forest (`sklearn.ensemble.IsolationForest`)**: Unsupervised algorithm for isolating numerical outliers based on tree partitions and anomaly decision scores.
2. **Random Forest Classifier & Regressor (`sklearn.ensemble`)**: Ensemble tree model for high-accuracy non-linear target estimation.
3. **Linear & Logistic Regression (`sklearn.linear_model`)**: Baseline statistical models for continuous target regression and discrete classification tasks.
4. **Column Transformer Pipeline (`sklearn.compose.ColumnTransformer`)**:
   - `SimpleImputer` for handling missing numeric and categorical values.
   - `StandardScaler` for feature normalization ($Z$-score standardization).
   - `OneHotEncoder` for categorical feature vectorization.

---

## 🗣️ 7. Natural Language Processing (NLP) Techniques
1. **Intent Classification**: Naive Bayes (`MultinomialNB`) & rule-based classifier trained on natural language command patterns to classify user intent into `UPDATE`, `FIND`, `CLEAN`, `ANALYZE`, or `PREDICT`.
2. **Hybrid Column Matcher**:
   - **TF-IDF Character N-Gram Vectorization (`TfidfVectorizer`)**: Captures structural similarities between prompt tokens and column headers.
   - **Cosine Similarity (`sklearn.metrics.pairwise.cosine_similarity`)**: Measures vector proximity.
   - **Fuzzy String Matching (`fuzzywuzzy`)**: Uses Levenshtein distance, partial ratio, and token set ratio to map informal slang (`"dept"` $\rightarrow$ `"Department"`).
3. **Regex Entity Extraction**: Regular expression patterns extract target identifiers (e.g., `1025`, `E104`), target column terms, and target new values.

---

## 🛠️ 8. Technology Stack

### Backend
- **Python 3.13**
- **FastAPI** & **Uvicorn** (REST API framework)
- **Pandas** & **NumPy** (Data processing)
- **OpenPyXL** (Excel spreadsheet read/write)
- **Scikit-Learn** (Machine learning algorithms)
- **NLTK** & **FuzzyWuzzy** / **Python-Levenshtein** (NLP & string matching)
- **Joblib** (Model serialization)

### Frontend (GitHub Pages Ready)
- **HTML5 & Vanilla CSS3** (Custom dark glassmorphic design system)
- **JavaScript (ES6+)**
- **SheetJS (xlsx.full.min.js)** (Client-side spreadsheet parsing & export)
- **Chart.js** (Interactive data visualization)
- **FontAwesome 6** (Iconography)

---

## 🏗️ 9. System Architecture

```
[ User Upload / Prompt ]
          │
          ▼
┌──────────────────────────────────────────────────────────┐
│                   GitHub Pages Frontend                  │
│                (docs/index.html & script.js)              │
└────────────────────────────┬─────────────────────────────┘
                             │
            ┌────────────────┴────────────────┐
            ▼                                 ▼
 ┌──────────────────────┐        ┌──────────────────────────┐
 │ Client-Side Engine   │        │ Python FastAPI Backend   │
 │ (SheetJS / Chart.js) │        │ (http://localhost:8000)  │
 └──────────────────────┘        └────────────┬─────────────┘
                                              │
         ┌────────────────────────────────────┼────────────────────────────────────┐
         ▼                                    ▼                                    ▼
┌──────────────────────┐           ┌──────────────────────┐           ┌──────────────────────┐
│ Module 1: NLP Engine │           │ Module 2: Cleaner    │           │ Module 3: ML Models  │
│ - TF-IDF & Fuzzy     │           │ - Isolation Forest   │           │ - Random Forest      │
│ - Intent Classifier  │           │ - Quality Audit      │           │ - Linear/Logistic Reg│
└──────────────────────┘           └──────────────────────┘           └──────────────────────┘
```

---

## 📁 10. Folder Structure

```
aicw/
├── docs/                             # GitHub Pages deployment folder
│   ├── index.html                    # Single Page Application (SPA) dashboard
│   ├── style.css                     # Premium modern CSS design system & styles
│   └── script.js                     # Frontend interactive logic (Client-side & REST API client)
│
├── backend/                          # Python Machine Learning & NLP Backend
│   ├── app.py                        # FastAPI REST API server
│   ├── services/                     # Business logic services
│   │   ├── __init__.py
│   │   ├── excel_reader.py           # Pandas/OpenPyXL reading & summary utilities
│   │   ├── excel_updater.py          # Row/cell modification without overwriting originals
│   │   ├── excel_cleaner.py          # Missing data, duplicates, outliers & normalization
│   │   ├── nlp_processor.py          # Intent classification & entity extraction pipeline
│   │   ├── column_matcher.py         # TF-IDF, Cosine Similarity & Fuzzy matching
│   │   └── history_manager.py        # Audit trail & operation logging
│   ├── models/                       # ML model components
│   │   ├── __init__.py
│   │   ├── intent_classifier.py      # NLP Intent Classifier
│   │   ├── anomaly_detector.py       # Isolation Forest anomaly detection model
│   │   └── prediction_models.py      # Random Forest, Linear/Logistic Regression wrappers
│   └── utils/                        # System utilities
│       ├── __init__.py
│       ├── validators.py             # Schema & input validators
│       └── file_handler.py           # Temporary file management & safe export
│
├── tests/                            # Pytest test suite
│   ├── test_nlp.py                   # Tests NLP intent parsing & fuzzy column matching
│   ├── test_excel_updater.py         # Tests Excel cell updates & output generation
│   ├── test_data_cleaner.py          # Tests missing values, duplicates, and Isolation Forest
│   └── test_prediction.py            # Tests ML classification and regression training
│
├── sample_data/                      # Pre-populated test datasets
│   └── Students.xlsx                 # Test dataset for Student updates & ML testing
│
├── requirements.txt                  # Python dependencies
└── README.md                         # Project documentation
```

---

## 💻 11. Installation Instructions

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/your-username/smart-excel-ai.git
   cd smart-excel-ai
   ```

2. **Create & Activate Virtual Environment**:
   ```bash
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   ```

3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

---

## 🚀 12. How to Run Locally

### Step 1: Start the Python Backend
Run the FastAPI application via `uvicorn`:
```bash
uvicorn backend.app:app --reload --port 8000
```
- API Base URL: `http://127.0.0.1:8000`
- Interactive Swagger Documentation: `http://127.0.0.1:8000/docs`

### Step 2: Launch the Frontend Interface
Open `docs/index.html` directly in your web browser, or serve it using Python's built-in HTTP server:
```bash
python -m http.server 8080 --directory docs
```
Navigate to `http://localhost:8080` in your web browser.

---

## 🌐 13. GitHub Pages Deployment Instructions

Because the frontend application is located inside the `docs/` folder, deploying to GitHub Pages requires zero complex build steps:

1. Push your repository code to GitHub.
2. Go to your GitHub repository **Settings** $\rightarrow$ **Pages**.
3. Under **Build and deployment** $\rightarrow$ **Source**, select **Deploy from a branch**.
4. Select branch `main` and folder `/docs`.
5. Click **Save**.
6. Your application will be live at: `https://<your-username>.github.io/<repo-name>/`.

---

## 🔮 14. Future Scope
- **LLM Integration**: Connect OpenAI GPT-4 / Google Gemini API for complex multi-step prompt reasoning.
- **Voice Commands**: Add Web Speech API integration to allow voice-driven spreadsheet updates.
- **Multi-File Joins**: Support natural language cross-workbook VLOOKUP and SQL-style JOIN queries.

---

## ⚠️ 15. Limitations
- Extremely large Excel workbooks (> 100,000 rows) may require higher memory limits when generating client-side previews.
- GitHub Pages static hosting runs client-side JS mode unless connected to a running Python backend.

---

## 🧪 16. Testing

The project includes unit tests covering all core backend modules.

Run the test suite using `pytest`:
```bash
python -m pytest tests/ -v
```

### Verified Test Cases
- `tests/test_nlp.py`: Verifies intent classification (`UPDATE`, `FIND`, `CLEAN`, `PREDICT`) and fuzzy column matching (`dept` $\rightarrow$ `Department`).
- `tests/test_excel_updater.py`: Ensures cell updates produce valid modified files without overwriting original inputs.
- `tests/test_data_cleaner.py`: Verifies missing value imputation, duplicate removal, and Isolation Forest anomaly detection.
- `tests/test_prediction.py`: Tests Scikit-learn Random Forest model training, $R^2$ score calculation, and inference predictions.

---

## 🎨 17. Screenshots Section

| Module | Interface Preview |
|---|---|
| **Dashboard** | Modern dark glassmorphism SaaS layout with KPI metric counters and module shortcuts. |
| **Excel Updater** | Natural language prompt input, confidence score badge, value diff box (`CSE` $\rightarrow$ `AI`), and download button. |
| **Data Cleaner** | Data health overview cards, Isolation Forest outlier counts, and customizable cleaning toggles. |
| **ML Analyzer** | Feature correlation heatmap, distribution charts, and Random Forest evaluation metrics. |

---

## 👨‍🎓 18. Author Section
- **Student Project**: B.Tech Computer Science & Engineering / Artificial Intelligence
- **Project Name**: Smart Excel AI Automation Assistant
