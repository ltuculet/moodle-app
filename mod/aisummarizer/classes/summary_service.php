<?php
/**
 * Service class for handling AI summarization logic.
 *
 * @package    mod_aisummarizer
 * @copyright  2024 Your Name
 * @license    http://www.gnu.org/copyleft/gpl.html GNU GPL v3 or later
 */

namespace mod_aisummarizer;

defined('MOODLE_INTERNAL') || die();

use core\http\client;

/**
 * Service class for handling AI summarization logic.
 */
class summary_service {

    /**
     * Generates a summary for the given text content using an external AI API.
     *
     * @param string $textcontent The text to summarize.
     * @return \core\http\response The response from the AI service.
     * @throws \moodle_exception
     */
    public static function generate_summary(string $textcontent): \core\http\response {
        $apikey = get_config('mod_aisummarizer', 'apikey');
        $apiendpoint = get_config('mod_aisummarizer', 'apiendpoint');
        $apimodel = get_config('mod_aisummarizer', 'apimodel');

        if (empty($apikey) || empty($apiendpoint)) {
            throw new \moodle_exception('error:apiconfigmissing', 'mod_aisummarizer');
        }

        $httpclient = new client();
        $httpclient->set_options(['timeout' => 120]); // 2-minute timeout for AI response.
        $httpclient->set_header('Authorization', 'Bearer ' . $apikey);
        $httpclient->set_header('Content-Type', 'application/json');

        $systemprompt = 'You are a helpful assistant. Summarize the following text for a university student. The summary should be concise and capture the main points.';
        $payload = json_encode([
            'model' => $apimodel,
            'messages' => [
                ['role' => 'system', 'content' => $systemprompt],
                ['role' => 'user', 'content' => $textcontent],
            ],
            'temperature' => 0.5,
        ]);

        try {
            $response = $httpclient->post($apiendpoint, $payload);
            return $response;
        } catch (\Exception $e) {
            throw new \moodle_exception('error:apierror', 'mod_aisummarizer', '', null, $e->getMessage());
        }
    }

    /**
     * Extracts the text content from a file.
     *
     * Note: This is a simplified placeholder. A real implementation would need
     * to handle different file types (PDF, DOCX) using appropriate libraries
     * like pdftotext, unoconv, or cloud services.
     *
     * @param \stored_file $file The file to extract text from.
     * @return string The extracted text content.
     */
    public static function extract_text_from_file(\stored_file $file): string {
        // For this example, we only support plain text files.
        if ($file->get_mimetype() !== 'text/plain') {
            // In a real plugin, you would add converters for PDF, DOCX, etc. here.
            throw new \moodle_exception('error:unsupportedfiletype', 'mod_aisummarizer', $file->get_mimetype());
        }
        return $file->get_content();
    }
}
