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
$plugin->requires = 2023100900; // Moodle 4.3 release
$plugin->maturity = MATURITY_ALPHA;
$plugin->release = '0.1.0';

// The new plugin will have a dependency on the OAuth 2 services API.
$plugin->dependencies = [
    'core' => 2023100900,
    'core_oauth2' => 2023100900,
];

$plugin->supported = [
    'moodle_403' => true,
    'moodle_404' => true,
    'moodle_500' => true,
];

$plugin->capabilities = [
    'mod/geminisummarizer:addinstance',
    'mod/geminisummarizer:view',
    'mod/geminisummarizer:submit',
    'mod/geminisummarizer:viewsummary',
    'mod/geminisummarizer:viewallsummaries',
];
