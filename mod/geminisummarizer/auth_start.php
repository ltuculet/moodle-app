<?php
/**
 * Initiates the Google OAuth 2.0 flow for Gemini Summarizer.
 *
 * @package    mod_geminisummarizer
 * @copyright  2024 Your Name
 * @license    http://www.gnu.org/copyleft/gpl.html GNU GPL v3 or later
 */

require_once(__DIR__ . '/../../config.php');

// We need the course module id to redirect back to the activity later.
$cmid = required_param('cmid', PARAM_INT);

require_login();

// Get the OAuth client ID and secret from settings.
$clientid = get_config('mod_geminisummarizer', 'oauthclientid');
$clientsecret = get_config('mod_geminisummarizer', 'oauthclientsecret');

if (empty($clientid) || empty($clientsecret)) {
    throw new \moodle_exception('error:oauthnotconfigured', 'mod_geminisummarizer');
}

// Define the Google OAuth 2.0 issuer details.
// In a real Moodle plugin, this would be registered as a system-wide issuer.
// For this self-contained example, we define it here.
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

// Define the scopes required for the API.
// We need email to identify the user and potentially a scope for the AI service.
// For now, we'll request email and profile.
$scopes = 'email profile https://www.googleapis.com/auth/generative-language.tuning';

// The callback URL must be registered in the Google Cloud Console.
$redirecturl = new \moodle_url('/mod/geminisummarizer/oauth_callback.php');

// Create a login flow instance.
$login = new \core_oauth2\login($issuer, $scopes, $redirecturl);

// Store the course module ID in the state parameter so we can use it after the callback.
$login->set_state_param('cmid', $cmid);

// Generate the authorization URL and redirect the user.
$login->redirect();
