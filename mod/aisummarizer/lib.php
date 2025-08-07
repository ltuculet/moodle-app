<?php
/**
 * Library of functions and constants for the AI Summarizer activity module.
 *
 * @package    mod_aisummarizer
 * @copyright  2024 Your Name
 * @license    http://www.gnu.org/copyleft/gpl.html GNU GPL v3 or later
 */

defined('MOODLE_INTERNAL') || die();

/**
 * Given a course and an instance of aisummarizer, this function will
 * backup the contents of the instance.
 *
 * @param MoodleQuickForm $mform
 * @return stdClass
 */
function aisummarizer_add_instance(stdClass $aisummarizer, mod_aisummarizer_mod_form $mform = null): int {
    global $DB;

    $aisummarizer->timecreated = time();
    $aisummarizer->timemodified = $aisummarizer->timecreated;

    // Get the text from the form.
    $data = $mform->get_data();
    $aisummarizer->intro = $data->intro['text'];
    $aisummarizer->introformat = $data->intro['format'];

    $aisummarizer->id = $DB->insert_record('aisummarizer', $aisummarizer);

    return $aisummarizer->id;
}

/**
 * Given a course and an instance of aisummarizer, this function will
 * update the contents of the instance.
 *
 * @param stdClass $aisummarizer
 * @param MoodleQuickForm $mform
 * @return bool
 */
function aisummarizer_update_instance(stdClass $aisummarizer, mod_aisummarizer_mod_form $mform = null): bool {
    global $DB;

    $aisummarizer->timemodified = time();
    $aisummarizer->id = $aisummarizer->instance;

    // Get the text from the form.
    $data = $mform->get_data();
    $aisummarizer->intro = $data->intro['text'];
    $aisummarizer->introformat = $data->intro['format'];

    return $DB->update_record('aisummarizer', $aisummarizer);
}

/**
 * Given an ID of an instance of this module, this function will
 * permanently delete the instance and any data that depends on it.
 *
 * @param int $id
 * @return bool
 */
function aisummarizer_delete_instance(int $id): bool {
    global $DB;

    if (!$aisummarizer = $DB->get_record('aisummarizer', ['id' => $id])) {
        return false;
    }

    // Delete associated summaries.
    $DB->delete_records('aisummarizer_summaries', ['aisummarizerid' => $aisummarizer->id]);
    // Delete the main activity instance.
    $DB->delete_records('aisummarizer', ['id' => $aisummarizer->id]);

    return true;
}

/**
 * Returns a list of features that this module supports.
 *
 * @param string $feature FEATURE_... constant for requested feature
 * @return mixed True if module supports feature, false otherwise, null if doesn't know
 */
function aisummarizer_supports(string $feature): ?bool {
    switch ($feature) {
        case FEATURE_MOD_INTRO:
            return true;
        case FEATURE_SHOW_DESCRIPTION:
            return true;
        case FEATURE_BACKUP_MOODLE2:
            return true;
        case FEATURE_COMPLETION_TRACKS_VIEWS:
            return true;
        case FEATURE_GRADE_HAS_GRADE:
            return false; // No grading for now.
        case FEATURE_GRADE_OUTCOMES:
            return false;
        default:
            return null;
    }
}
