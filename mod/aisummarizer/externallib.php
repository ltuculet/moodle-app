<?php
/**
 * External API for the AI Summarizer module.
 *
 * @package    mod_aisummarizer
 * @copyright  2024 Your Name
 * @license    http://www.gnu.org/copyleft/gpl.html GNU GPL v3 or later
 */

defined('MOODLE_INTERNAL') || die();

require_once($CFG->dirroot . '/lib/externallib.php');
require_once($CFG->dirroot . '/mod/aisummarizer/classes/summary_service.php');

use external_api;
use external_function_parameters;
use external_single_structure;
use external_value;

class mod_aisummarizer_external extends external_api {

    /**
     * Define the parameters for the generate_summary web service.
     *
     * @return external_function_parameters
     */
    public static function generate_summary_parameters(): external_function_parameters {
        return new external_function_parameters([
            'contextid' => new external_value(PARAM_INT, 'The context id for the activity.'),
            'jsonformdata' => new external_value(PARAM_RAW, 'The data from the file picker form, JSON encoded.'),
            'aisummarizerid' => new external_value(PARAM_INT, 'The ID of the aisummarizer instance.'),
        ]);
    }

    /**
     * The web service implementation for generating a summary.
     *
     * @param int $contextid
     * @param string $jsonformdata
     * @param int $aisummarizerid
     * @return array
     */
    public static function generate_summary(int $contextid, string $jsonformdata, int $aisummarizerid): array {
        global $USER, $DB;

        self::validate_context($contextid);

        $formdata = json_decode($jsonformdata);
        if (!isset($formdata->userfile) || empty($formdata->userfile)) {
            throw new \moodle_exception('error:filerequired', 'mod_aisummarizer');
        }
        $itemid = $formdata->userfile;

        $fs = get_file_storage();
        $files = $fs->get_area_files($contextid, 'user', 'draft', $itemid);

        if (count($files) === 0) {
            throw new \moodle_exception('error:filerequired', 'mod_aisummarizer');
        }
        $file = reset($files);

        // For simplicity, we process the first file.
        $textcontent = \mod_aisummarizer\summary_service::extract_text_from_file($file);

        // Call the AI service.
        $response = \mod_aisummarizer\summary_service::generate_summary($textcontent);
        $responsebody = json_decode($response->body);

        if ($response->status !== 200 || !isset($responsebody->choices[0]->message->content)) {
            throw new \moodle_exception('error:apierror', 'mod_aisummarizer', $response->body);
        }

        $summarytext = $responsebody->choices[0]->message->content;

        // Save the summary to the database.
        $summaryrecord = new \stdClass();
        $summaryrecord->aisummarizerid = $aisummarizerid;
        $summaryrecord->userid = $USER->id;
        $summaryrecord->sourcefileid = $file->get_id(); // This might need adjustment based on final file handling.
        $summaryrecord->summarytext = $summarytext;
        $summaryrecord->summaryformat = FORMAT_MARKDOWN;
        $summaryrecord->timegenerated = time();
        $summaryrecord->id = $DB->insert_record('aisummarizer_summaries', $summaryrecord);

        // Trigger the summary generated event.
        $event = \mod_aisummarizer\event\summary_generated::create([
            'context' => self::validate_context($contextid),
            'objectid' => $summaryrecord->id,
            'relateduserid' => $USER->id,
        ]);
        $event->trigger();

        return [
            'status' => 'ok',
            'summary' => $summarytext,
        ];
    }

    /**
     * Define the return value for the generate_summary web service.
     *
     * @return external_single_structure
     */
    public static function generate_summary_returns(): external_single_structure {
        return new external_single_structure([
            'status' => new external_value(PARAM_TEXT, 'The status of the operation.'),
            'summary' => new external_value(PARAM_RAW, 'The generated summary text.'),
        ]);
    }
}
