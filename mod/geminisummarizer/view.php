<?php
/**
 * The main view page for the Gemini Summarizer activity module.
 *
 * @package    mod_geminisummarizer
 * @copyright  2024 Your Name
 * @license    http://www.gnu.org/copyleft/gpl.html GNU GPL v3 or later
 */

require_once(__DIR__ . '/../../config.php');
require_once(__DIR__ . '/lib.php');

$id = required_param('id', PARAM_INT); // Course module ID.

// Get the course module, course, and activity instance records.
$cm = get_coursemodule_from_id('geminisummarizer', $id, 0, false, MUST_EXIST);
$course = $DB->get_record('course', ['id' => $cm->course], '*', MUST_EXIST);
$geminisummarizer = $DB->get_record('geminisummarizer', ['id' => $cm->instance], '*', MUST_EXIST);

// Require login and course context.
require_login($course, true, $cm);
$context = context_module::instance($cm->id);
require_capability('mod/geminisummarizer:view', $context);

// Trigger the course module viewed event.
$event = \core\event\course_module_viewed::create([
    'context' => $context,
    'objectid' => $geminisummarizer->id,
]);
$event->add_record_snapshot('course_modules', $cm);
$event->add_record_snapshot('course', $course);
$event->add_record_snapshot('geminisummarizer', $geminisummarizer);
$event->trigger();

// Set up the page.
$PAGE->set_url('/mod/geminisummarizer/view.php', ['id' => $cm->id]);
$PAGE->set_title(format_string($geminisummarizer->name));
$PAGE->set_heading(format_string($course->fullname));
$PAGE->set_context($context);

// Check if the current user has a valid OAuth token.
$usertoken = $DB->get_record('geminisummarizer_usertokens', ['userid' => $USER->id]);
$hastoken = $usertoken && $usertoken->expiresat > time();

// Get the renderer.
$output = $PAGE->get_renderer('mod_geminisummarizer');

// Display the page header.
echo $output->header();

// Display the introduction.
if (trim(strip_tags($geminisummarizer->intro))) {
    echo $output->box(format_module_intro('geminisummarizer', $geminisummarizer, $cm->id), 'generalbox', 'intro');
}

// Create a renderable object to pass data to the template.
$renderable = new \mod_geminisummarizer\output\main_view($geminisummarizer, $context, $hastoken);
echo $output->render($renderable);


// Display the page footer.
echo $output->footer();
