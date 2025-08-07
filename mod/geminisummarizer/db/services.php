<?php
/**
 * Web service definitions for the Gemini Summarizer module.
 *
 * @package    mod_geminisummarizer
 * @copyright  2024 Your Name
 * @license    http://www.gnu.org/copyleft/gpl.html GNU GPL v3 or later
 */

defined('MOODLE_INTERNAL') || die();

$functions = [
    'mod_geminisummarizer_generate_summary' => [
        'classname' => 'mod_geminisummarizer_external',
        'methodname' => 'generate_summary',
        'classpath' => 'mod/geminisummarizer/externallib.php',
        'description' => 'Generates a summary for a given file using the user\'s own Gemini account.',
        'type' => 'write',
        'ajax' => true,
        'capabilities' => 'mod/geminisummarizer:submit',
    ],
];

$services = [
    'mod_geminisummarizer' => [
        'functions' => ['mod_geminisummarizer_generate_summary'],
        'restrictedusers' => 0,
        'enabled' => 1,
        'shortname' => 'Gemini Summarizer Service',
    ]
];
