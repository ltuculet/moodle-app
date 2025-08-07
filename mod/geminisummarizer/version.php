<?php
/**
 * Version details for the Gemini Summarizer activity module.
 *
 * @package    mod_geminisummarizer
 * @copyright  2024 Your Name
 * @license    http://www.gnu.org/copyleft/gpl.html GNU GPL v3 or later
 */

defined('MOODLE_INTERNAL') || die();

$plugin->component = 'mod_geminisummarizer';
$plugin->version = 2024080700; // YYYYMMDDXX (Date + increment)
$plugin->requires = 2024042200; // Moodle 4.5 release
$plugin->maturity = MATURITY_ALPHA;
$plugin->release = '0.1.0';

// The new plugin will have a dependency on the OAuth 2 services API.
$plugin->dependencies = [
    'core' => 2024042200, // Moodle 4.5
    'core_oauth2' => 2023100900, // This API is stable.
];

$plugin->supported = [
    (object)['release' => '4.5', 'tested' => true],
    (object)['release' => '5.0', 'tested' => true],
];

$plugin->capabilities = [
    'mod/geminisummarizer:addinstance',
    'mod/geminisummarizer:view',
    'mod/geminisummarizer:submit',
    'mod/geminisummarizer:viewsummary',
    'mod/geminisummarizer:viewallsummaries',
];
