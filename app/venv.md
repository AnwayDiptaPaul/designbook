# Python Virtual Environment (`app/.venv`)

This document details the configuration, installed packages, and instructions for managing and recreating the Python virtual environment (`.venv`) located in the `./app/` directory of the **DesignBook** project.

---

## 🔍 Virtual Environment Overview

DesignBook uses an isolated Python virtual environment to manage dependencies for its FastAPI backend, OpenSeesPy structural-analysis engine, Celery task runners, and scientific packages.

*   **Path:** `./app/.venv/`
*   **Base Python Version:** CPython `3.11.11` (configured via `pyvenv.cfg`)
*   **Package Manager:** Managed using [**uv**](https://github.com/astral-sh/uv) (version `0.11.28`), a fast Rust-based replacement for `pip` and `virtualenv`.
*   **Ignoring in Git:** The folder is ignored in version control via the root [`.gitignore`](../.gitignore).

---

## 📁 Directory Structure of `.venv`

```text
app/.venv/
├── pyvenv.cfg          # Environment configuration (python version, uv reference)
├── Scripts/            # Windows executable binaries (python, uvicorn, celery, pytest)
├── Lib/site-packages/  # Compiled source libraries for all installed packages
├── include/            # C/C++ header files for compiled modules
└── share/              # Shared assets and documents
```

*Key files under `Scripts/`:*
*   `python.exe` / `pythonw.exe` — The environment's local Python interpreters.
*   `activate` / `activate.ps1` / `activate.bat` — Activation scripts for different shells.
*   Command-line tool wrappers: `uvicorn.exe`, `celery.exe`, `alembic.exe`, `pytest.exe`, `fastapi.exe`, `websockets.exe`.

---

## 📦 Installed Packages & Their Roles

Below is a categorized breakdown of the packages installed inside the environment, including their functions and needs within the DesignBook application:

### 1. Web API & Server Layer
These packages run the HTTP server, serve the API, and handle real-time communications.

| Package | Version | Need & Function in DesignBook |
|---|---|---|
| **fastapi** | `0.141.1` | Web framework used to define REST API endpoints, routing, and request handlers. |
| **starlette** | `1.6.0` | Core toolkit underlying FastAPI, providing routing, middleware, and request/response abstraction. |
| **uvicorn** | `0.52.1` | High-performance ASGI server for running the FastAPI application locally. |
| **websockets** | `17.0.1` | Enables live bidirectional WebSocket communication, used to stream structural analysis progress updates to the frontend. |
| **python-multipart** | `0.0.32` | Enables support for parsing multi-part form data (e.g., uploading files like DXF/CAD or structural configuration files). |
| **h11** / **httptools** / **watchfiles** | Variable | Uvicorn dependency handlers for HTTP parsing and automatic code reloading on changes. |

### 2. Structural Analysis & Engineering Engine
The core computational engines that run calculations and evaluate structures.

| Package | Version | Need & Function in DesignBook |
|---|---|---|
| **openseespy** / **openseespywin** | `3.7.0.3` | Python bindings for OpenSees (Open System for Earthquake Engineering Simulation). The core engine used to construct 2D/3D models, run linear elastic/dynamic analyses, and check modal frequencies. |
| **numpy** | `2.4.6` | Numerical computing library used for matrix operations, coordinate math, and high-performance structural geometry data handling. |
| **scipy** | `1.17.1` | Used for advanced mathematical operations, solver routines, and scientific algorithms. |
| **pandas** | `3.0.5` | Data manipulation library used to structure and export calculation tables, results, and quantity takeoffs. |

### 3. Data Validation & Configuration
| Package | Version | Need & Function in DesignBook |
|---|---|---|
| **pydantic** | `2.13.4` | Enforces type hints at runtime, validates incoming user request bodies (e.g. node coordinates, section properties), and serializes JSON outputs. |
| **pydantic-settings** | `2.15.0` | Reads environment configurations and binds them to type-safe settings classes in the app configuration. |
| **python-dotenv** | `1.2.2` | Parses `.env` configuration files to load variables into the system environment. |

### 4. Database Access & Migrations
| Package | Version | Need & Function in DesignBook |
|---|---|---|
| **sqlalchemy** | `2.0.51` | Object-Relational Mapper (ORM) for communication with the PostgreSQL database. |
| **asyncpg** | `0.31.0` | Asynchronous PostgreSQL database driver. |
| **alembic** | `1.19.1` | Database migration framework used to generate and execute SQL schema updates. |
| **greenlet** | `3.5.4` | Async execution helper required by SQLAlchemy for async operation compatibility. |
| **mako** | `1.4.1` | Template engine used by Alembic to render database migration script templates. |

### 5. Background Tasks & Job Queue
Offloads long-running structural analysis jobs from the main API thread.

| Package | Version | Need & Function in DesignBook |
|---|---|---|
| **celery** | `5.6.3` | Distributed task queue used to run OpenSeesPy analysis workers asynchronously. |
| **redis** | `8.1.0` | Redis Python client, serving as Celery's message broker and database state store. |
| **amqp** / **kombu** / **billiard** | Variable | Lower-level transport and process pooling libraries required by Celery to process tasks safely. |

### 6. Excel Integration
| Package | Version | Need & Function in DesignBook |
|---|---|---|
| **openpyxl** | `3.1.5` | Used to read and write Excel (`.xlsx`) files. This permits the engine to load configuration templates, export calculation sheets, and verify structural designs against the workbooks in `doc-files/design-excel/`. |

### 7. Visualization & PDF Reports
| Package | Version | Need & Function in DesignBook |
|---|---|---|
| **matplotlib** | `3.11.1` | Renders structural drawings, load diagrams, and P-M column interaction charts to image files. |
| **reportlab** | `5.0.0` | PDF generation engine used to compile and export formal engineering reports. |
| **pillow** | `12.3.0` | Image processing library used to resize, compress, and embed diagrams within the PDF reports. |
| **fonttools** | `4.63.0` | Manages vector fonts inside PDF report templates. |

### 8. Authentication & Security
| Package | Version | Need & Function in DesignBook |
|---|---|---|
| **python-jose** | `3.5.0` | Encodes and decodes JSON Web Tokens (JWT) for secure user sessions. |
| **cryptography** / **bcrypt** / **passlib** | Variable | Secure hashing utilities for user passwords and cryptographic token verification. |

### 9. Test Suite
| Package | Version | Need & Function in DesignBook |
|---|---|---|
| **pytest** | `9.1.1` | Test runner for executing unit and integration tests. |
| **pytest-asyncio** | `1.4.0` | Extension to allow writing and running asynchronous tests. |

---

## 🛠️ How to Recreate the Virtual Environment

Follow these steps to recreate the `./app/.venv` environment from scratch using the `uv` package manager:

### Prerequisites
1.  **Python:** Ensure Python `3.11` (ideally `3.11.11` or higher) is installed on your machine.
2.  **uv:** Ensure `uv` is installed on your system. If not, install it using:
    *   **Windows (PowerShell):** `irm https://astral.sh/uv/install.ps1 | iex`
    *   **macOS/Linux:** `curl -LsSf https://astral.sh/uv/install.sh | sh`

---

### Step-by-Step Recreation

Navigate to the project root directory in your terminal and run:

#### 1. Remove the Existing Environment (if any)
```powershell
# On Windows PowerShell / Command Prompt
rmdir /s /q app\.venv

# On macOS/Linux/Git Bash
rm -rf app/.venv
```

#### 2. Create the Virtual Environment
Initialize a fresh environment inside `./app/` pointing to Python 3.11:
```bash
# This creates the .venv folder inside the app directory
uv venv app/.venv --python 3.11
```

#### 3. Install Dependencies
You can install the backend packages directly from `app/backend/requirements.txt` using `uv pip`:

```bash
# Install the locked requirements into the new virtual environment
uv pip install -r app/backend/requirements.txt --python app/.venv/Scripts/python.exe
```

*Note: Alternatively, if you activate the virtual environment first, you can run the standard `uv pip` install command directly:*

**Activate & Install (Windows):**
```powershell
# Activate the environment
.\app\.venv\Scripts\Activate.ps1

# Install requirements
uv pip install -r .\app\backend\requirements.txt
```

**Activate & Install (macOS/Linux):**
```bash
# Activate the environment
source app/.venv/bin/activate

# Install requirements
uv pip install -r app/backend/requirements.txt
```
