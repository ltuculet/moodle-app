<?php
/**
 * Settings for the Gemini Summarizer activity module.
 *
 * @package    mod_geminisummarizer
 * @copyright  2024 Your Name
 * @license    http://www.gnu.org/copyleft/gpl.html GNU GPL v3 or later
 */

defined('MOODLE_INTERNAL') || die();

if ($hassiteconfig) {
    // Create a new settings page for the plugin.
    $settings = new admin_settingpage(
        'mod_geminisummarizer_settings',
        get_string('settings:header', 'mod_geminisummarizer')
    );

    // Add a heading with an explanation.
    $settings->add(new admin_setting_heading(
        'mod_geminisummarizer/header',
        get_string('settings:header', 'mod_geminisummarizer'),
        get_string('settings:explanation', 'mod_geminisummarizer')
    ));

    // Google OAuth Client ID setting.
    $settings->add(new admin_setting_configtext(
        'mod_geminisummarizer/oauthclientid',
        get_string('settings:oauthclientid', 'mod_geminisummarizer'),
        get_string('settings:oauthclientid_desc', 'mod_geminisummarizer'),
        '',
        PARAM_TEXT
    ));

    // Google OAuth Client Secret setting.
    $settings->add(new admin_setting_configpasswordunmask(
        'mod_geminisummarizer/oauthclientsecret',
        get_string('settings:oauthclientsecret', 'mod_geminisummarizer'),
        get_string('settings:oauthclientsecret_desc', 'mod_geminisummarizer'),
        '',
        PARAM_TEXT
    ));

    // Add the page to the admin menu under "Plugins".
    $ADMIN->add('plugins', $settings);
}
