<?php
/**
 * Library of functions and constants for the Gemini Summarizer activity module.
 *
 * @package    mod_geminisummarizer
 * @copyright  2024 Your Name
 * @license    http://www.gnu.org/copyleft/gpl.html GNU GPL v3 or later
 */

defined('MOODLE_INTERNAL') || die();

/**
 * Adds a new instance of a geminisummarizer to a course.
 *
 * @param stdClass $geminisummarizer
 * @param mod_geminisummarizer_mod_form $mform
 * @return int
 */
function geminisummarizer_add_instance(stdClass $geminisummarizer, mod_geminisummarizer_mod_form $mform = null): int {
    global $DB;

    $geminisummarizer->timecreated = time();
    $geminisummarizer->timemodified = $geminisummarizer->timecreated;

    $data = $mform->get_data();
    $geminisummarizer->intro = $data->intro['text'];
    $geminisummarizer->introformat = $data->intro['format'];

    $geminisummarizer->id = $DB->insert_record('geminisummarizer', $geminisummarizer);

    return $geminisummarizer->id;
}

/**
 * Updates an instance of a geminisummarizer in a course.
 *
 * @param stdClass $geminisummarizer
 * @param mod_geminisummarizer_mod_form $mform
 * @return bool
 */
function geminisummarizer_update_instance(stdClass $geminisummarizer, mod_geminisummarizer_mod_form $mform = null): bool {
    global $DB;

    $geminisummarizer->timemodified = time();
    $geminisummarizer->id = $geminisummarizer->instance;

    $data = $mform->get_data();
    $geminisummarizer->intro = $data->intro['text'];
    $geminisummarizer->introformat = $data->intro['format'];

    return $DB->update_record('geminisummarizer', $geminisummarizer);
}

/**
 * Deletes an instance of this module.
 *
 * @param int $id
 * @return bool
 */
function geminisummarizer_delete_instance(int $id): bool {
    global $DB;

    if (!$geminisummarizer = $DB->get_record('geminisummarizer', ['id' => $id])) {
        return false;
    }

    // Delete associated user tokens and summaries.
    $DB->delete_records('geminisummarizer_usertokens', ['geminisummarizerid' => $geminisummarizer->id]);
    $DB->delete_records('geminisummarizer_summaries', ['geminisummarizerid' => $geminisummarizer->id]);
    // Delete the main activity instance.
    $DB->delete_records('geminisummarizer', ['id' => $geminisummarizer->id]);

    return true;
}

/**
 * Returns a list of features that this module supports.
 *
 * @param string $feature FEATURE_... constant for requested feature
 * @return mixed True if module supports feature, false otherwise, null if doesn't know
 */
function geminisummarizer_supports(string $feature): ?bool {
    switch ($feature) {
        case FEATURE_MOD_INTRO:
            return true;
        case FEATURE_SHOW_DESCRIPTION:
            return true;
        case FEATURE_BACKUP_MOODLE2:
            return true;
        case FEATURE_COMPLETION_TRACKS_VIEWS:
            return true;
        default:
            return null;
    }
}
