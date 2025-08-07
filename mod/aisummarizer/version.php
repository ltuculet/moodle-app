<?php
/**
 * Version details for the AI Summarizer activity module.
 *
 * @package    mod_aisummarizer
 * @copyright  2024 Your Name
 * @license    http://www.gnu.org/copyleft/gpl.html GNU GPL v3 or later
 */

defined('MOODLE_INTERNAL') || die();

$plugin->component = 'mod_aisummarizer';
$plugin->version = 2024080700; // YYYYMMDDXX (Date + increment)
$plugin->requires = 2023100900; // Moodle 4.3 release
$plugin->maturity = MATURITY_ALPHA;
$plugin->release = '0.1.0';
$plugin->dependencies = [
    'core' => 2023100900, // Moodle 4.3
];
$plugin->supported = [
    'moodle_403' => true,
    'moodle_404' => true,
    'moodle_500' => true,
];

$plugin->frankenstyle = 'mod_aisummarizer';
$plugin->submodules = [];

$plugin->capabilities = [
    'mod/aisummarizer:addinstance',
    'mod/aisummarizer:view',
    'mod/aisummarizer:submit',
    'mod/aisummarizer:viewsummary',
    'mod/aisummarizer:viewallsummaries',
];
