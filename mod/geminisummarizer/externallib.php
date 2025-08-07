<?php
/**
 * External API for the Gemini Summarizer module.
 *
 * @package    mod_geminisummarizer
 * @copyright  2024 Your Name
 * @license    http://www.gnu.org/copyleft/gpl.html GNU GPL v3 or later
 */

defined('MOODLE_INTERNAL') || die();

require_once($CFG->dirroot . '/lib/externallib.php');
require_once($CFG->dirroot . '/mod/geminisummarizer/classes/gemini_service.php');

use external_api;
use external_function_parameters;
use external_single_structure;
use external_value;

class mod_geminisummarizer_external extends external_api {

    /**
     * Define the parameters for the generate_summary web service.
     *
     * @return external_function_parameters
     */
    public static function generate_summary_parameters(): external_function_parameters {
        return new external_function_parameters([
            'contextid' => new external_value(PARAM_INT, 'The context id for the activity.'),
            'jsonformdata' => new external_value(PARAM_RAW, 'The data from the file picker form, JSON encoded.'),
            'geminisummarizerid' => new external_value(PARAM_INT, 'The ID of the geminisummarizer instance.'),
        ]);
    }

    /**
     * The web service implementation for generating a summary.
     *
     * @param int $contextid
     * @param string $jsonformdata
     * @param int $geminisummarizerid
     * @return array
     */
    public static function generate_summary(int $contextid, string $jsonformdata, int $geminisummarizerid): array {
        global $USER, $DB;

        self::validate_context($contextid);
        require_capability('mod/geminisummarizer:submit', self::get_context_instance(self::CONTEXT_MODULE, $contextid));

        $formdata = json_decode($jsonformdata);
        if (!isset($formdata->userfile) || empty($formdata->userfile)) {
            throw new \moodle_exception('error:filerequired', 'mod_geminisummarizer');
        }
        $itemid = $formdata->userfile;

        $fs = get_file_storage();
        $files = $fs->get_area_files($contextid, 'user', 'draft', $itemid);

        if (count($files) === 0) {
            throw new \moodle_exception('error:filerequired', 'mod_geminisummarizer');
        }
        $file = reset($files);

        // Extract text from the file.
        $textcontent = \mod_geminisummarizer\gemini_service::extract_text_from_file($file);

        // Call the Gemini service, which handles user auth and the API call.
        $summarytext = \mod_geminisummarizer\gemini_service::generate_summary($USER->id, $textcontent);

        // Save the summary to the database.
        $summaryrecord = new \stdClass();
        $summaryrecord->geminisummarizerid = $geminisummarizerid;
        $summaryrecord->userid = $USER->id;
        $summaryrecord->summarytext = $summarytext;
        $summaryrecord->summaryformat = FORMAT_MARKDOWN;
        $summaryrecord->timegenerated = time();
        $DB->insert_record('geminisummarizer_summaries', $summaryrecord);

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
