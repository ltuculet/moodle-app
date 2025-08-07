<?php
/**
 * The main view page for the AI Summarizer activity module.
 *
 * @package    mod_aisummarizer
 * @copyright  2024 Your Name
 * @license    http://www.gnu.org/copyleft/gpl.html GNU GPL v3 or later
 */

require_once(__DIR__ . '/../../config.php');
require_once(__DIR__ . '/lib.php');

$id = required_param('id', PARAM_INT); // Course module ID.

// Get the course module record.
$cm = get_coursemodule_from_id('aisummarizer', $id, 0, false, MUST_EXIST);
// Get the course record.
$course = $DB->get_record('course', ['id' => $cm->course], '*', MUST_EXIST);
// Get the activity instance record.
$aisummarizer = $DB->get_record('aisummarizer', ['id' => $cm->instance], '*', MUST_EXIST);

// Require login and course context.
require_login($course, true, $cm);
$context = context_module::instance($cm->id);
require_capability('mod/aisummarizer:view', $context);

// Trigger the course module viewed event.
$event = \mod_aisummarizer\event\course_module_viewed::create([
    'context' => $context,
    'objectid' => $aisummarizer->id,
]);
$event->add_record_snapshot('course_modules', $cm);
$event->add_record_snapshot('course', $course);
$event->add_record_snapshot('aisummarizer', $aisummarizer);
$event->trigger();

// Set up the page.
$PAGE->set_url('/mod/aisummarizer/view.php', ['id' => $cm->id]);
$PAGE->set_title(format_string($aisummarizer->name));
$PAGE->set_heading(format_string($course->fullname));
$PAGE->set_context($context);

// Get the renderer.
$output = $PAGE->get_renderer('mod_aisummarizer');

// Display the page header.
echo $output->header();

// Display the introduction.
if (trim(strip_tags($aisummarizer->intro))) {
    echo $output->box(format_module_intro('aisummarizer', $aisummarizer, $cm->id), 'generalbox', 'intro');
}

// Render the main content for the view page.
echo $output->render_summary_view($aisummarizer, $context);

// Display the page footer.
echo $output->footer();
