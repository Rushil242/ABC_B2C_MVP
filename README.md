# ABC Tax Intelligence Platform (MVP)

A secure B2C platform for analyzing Income Tax Returns (ITR), identifying risks, and finding tax-saving opportunities.

## Features
- **Secure Authentication**: JWT-based login and registration.
- **Dashboard**: Real-time insights into tax risks and opportunities.
- **History**: View past ITR filings and tax notices.
- **Automation**: One-click sync to download ITR data from the official portal.

## Prerequisites
- **Python 3.9+**
- **Node.js 18+**

## Setup & Run Instructions

### 1. Backend Setup

The backend is built with **FastAPI** and uses **SQLite** as the database.

1.  **Navigate to the root directory**:
    ```bash
    cd ABC_B2C_MVP
    ```

2.  **Create a Virtual Environment (Optional but Recommended)**:
    ```bash
    python -m venv venv
    # Windows
    venv\Scripts\activate
    # Mac/Linux
    source venv/bin/activate
    ```

3.  **Install Python Dependencies**:
    ```bash
    pip install -r backend/requirements.txt
    ```

4.  **Install Playwright Browsers (Required for Sync)**:
    The scraper uses Playwright to automate the Income Tax Portal.
    ```bash
    python -m playwright install
    ```

5.  **Run the Backend Server**:
    ```bash
    uvicorn backend.main:app --reload --port 8000
    ```
    The API will be available at `http://localhost:8000`.
    API Documentation: `http://localhost:8000/docs`

### 2. Frontend Setup

The frontend is built with **React** (Vite) and **TypeScript**.

1.  **Navigate to the frontend directory**:
    ```bash
    cd frontend
    ```

2.  **Install Node Dependencies**:
    ```bash
    npm install
    ```

3.  **Run the Development Server**:
    ```bash
    npm run dev
    ```
    The application will be available at `http://localhost:5173`.

## Usage Guide

1.  **Login / Register**:
    - **Demo User**: PAN: `ABCDE1234F`, Password: `demo123`
    - Or register a new user.

2.  **View Dashboard**:
    - See your Risk Analysis, Tax Opportunities, and Tax Liability.

3.  **Sync Data (Automation)**:
    - Click the **"Sync Data"** button on the top-right of the Dashboard.
    - Enter your **Income Tax Portal Password** in the dialog.
    - The backend will use your PAN and Password to securely log in to the portal and download your filed returns.
    - **Check Logs**: Watch the terminal where `uvicorn` is running to see real-time scraping logs.

4.  **History**:
    - **Return History**: View past filings.
    - **Notice History**: View tax notices.

## Project Structure

- `backend/`: FastAPI application, database models, and logic.
- `frontend/`: React application.
- `automation/`: Playwright scripts for scraping ITR data.
