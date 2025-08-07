<?php
/**
 * English language strings for the Gemini Summarizer activity module.
 *
 * @package    mod_geminisummarizer
 * @copyright  2024 Your Name
 * @license    http://www.gnu.org/copyleft/gpl.html GNU GPL v3 or later
 */

defined('MOODLE_INTERNAL') || die();

$string['pluginname'] = 'Gemini Summarizer';
$string['pluginnameplural'] = 'Gemini Summarizers';
$string['modulename'] = 'Gemini Summarizer';
$string['modulename_help'] = 'The Gemini Summarizer allows students to connect their Google account to generate summaries of documents using the Gemini API, with usage billed to their own account.';
$string['modulename_link'] = 'mod/geminisummarizer/view';

// Capabilities
$string['geminisummarizer:addinstance'] = 'Add a new Gemini Summarizer';
$string['geminisummarizer:view'] = 'View Gemini Summarizer';
$string['geminisummarizer:submit'] = 'Submit a document for summary';
$string['geminisummarizer:viewsummary'] = 'View own summary';
$string['geminisummarizer:viewallsummaries'] = 'View all summaries';

// Form strings
$string['name'] = 'Activity name';
$string['intro'] = 'Introduction';

// View page strings
$string['connectgoogle'] = 'Connect Google Account';
$string['connectgoogle_help'] = 'To use this tool, you need to connect your Google account. This will allow the service to use the Gemini API on your behalf. Usage will be associated with your Google account\'s API quota and billing.';
$string['uploaddocument'] = 'Upload a document to summarize';
$string['uploaddocument_help'] = 'Upload a text-based file. The content will be processed by the Gemini API using your connected Google account.';
$string['generatesummary'] = 'Generate Summary';
$string['pleasewait'] = 'Please wait, generating summary...';
$string['summary'] = 'Summary';

// Error messages
$string['error:oauthnotconfigured'] = 'The Google OAuth integration has not been configured by the site administrator. Please contact support.';
$string['error:filerequired'] = 'A file is required to generate a summary.';
$string['error:apierror'] = 'Could not connect to the Gemini service. Please check your account status or contact support.';

// Settings page
$string['settings:header'] = 'Gemini Summarizer Settings';
$string['settings:explanation'] = 'Configure the site-wide Google OAuth 2.0 credentials. These are required to allow users to connect their own Google accounts to use the Gemini API.';
$string['settings:oauthclientid'] = 'Google OAuth Client ID';
$string['settings:oauthclientid_desc'] = 'The Client ID obtained from the Google Cloud Console for your OAuth 2.0 credentials.';
$string['settings:oauthclientsecret'] = 'Google OAuth Client Secret';
$string['settings:oauthclientsecret_desc'] = 'The Client Secret obtained from the Google Cloud Console.';
