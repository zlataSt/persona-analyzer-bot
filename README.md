# Communication Style Analysis Bot

<p align="center">
  <a href="https://t.me/PersonaAnalyzerBot">
    <img src="https://img.shields.io/badge/Run%20Bot-on%20Telegram-blue.svg?style=for-the-badge&logo=telegram" alt="Run on Telegram">
  </a>
</p>

A Telegram bot designed to analyze communication patterns from chat logs and provide insights based on psychometric models.

**For a user guide in Russian, please see [USER_GUIDE_RU.md](./USER_GUIDE_RU.md).**

## Features

-   **VK Chat Log Parsing**: Upload a `.txt` file exported from VK (e.g., via Kate Mobile).
-   **User-Specific Extraction**: Isolates all messages from a single, specified user, ignoring replies and forwarded messages.
-   **AI-Powered Analysis**: Utilizes Google's Gemini Pro to perform a deep analysis of the user's communication style.
-   **Structured Reporting**: The analysis is structured by dichotomies (e.g., extraversion/introversion) and functional models for a comprehensive overview.
-   **PDF Export**: Download the complete analysis as a neatly formatted PDF document.
-   **Interactive Interface**: A simple, step-by-step process guided by inline buttons.

## Usage Guide

You can start using the bot right away on Telegram:
-   **[t.me/PersonaAnalyzerBot](https://t.me/PersonaAnalyzerBot)**

For detailed instructions on how to use the bot, please refer to our user guide:
-   **[User Guide (Russian)](./USER_GUIDE_RU.md)**

## Deployment

This bot is designed for deployment using Docker and can be easily hosted on platforms like [Fly.io](https://fly.io/).

### Prerequisites

-   Python 3.11+
-   Docker
-   `flyctl` command-line tool

### Local Setup

1.  Clone the repository:
    ```bash
    git clone https://github.com/your-username/your-repo-name.git
    cd your-repo-name
    ```
2.  Create a virtual environment and activate it:
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
    ```
3.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```
4.  Create a `.env` file in the root directory and add your secrets:
    ```
    TELEGRAM_TOKEN="YOUR_TELEGRAM_BOT_TOKEN"
    GEMINI_API_KEY="YOUR_GEMINI_API_KEY"
    ```
5.  Run the bot:
    ```bash
    python -m src.main
    ```

### Deployment to Fly.io

1.  Authenticate with Fly.io:
    ```bash
    flyctl auth login
    ```
2.  Launch the app (this will create a `fly.toml` file if one doesn't exist):
    ```bash
    flyctl launch
    ```
    Follow the prompts. Choose a unique name for your app and select a US-based region (e.g., `iad` - Ashburn, VA) for Gemini API compatibility.
3.  Set the secrets on Fly.io. These will be securely injected as environment variables.
    ```bash
    flyctl secrets set TELEGRAM_TOKEN="YOUR_TELEGRAM_BOT_TOKEN"
    flyctl secrets set GEMINI_API_KEY="YOUR_GEMINI_API_KEY"
    ```
4.  Deploy your application:
    ```bash
    flyctl deploy
    ```

Your bot is now live! You can check its status and logs using `flyctl status` and `flyctl logs`.