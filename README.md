# CHIRP to BTECH CSV Converter

A web application built with Python, HTMX, and a modern CSS framework to convert CSV files exported from CHIRP format to the BTECH UV-Pro format and vice-versa.

## 🚀 Overview

This application provides a bi-directional conversion tool for GMRs/radio logs, allowing users to seamlessly convert between the CHIRP format (from sources like chirpmyradio.com) and the format used by the BTECH UV-Pro.

## ✨ Features

*   **Bi-directional Conversion:** Convert CSVs from CHIRP format to BTECH UV-Pro format, and vice-versa.
*   **File Handling:** Ability to upload/download CSV files.
*   **Data Persistence:** Stores conversion history, input/output files, and conversion records in a SQLite database.
*   **Channel Limiting:** Automatically handles the BTECH UV-Pro limit of 30 channels by truncating files with more than 30 entries and issuing a warning to the user.
*   **Interactive Input:** Features a text area for copying/pasting CSV content.
*   **User Interface:** Built with HTMX for dynamic interactivity and styled with a modern CSS framework.
*   **Testing:** Includes a comprehensive suite of unit tests to ensure correct behavior and prevent regressions.
*   **End-to-End Testing:** Includes Playwright tests for verifying the full user flow.

## 🛠️ Technology Stack

*   **Backend:** Python
*   **Frontend:** HTMX
*   **Styling:** Modern CSS Framework
*   **Database:** SQLite
*   **Testing:** Pytest, Playwright

## 📚 Usage

1.  **Upload:** Upload a CHIRP or BTECH CSV file via the interface.
2.  **Convert:** Select the desired direction (CHIRP $\leftrightarrow$ BTECH) and initiate the conversion.
3.  **View Results:** Download the converted file containing the results.
4.  **History:** Review the SQLite database for a record of past conversions.

## 📚 Documentation

For details on the required CSV formats, please refer to the official guide: [https://baofengtech.com/your-complete-channel-import-guide-for-gmrs-pro-uv-pro/](https://baofengtech.com/your-complete-channel-import-guide-for-gmrs-pro-uv-pro/)
