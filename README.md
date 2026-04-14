# CHIRP to BTECH CSV Converter

A web application built with Python, HTMX, and a modern CSS framework to convert CSV files exported from CHIRP format to the BTECH UV-Pro format and vice-versa.

## 🚀 Overview

This application provides a bi-directional conversion tool for GMRs/radio logs, allowing users to seamlessly convert between the CHint format (from sources like chirpmyradio.com) and the format used by the BTECH UV-Pro.

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

*   **Backend:** Python (Flask)
*   **Frontend:** HTMX
*   **Styling:** Modern CSS Framework (Water.css)
*   **Database:** SQLite
*   **Testing:** Pytest, Playwright

## ⚙️ Installation & Setup

1.  **Clone the repository:**
    ```bash
    git clone <repository-url>
    cd chirp2uvpro
    ```

2.  **Create and activate a virtual environment:**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On macOS/Linux
    # venv\Scripts\activate  # On Windows
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Run the application:**
    ```bash
    python src/app/main.py
    ```
    The application will be available at `http://localhost:5000`.

## 🐳 Docker Deployment

You can run the application using Docker and Docker Compose. This setup includes the application itself and a Cloudflare Tunnel for secure remote access.

1.  **Create a `.env` file** in the root directory with your Cloudflare Tunnel token:
    ```env
    CLOUDFLARE_TUNNEL_TOKEN=your_token_here
    ```

2.  **Build and run the containers:**
    ```bash
    # If you encounter issues with stale containers, run: docker-compose down
    # If you are not in the docker group, you may need to use sudo
    sudo docker-compose up --build -d
    ```

**Note:** If you have recently added your user to the `docker` group, you will need to log out and back in (or start a new session) for the changes to take effect. You can use `sudo` as a temporary workaround.

Once started, the application is accessible at `http://localhost:5000` on your local network, and via the public URL configured in your Cloudflare Dashboard (pointing to `http://localhost:5000`).

**Note:** The Cloudflare Tunnel service is configured with `network_mode: "host"` to allow it to reach the Flask application running on the host's port 5000.

## 📚 Usage

1.  **Upload:** Upload a CHIRP or BTECH CSV file via the interface.
2.  **Convert:** Select the desired direction (CHIRP $\leftrightarrow$ BTECH) and initiate the conversion.
3.  **View Results:** Download the converted file containing the results.
4.  **History:** Review the SQLite database for a record of past conversions.

For details on the required CSV formats, please refer to the official guide: [https://baofengtech.com/your-complete-channel-import-guide-for-gmrs-pro-uv-pro/](https://baofengtech/your-complete-channel-import-guide-for-gmrs-pro-uv-pro/)

## 🧪 Running Tests

### Unit Tests
Run the unit tests using pytest:
```bash
source venv/binenter/activate
pytest tests/unit
```

### End-to-End (E2E) Tests
Run the Playwright-based E2E tests:
```bash
source venv/bin/activate
pytest tests/e2e
```

## 📂 Project Structure

*   `src/app/`: Main application logic and routes.
*   `src/app/templates/`: HTML templates and partials.
*   `src/database/`: Database connection and management.
*   `src/converter/`: Core conversion logic.
*   `tests/`: Test suites (Unit and E2E).
*   `uploads/`: Directory for uploaded and processed files.

## 🛡️ License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
