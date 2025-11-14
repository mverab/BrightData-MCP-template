[![Thordata Residential Proxies - Fast & Reliable IPs](./fef1680a-fbbb-4096-b40b-b69402cae52c.png)](https://dashboard.thordata.com/register?invitation_code=RZXYJQ1)

# BrightData Pain Extractor Agent

This project provides a conversational agent powered by LangChain, LangGraph, and OpenAI that leverages BrightData's web scraping and data extraction tools. You can interact with the agent in your terminal to perform various web data tasks.

## Features

- **Conversational Interface**: Interact with web scraping tools using natural language.
- **Powered by LangChain & OpenAI**: Utilizes the robust ReAct agent framework from LangChain and state-of-the-art models from OpenAI.
- **BrightData Integration**: Seamlessly connects to the BrightData MCP (Multi-purpose Crawler Platform) to access a wide range of data extraction tools.
- **Secure**: Manages API keys and sensitive credentials using environment variables.

## Prerequisites

- Python 3.9+
- Node.js and npm
- A BrightData account and API credentials
- An OpenAI API key

## Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/mverab/BrightData-painextractor.git
    cd BrightData-painextractor
    ```

2.  **Install Node.js dependencies:**
    The agent uses `npx` to run the BrightData MCP client.
    ```bash
    npm install
    ```

3.  **Set up a Python virtual environment:**
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```

4.  **Install Python dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

5.  **Configure your environment variables:**
    Create a `.env` file in the root of the project by copying the example:
    ```bash
    cp .env.example .env
    ```
    Now, edit the `.env` file and add your credentials:
    ```
    # .env
    OPENAI_API_KEY="your_openai_api_key"

    # BrightData Credentials
    API_TOKEN="your_brightdata_api_token"
    WEB_UNLOCKER_ZONE="your_web_unlocker_zone"
    BROWSER_ZONE="your_browser_zone"
    ```

## Usage

To start the conversational agent, run the `main.py` script:

```bash
python main.py
```

Once the agent is connected, you can start making requests. Here are a few examples:

- `Extract specs for Amazon ASIN B07NJG12GB`
- `Scrape product data from amazon.mx for laptops`
- `Get the latest news from reuters.com on technology`

To exit the agent, type `exit` or `quit`.

## How It Works

The agent uses a `StdioServer` to communicate with the BrightData MCP client, which is a Node.js process. `main.py` orchestrates the setup and runs a `langgraph` agent that can decide which BrightData tool to use based on the user's prompt.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.