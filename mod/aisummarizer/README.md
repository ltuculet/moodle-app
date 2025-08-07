# AI Summarizer (mod_aisummarizer)

## Description

The AI Summarizer is a Moodle activity module that allows students to upload text-based documents (such as `.txt`, `.pdf`, or `.docx` files) and receive an AI-generated summary of the content.

This plugin integrates with an external AI provider (like OpenAI or Vertex.ai) to perform the summarization. It is designed to be extensible and follows modern Moodle development practices.

**Note:** The current version has a simplified text extraction mechanism and only supports `.txt` files out-of-the-box. Extending it to support PDF and DOCX files requires installing additional server-side utilities (like `pdftotext` or `unoconv`) and modifying the `summary_service.php` class.

## Installation

1.  **Get the code:** Place the `aisummarizer` directory in the `mod/` directory of your Moodle installation. The path should be `/path/to/moodle/mod/aisummarizer`.
2.  **Log in to Moodle:** Log in to your Moodle site as an administrator.
3.  **Upgrade Moodle database:** Navigate to `Site administration > Notifications`. Moodle will detect the new plugin and guide you through the installation/upgrade process. Click "Upgrade Moodle database now" to install the plugin and create the necessary database tables.

## Configuration

Before you can use the plugin, you must configure it with the credentials for your chosen AI provider.

1.  **Navigate to settings:** Go to `Site administration > Plugins > Activity modules > AI Summarizer`.
2.  **Enter API credentials:**
    *   **API Key:** Enter the secret API key provided by your AI service.
    *   **API Endpoint:** Enter the full URL for the API endpoint. The default is for OpenAI's chat completions API.
    *   **AI Model:** Specify the model you wish to use (e.g., `gpt-3.5-turbo`, `gemini-pro`).
3.  **Save changes:** Click "Save changes".

The plugin is now ready to be added to courses.

## How to Use

1.  As a teacher in a course, turn editing on.
2.  Click "Add an activity or resource" in any course section.
3.  Select "AI Summarizer" from the activity chooser.
4.  Give the activity a name and an optional introduction.
5.  Click "Save and display".

Students can now visit the activity, upload a supported document, and click "Generate Summary" to receive the AI-powered summary.

## Testing

This plugin includes a foundation for both PHPUnit and Behat tests.

*   **PHPUnit:** To run the unit tests, execute:
    ```bash
    vendor/bin/phpunit --group mod_aisummarizer
    ```
*   **Behat:** To run the functional tests, you need a running Behat instance with Moodle. The feature file is located in `tests/behat/`.
    ```bash
    # (Requires a configured Behat environment)
    ```

## License

This plugin is licensed under the [GNU GPL v3 or later](http://www.gnu.org/copyleft/gpl.html).
