<?php
/**
 * Handles the Google OAuth 2.0 callback.
 *
 * @package    mod_geminisummarizer
 * @copyright  2024 Your Name
 * @license    http://www.gnu.org/copyleft/gpl.html GNU GPL v3 or later
 */

require_once(__DIR__ . '/../../config.php');

global $DB, $USER;

require_login();

// Get the OAuth client ID and secret from settings.
$clientid = get_config('mod_geminisummarizer', 'oauthclientid');
$clientsecret = get_config('mod_geminisummarizer', 'oauthclientsecret');

if (empty($clientid) || empty($clientsecret)) {
    throw new \moodle_exception('error:oauthnotconfigured', 'mod_geminisummarizer');
}

// Define the issuer again, just like in auth_start.php.
$issuer = new \core_oauth2\issuer(
    'google',
    $clientid,
    $clientsecret,
    'https://accounts.google.com/o/oauth2/v2/auth',
    'https://oauth2.googleapis.com/token',
    [
        'userinfo' => 'https://www.googleapis.com/oauth2/v3/userinfo'
    ]
);

// Process the login callback. This validates the state and exchanges the code for tokens.
$tokens = \core_oauth2\login::process($issuer);

// Use the token to get user info from Google.
$userinfo = \core_oauth2\api::get_userinfo($issuer, $tokens);

// Save or update the tokens in the database for the current Moodle user.
$record = $DB->get_record('geminisummarizer_usertokens', ['userid' => $USER->id]);
if (!$record) {
    $record = new stdClass();
    $record->userid = $USER->id;
}

$record->googleemail = $userinfo['email'];
$record->accesstoken = $tokens->get_access_token();
$record->refreshtoken = $tokens->get_refresh_token();
$record->expiresat = $tokens->get_expiry();
$record->timemodified = time();

if (isset($record->id)) {
    $DB->update_record('geminisummarizer_usertokens', $record);
} else {
    $DB->insert_record('geminisummarizer_usertokens', $record);
}

// Retrieve the original cmid from the state parameter.
$stateparams = \core_oauth2\state::get_state_params();
$cmid = $stateparams['cmid'];

if (empty($cmid)) {
    // If we lost the cmid, redirect to the dashboard.
    redirect(new \moodle_url('/my/'));
} else {
    // Redirect back to the activity page.
    $url = new \moodle_url('/mod/geminisummarizer/view.php', ['id' => $cmid]);
    redirect($url);
}
