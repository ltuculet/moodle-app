<?php
/**
 * Settings for the AI Summarizer activity module.
 *
 * @package    mod_aisummarizer
 * @copyright  2024 Your Name
 * @license    http://www.gnu.org/copyleft/gpl.html GNU GPL v3 or later
 */

defined('MOODLE_INTERNAL') || die();

if ($hassiteconfig) {
    // Create a new settings page.
    $settings = new admin_settingpage('mod_aisummarizer_settings', get_string('settings:header', 'mod_aisummarizer'));

    // Add a heading and explanation.
    $settings->add(new admin_setting_heading(
        'mod_aisummarizer/header',
        get_string('settings:header', 'mod_aisummarizer'),
        get_string('settings:explanation', 'mod_aisummarizer')
    ));

    // API Key setting.
    $settings->add(new admin_setting_configpasswordunmask(
        'mod_aisummarizer/apikey',
        get_string('settings:apikey', 'mod_aisummarizer'),
        get_string('settings:apikey_desc', 'mod_aisummarizer'),
        '',
        PARAM_TEXT
    ));

    // API Endpoint setting.
    $settings->add(new admin_setting_configtext(
        'mod_aisummarizer/apiendpoint',
        get_string('settings:apiendpoint', 'mod_aisummarizer'),
        get_string('settings:apiendpoint_desc', 'mod_aisummarizer'),
        'https://api.openai.com/v1/chat/completions', // Example default
        PARAM_URL
    ));

    // AI Model setting.
    $settings->add(new admin_setting_configtext(
        'mod_aisummarizer/apimodel',
        get_string('settings:apimodel', 'mod_aisummarizer'),
        get_string('settings:apimodel_desc', 'mod_aisummarizer'),
        'gpt-3.5-turbo', // Example default
        PARAM_TEXT
    ));

    // Add the page to the admin menu.
    $ADMIN->add('plugins', $settings);
}
