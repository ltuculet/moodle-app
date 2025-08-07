<?php
/**
 * Web service definitions for the AI Summarizer module.
 *
 * @package    mod_aisummarizer
 * @copyright  2024 Your Name
 * @license    http://www.gnu.org/copyleft/gpl.html GNU GPL v3 or later
 */

defined('MOODLE_INTERNAL') || die();

$functions = [
    'mod_aisummarizer_generate_summary' => [
        'classname' => 'mod_aisummarizer_external',
        'methodname' => 'generate_summary',
        'classpath' => 'mod/aisummarizer/externallib.php',
        'description' => 'Generates a summary for a given file.',
        'type' => 'write',
        'ajax' => true,
        'capabilities' => 'mod/aisummarizer:submit',
    ],
];

$services = [
    'mod_aisummarizer' => [
        'functions' => ['mod_aisummarizer_generate_summary'],
        'restrictedusers' => 0,
        'enabled' => 1,
        'shortname' => 'AI Summarizer Service',
    ]
];
