# DevSeek - Vertical Search Engine for Developers

## Overview
DevSeek is a Vertical Search Engine built from scratch specifically for the Information Technology (IT) and Programming domain.

The system is designed following standard Data Engineering & Information Retrieval pipelines, consisting of the following core features:
- **Automated Data Crawling**: Collects and aggregates hundreds of in-depth IT articles, storing them in multiple formats (JSON, CSV, SQLite Database).
- **Preprocessing & Indexing**: Performs Vietnamese Natural Language Processing (tokenization using Underthesea) and builds a multi-field Inverted Index data structure incorporating Positions and Field Term Frequency (TF).
- **Ranking & Retrieval**: Supports two of the most popular document search and ranking algorithms: Multi-Field TF-IDF and Okapi BM25F.
- **Automated Evaluation**: Integrates an automated testing system to directly compare the performance of TF-IDF and BM25 (measured by Precision@10 and MAP).
- **Web Interface (Web App)**: An intuitive graphical user interface built with Flask, allowing users to easily query and retrieve documents.

## Environment Setup
Ensure you have Python installed (version 3.8 or higher is recommended).
To install the required libraries, open your Terminal/Command Prompt in the project's root directory and run the following command:

```bash
pip install -r requirements.txt
```

## Usage Instructions

The project consists of 2 main workflows: **Data Building & Evaluation (Backend Pipeline)** and **Running the Web App (Frontend App)**.

### Step 1: Run the Full Pipeline (Data Building, Indexing & Evaluation)
Before you can search, you need to run the system to crawl data, create the index, and evaluate the algorithms.
From the project's root directory, run the `main.py` file:

```bash
python main.py
```

The process will automatically execute sequentially:
1. Clear all old data (complete system reset).
2. Crawl the new IT dataset and save it to the `data/raw/` directory.
3. Process Vietnamese NLP and create the Inverted Index at `data/processed/`.
4. Run the automated benchmark evaluation to compare TF-IDF vs BM25 algorithms.

### Step 2: Launch the Web Search Interface
After Step 1 has successfully prepared the data, you can open the search interface for end-users by running:

```bash
python run_app.py
```

Once the server has successfully started, open your web browser and navigate to the following address:
👉 **http://localhost:5000**

*(Note: To stop the web server, you can press the `Ctrl + C` key combination in the Terminal window).*

## Project Directory Structure
- `crawler/`: Contains scripts for crawling/collecting data from technology websites.
- `data/`: The location for storing raw data (`raw/`) and processed/indexed data (`processed/`).
- `engine/`: Contains the core logic of the search engine (Inverted Indexer, Retrieval/Ranking Models).
- `evaluation/`: Automated testing scripts and generation of benchmark queries for system evaluation.
- `web/`: The Flask Backend source code and HTML/CSS/JS Frontend of the web application.
- `main.py`: The script to trigger the entire Data pipeline & Evaluation process.
- `run_app.py`: The script to start the Flask Web App server.
