<?php
/**
 * Service class for handling Gemini API integration and token management.
 *
 * @package    mod_geminisummarizer
 * @copyright  2024 Your Name
 * @license    http://www.gnu.org/copyleft/gpl.html GNU GPL v3 or later
 */

namespace mod_geminisummarizer;

defined('MOODLE_INTERNAL') || die();

use core\http\client;
use moodle_exception;
use stdClass;

class gemini_service {

    /**
     * Gets a valid access token for the user, refreshing it if necessary.
     *
     * @param int $userid The Moodle user ID.
     * @return string The valid access token.
     * @throws moodle_exception
     */
    public static function get_valid_access_token(int $userid): string {
        global $DB;
        $usertoken = $DB->get_record('geminisummarizer_usertokens', ['userid' => $userid]);

        if (!$usertoken) {
            throw new moodle_exception('error:notoken', 'mod_geminisummarizer');
        }

        // Check if the token is expired or about to expire (e.g., within 5 minutes).
        if ($usertoken->expiresat < (time() + 300)) {
            return self::refresh_token($usertoken);
        }

        return $usertoken->accesstoken;
    }

    /**
     * Refreshes an expired OAuth token.
     *
     * @param stdClass $usertoken The user token record from the database.
     * @return string The new access token.
     * @throws moodle_exception
     */
    private static function refresh_token(stdClass $usertoken): string {
        global $DB;

        $clientid = get_config('mod_geminisummarizer', 'oauthclientid');
        $clientsecret = get_config('mod_geminisummarizer', 'oauthclientsecret');

        if (empty($clientid) || empty($clientsecret)) {
            throw new moodle_exception('error:oauthnotconfigured', 'mod_geminisummarizer');
        }

        $http = new client();
        $url = 'https://oauth2.googleapis.com/token';
        $params = [
            'client_id' => $clientid,
            'client_secret' => $clientsecret,
            'refresh_token' => $usertoken->refreshtoken,
            'grant_type' => 'refresh_token',
        ];

        $response = $http->post($url, $params);
        $body = json_decode($response->body);

        if ($response->status !== 200 || !isset($body->access_token)) {
            // If refresh fails, the user may need to re-authenticate.
            // We should delete the invalid token record.
            $DB->delete_records('geminisummarizer_usertokens', ['id' => $usertoken->id]);
            throw new moodle_exception('error:tokenrefreshfailed', 'mod_geminisummarizer', '', null, $response->body);
        }

        // Update the database with the new token details.
        $usertoken->accesstoken = $body->access_token;
        $usertoken->expiresat = time() + $body->expires_in;
        $usertoken->timemodified = time();
        $DB->update_record('geminisummarizer_usertokens', $usertoken);

        return $usertoken->accesstoken;
    }

    /**
     * Generates a summary for the given text content using the Gemini API.
     *
     * @param int $userid The Moodle user ID of the user making the request.
     * @param string $textcontent The text to summarize.
     * @return string The summary text.
     * @throws moodle_exception
     */
    public static function generate_summary(int $userid, string $textcontent): string {
        $accesstoken = self::get_valid_access_token($userid);

        $http = new client();
        $http->set_header('Authorization', 'Bearer ' . $accesstoken);
        $http->set_header('Content-Type', 'application/json');

        // The Gemini API endpoint.
        $url = 'https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent';

        $payload = json_encode([
            'contents' => [
                [
                    'parts' => [
                        ['text' => 'Summarize the following text for a university student. The summary should be concise and capture the main points. Text to summarize: ' . $textcontent]
                    ]
                ]
            ]
        ]);

        $response = $http->post($url, $payload);
        $body = json_decode($response->body);

        if ($response->status !== 200 || !isset($body->candidates[0]->content->parts[0]->text)) {
            throw new moodle_exception('error:apierror', 'mod_geminisummarizer', '', null, $response->body);
        }

        return $body->candidates[0]->content->parts[0]->text;
    }

    /**
     * Extracts text content from a file (simplified for .txt files).
     *
     * @param \stored_file $file The file to extract text from.
     * @return string The extracted text content.
     * @throws moodle_exception
     */
    public static function extract_text_from_file(\stored_file $file): string {
        if ($file->get_mimetype() !== 'text/plain') {
            throw new moodle_exception('error:unsupportedfiletype', 'mod_geminisummarizer', $file->get_mimetype());
        }
        return $file->get_content();
    }
}
