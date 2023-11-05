# LOLA: Learn Online Like Actually

LOLA is a Streamlit application that serves as a conversational agent, connecting users with learning resources on YouTube based on their specific learning requests. By integrating OpenAI's language models, the application identifies the user's learning objectives and suggests personalized content.

## Features

- Interactive chat interface for natural language processing.
- Dynamic YouTube playlist suggestions based on user queries.
- Multi-threaded video upload and management system.
- Personalized learning experience through AI-driven conversational understanding.

## Installation

To set up the LOLA application, you need to have Python installed on your system. Follow these steps:

1. Clone the repository to your local machine:
    ```bash
    git clone https://github.com/Meeeee6623/Duke-GenAI-2023.git
    ```

2. Navigate to the cloned directory:
    ```bash
    cd Duke-GenAI-2023
    ```

3. Install the required Python packages:
    ```bash
    pip install -r requirements.txt
    ```

4. Create a `.env` file in the root directory and add the necessary environment variables as specified in `.env.example`.

5. Start the Streamlit application:
    ```bash
   ./run.sh
    ```

## Usage

After starting the Streamlit application, LOLA can be accessed through a web browser.

1. **Start a Conversation**: Engage with the AI by typing your learning request in the chat interface.

2. **Receive Suggestions**: Based on your input, LOLA will suggest YouTube playlists that match your learning objectives.

3. **Select Content**: Choose from the suggested playlists and watch the videos to learn about your topic of interest.

4. **Manage Playlists**: LOLA can manage multiple video uploads, utilizing multi-threading to optimize performance.

## Contributing

Contributions to LOLA are welcome! If you have suggestions for improvements or want to contribute code, please:

1. Fork the repository.
2. Create a new branch for your feature (`git checkout -b feature/AmazingFeature`).
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`).
4. Push to the branch (`git push origin feature/AmazingFeature`).
5. Open a pull request.

## License

Distributed under the MIT License. See `LICENSE` for more information.

## Contact


Project Link: [https://github.com](https://github.com/Meeeee6623/Duke-GenAI-2023)

## Acknowledgements

- [Streamlit](https://streamlit.io/)
- [OpenAI](https://openai.com/)
- [YouTube Data API](https://developers.google.com/youtube/v3)

