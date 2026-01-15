# Project: The Market Sentinel ETL Pipeline

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?style=for-the-badge&logo=python&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Neon-316192?style=for-the-badge&logo=postgresql&logoColor=white)
![CoinGecko](https://img.shields.io/badge/API-CoinGecko-8BC34A?style=for-the-badge&logo=coingecko&logoColor=white)
![ETL](https://img.shields.io/badge/Type-ETL_Pipeline-FF4B4B?style=for-the-badge)
![Status](https://img.shields.io/badge/Status-Phase_5_Complete-success?style=for-the-badge)
[![GitHub](https://img.shields.io/badge/GitHub-Repository-black?style=for-the-badge&logo=github)](https://github.com/zaltark/Automated-Crypto-Bot)

**Level:** Advanced Data Engineering / Infrastructure
**Objective:** Build a self-healing, cloud-native pipeline that ingests, transforms, and stores high-velocity commerce data with an automated 60-day retention policy and budget safeguards.

## 🚀 How to Run

### 1. Setup
1.  **Clone the repository.**
2.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
3.  **Configure Environment:**
    Create a `.env` file in the root directory:
    ```ini
    DATABASE_URL=postgres://user:password@host:port/dbname?sslmode=require
    ```

### 2. Execution
*   **Live Ingestion (Writes to DB):**
    ```bash
    python ingest.py --mode ingest --limit 500
    ```
*   **Dry-Run (Simulation only):**
    ```bash
    python ingest.py --mode dry-run
    ```

### 3. Management Utilities
*   **Check Database Health:** `python verify_db.py`
*   **Reset Database:** `python reset_db.py` (WARNING: Deletes all data)
*   **Check Budget:** `python budget_monitor.py` (Or runs automatically after ingestion)

---

## 🏗️ Architecture & Data Flow

This system follows a robust **Extract-Transform-Load (ETL)** pattern designed for resilience, scalability, and cost-efficiency.

![Market Sentinel Architecture](https://mermaid.ink/img/Z3JhcGggVEQKICAgIHN1YmdyYXBoICIxLiBPcmNoZXN0cmF0aW9uICYgU2FmZXR5IgogICAgICAgIEluZ2VzdFtpbmdlc3QucHldIC0tPnxMb2FkfCBDb25maWdbaW5nZXN0X2NvbmZpZy5qc29uXQogICAgICAgIEluZ2VzdCAtLT58U3luY3wgUmVnaXN0cnlbY29pbl9yZWdpc3RyeS5weV0KICAgICAgICBCdWRnZXRbYnVkZ2V0X21vbml0b3IucHldIC0uLT58TW9uaXRvcnwgSW5nZXN0CiAgICBzdWJncmFwaCAiMi4gRXh0cmFjdGlvbiAoQVBJKSIKICAgICAgICBSZWdpc3RyeSAtLT58VGFyZ2V0fCBBUElbYXBpX2xpYnJhcnkucHldCiAgICAgICAgQVBJIC0tPnxGZXRjaHwgQ29pbkdlY2tvW0NvaW5HZWNrbyBBUEldCiAgICBlbmQKCiAgICBzdWJncmFwaCAiMy4gVHJhbnNmb3JtYXRpb24gKExvZ2ljKSIKICAgICAgICBDb2luR2Vja28gLS0+fFJhdyBKU09OfCBUcmFuc2Zvcm1bdHJhbnNmb3JtLnB5XQogICAgICAgIFRyYW5zZm9ybSAtLT58VmFsaWRhdGV8IENsZWFuRGF0YVtDbGVhbiBUdXBsZXNdCiAgICBlbmQKCiAgICBzdWJncmFwaCAiNC4gU3RvcmFnZSAoUG9zdGdyZXMpIgogICAgICAgIENsZWFuRGF0YSAtLT58VXBzZXJ0fCBEQltkYXRhYmFzZS5weV0KICAgICAgICBEQiAtLT58U1FMfCBOZW9uW05lb24gUG9zdGdyZXNdCiAgICAgICAgREIgLS0+fFB1cmdlfCBSZXRlbnRpb25bNjAtRGF5IFJldGVudGlvbl0KICAgIGVuZA==)

1.  **Orchestrator (`ingest.py`):** The central nervous system. It coordinates the lifecycle, managing configuration, logging, and execution flow.
2.  **The Registry (`coin_registry.py`):** A smart filter that resolves symbols (e.g., "BTC" -> "bitcoin") and blocks "Ghost Coins" (dead assets) to save API credits.
3.  **Extraction:** Fetches data in smart chunks using **Exponential Backoff** and **Circuit Breakers**.
4.  **Transformation (`transform.py`):** A "Schema Shield" that validates types, ensures non-negative prices, and standardizes timestamps.
5.  **Loading (`database.py`):** Efficiently upserts data into Cloud SQL (Neon) and enforces a strict 60-day data retention policy.
6.  **Budget Guard (`budget_monitor.py`):** Tracks execution time and estimates cloud costs to prevent free-tier overages.

## 🌟 Key Feature: Self-Healing Autonomy

The pipeline includes a "Strike System" for asset health:
1.  **Detection:** If a coin returns garbage data (null prices) 3 times consecutively, it is flagged.
2.  **Action:** The system marks the coin as `inactive` in `coin_registry.json`.
3.  **Persistence:** The automation workflow (**GitHub Actions**) automatically commits this registry update back to the repository.
4.  **Result:** Future runs skip these dead assets, optimizing API usage and processing time automatically.

## 📂 File Library & Purpose

### Core System
*   **`ingest.py`**: The main executable. Runs the full pipeline (Extract -> Transform -> Load) or dry-run simulations. Wraps execution in budget monitoring.
*   **`transform.py`**: Pure logic module. Cleans raw API responses, validates schema (Float/DateTime), and merges symbol data.
*   **`database.py`**: SQL Interaction Layer. Handles schema initialization, efficient batch upserts, and data retention policies.
*   **`coin_registry.py`**: The intelligence unit. Manages the local "database" of coin mappings, resolves symbols, and tracks asset health.
*   **`coin_registry.json`**: Persistent storage for the registry. Stores the map of `symbol -> id` and the health status (`active`/`inactive`) of each coin.
*   **`safe_zone.py`**: Central configuration for safety constants (Batch sizes, API limits, Circuit breaker thresholds).

### Safety & Configuration
*   **`budget_monitor.py`**: Cost control unit. Logs execution time, calculates billable compute hours (including autosuspend buffer), and warns if monthly limits are near.
*   **`ingest_config.json`**: Runtime configuration. Sets default arguments (`mode`, `limit`, `targets`) for the pipeline.
*   **`.env`**: Secure environment variables. Stores the `DATABASE_URL` (ignored by Git).
*   **`api_library.py`**: API endpoint definitions. Keeps URLs and route logic decoupled from the main code.

### Utilities & Tools
*   **`verify_db.py`**: Dashboard tool. Checks database health, total record count, data freshness, and displays the top 5 assets.
*   **`reset_db.py`**: Administrative tool. Safely truncates (wipes) the `market_data` table for a fresh start.
*   **`sandbox.py`**: A "Paper Trading" simulator. Allows users to test trading strategies against the live pipeline data without real risk.
*   **`find_all_matches.py`**: Debugging tool. Detailed queries against the registry to inspect ticker collisions.

### Testing
*   **`test_registry.py`**: Unit tests for the Coin Registry logic (Top 250 sorting, symbol resolution).
*   **`test_restricted_endpoint.py`**: Specific test to ensure the system gracefully handles "Pro-Only" restricted API endpoints.

### Project Files
*   **`requirements.txt`**: Python dependencies.
*   **`README.md`**: This documentation.

## Phase Status

*   **Phase 1: Extraction** - `[COMPLETED]` (Smart Registry, Chunking, Circuit Breakers)
*   **Phase 2: Transformation** - `[COMPLETED]` (Schema Shield, Ghost Coin Guard)
*   **Phase 3: Storage** - `[COMPLETED]` (Neon Serverless Postgres, Efficient Upserts, Retention Policy)
*   **Phase 4: Automation** - `[COMPLETED]` (GitHub Actions Cron / Manual Trigger)
*   **Phase 5: Full Autonomy** - `[COMPLETED]` (Self-Healing Registry & Persistent Memory)

## Why this Portfolio Project Wins

*   **Scale:** Managing a rolling 1-million-row dataset proves you understand performance.
*   **Reliability:** The use of "Upserts", "Circuit Breakers", and "Budget Guards" shows you build systems that don't crash or bankrupt you.
*   **Automation:** The project runs itself 24/7 without human intervention.
*   **Self-Healing:** The system detects failures, fixes its own configuration, and persists those fixes to the codebase automatically.
*   **Full-Stack:** You demonstrate competence in Python, SQL, Cloud Infrastructure, and CI/CD pipelines.
