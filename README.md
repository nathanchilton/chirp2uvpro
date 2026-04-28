# Radio Frequency Configuration Converter

A web application and CLI tool built with Python, HTMX, and a modern CSS framework to convert CSV files between CHIRP, BTECH UV-Pro, and Clipboard formats.

## 🚀 Overview

This application provides a bi-directional conversion tool for GMRs/radio logs, allowing users to seamlessly convert between the CHint format (from sources like chirpmyradio.com) and the format used by the BTECH UV-Pro.

## ✨ Features

*   **Flexible Conversion:** Convert between CHIRP, BTECH UV-Pro, and Clipboard formats.
*   **Auto-detection:** Automatically detect the input format when "Auto-detect" is selected.
*   **Bi-directional:** Support for both CHIRP $\leftrightarrow$ BTECH and CHIRP $\leftrightarrow$ Clipboard conversions.
*   **File Handling:** Ability to upload/download CSV files.
*   **Data Persistence:** Stores conversion history, input/output files, and conversion records in a SQLite database.
*   **Channel Limiting:** Automatically handles the BTECH UV-Pro limit of 30 channels by truncating files with more than 30 entries and issuing a warning to the user.
*   **Interactive Input:** Features a text area for copying/pasting CSV content.
*   **User Interface:** Built with HTMX for dynamic interactivity and styled with a modern CSS framework.
*   **Testing:** Includes a comprehensive suite of unit tests to ensure correct and prevent regressions.
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

1.  **Upload/Paste:** Upload a CSV file or paste content into the "Text Input" tab.
2.  **Configure Formats:** Select the input format (or Auto-detect) and the desired output format.
3.  **Convert:** Initiate the conversion process.
4.  **View Results:** Download the converted file or copy the result from the text area.
5.  **History:** Review the SQLite database for a    record of past conversions.

### 🛰️ RepeaterBook Import Workflow

You can automatically populate your channel list with nearby repeaters:

1.  **Load Initial Channels:** Start by uploading a CSV or pasting existing channels into the "Text Input" or "Upload" tabs.
2.  **Trigger Import:** Click the **"Import Repeaters"** button. The app will request your location via the browser's Geolocation API.
3.  **Select Channels to Keep (Pinning):**
    *   If you have existing channels, a selection interface will appear.
    *   By default, all current channels are "pinned" (checked).
    *   **Uncheck** any channels you do *not* want to keep in your new list.
4.  **Apply:** Click **"Apply Import"**. The app will merge your pinned channels with the newly discovered repeaters, respecting the 30-channel limit of the BTECH UV-Pro.
5.  **Result:** The updated list will be automatically generated in the "Result" text area in Clipboard format.

For details on the required CSV formats, please refer to the official guide: [https://baofengtech.com/your-complete-channel-import-guide-for-gmrs-pro-uv-pro/](https://baofengtech.com/your-complete-channel-import-guide-for-gmrs-pro-uv-pro/)

## 💻 Command Line Interface (CLI)

For automation and headless environments, use the built-in CLI tool.

### Installation

Ensure you have the project dependencies installed:

```bash
pip install -r requirements.txt
```

### Usage

The CLI tool allows you to convert between formats directly from your terminal.

```bash
python src/cli/main.py convert --from <format> --to <format> [options]
```

#### Arguments:

*   `--from <format>`: The source format (`chirp`, `btech`, or `clipboard`). **Required.**
*   `--to <format>`: The target format (`chirp`, `btech`, or `clipboard`). **Required.**
*   `--input <file>`: Path to the input file (defaults to `stdin`).
*   `--output <file>`: Path to the output file (defaults to `stdout`).
*   `--clipboard-format <format>`: (Only for clipboard output) The format for clipboard output (`json` or `csv`). Defaults to `json`.

#### Examples:

**Convert CHIRP to BTECH:**

```bash
python src/cli/main.py convert --from chirp --to btech --input input.csv --output output.csv
```

**Convert BTECH to Clipboard (JSON):**

```bash
python src/cli/main.py convert --from btech --to clipboard --input btech.csv --clipboard-format json
```

**Using stdin/stdout:**

```bash
cat input.csv | python src/cli/main.py convert --from chirp --to btech
```

## 🧪 Running Tests

### Unit Tests
Run the unit tests using pytest:
```bash
source venv/bin/activate
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
