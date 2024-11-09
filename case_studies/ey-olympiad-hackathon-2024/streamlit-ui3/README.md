# Multilingual Chatbot with Streamlit

This project is a multilingual chatbot application built using Streamlit. The chatbot leverages Azure Cognitive Services for language detection and translation, and a custom RAG (Retrieval-Augmented Generation) model for answering questions.

## Project Structure



### Folder Descriptions

- **root directory**: Contains Jupyter notebooks for content analysis and metadata extraction.
- **streamlit-ui3/**: Main directory for the Streamlit application.
  - **.streamlit/**: Configuration files for Streamlit.
  - **assets/**: Contains the main Streamlit application script.
  - **views/**: Contains individual page scripts for the Streamlit application.
  - **language_detection_translation.py**: Script for language detection and translation using Azure Cognitive Services.
  - **rag.py**: Script for the RAG model.
  - **requirements.txt**: Dependencies for the Streamlit application.

## Setting Up and Running the Project

### Prerequisites

- Python 3.8 or higher
- Azure Cognitive Services account
- Streamlit

### Installation

1. Clone the repository:
    ```sh
    git clone <repository-url>
    cd <repository-directory>
    ```

2. Create a virtual environment and activate it:
    ```sh
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

3. Install the required dependencies:
    ```sh
    pip install -r requirements.txt
    ```

4. Set up your Azure Cognitive Services credentials in a `.env` file:
    ```env
    COG_SERVICE_ENDPOINT=<your-cognitive-service-endpoint>
    COG_SERVICE_KEY=<your-cognitive-service-key>
    ```

### Running the Application

1. Navigate to the `streamlit-ui3` directory:
    ```sh
    cd streamlit-ui3
    ```

2. Run the Streamlit application:
    ```sh
    streamlit run streamlit_app.py
    ```

3. Open your web browser and go to `http://localhost:8501` to access the application.

## Usage

- Navigate through the different pages using the sidebar.
- Use the chatbot to ask questions in multiple languages.
- View information about the hackathon and the team.

## Contributing

Contributions are welcome! Please open an issue or submit a pull request for any improvements or bug fixes.

## License

This project is licensed under the MIT License.