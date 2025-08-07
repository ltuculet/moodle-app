<?php
/**
 * English language strings for the AI Summarizer activity module.
 *
 * @package    mod_aisummarizer
 * @copyright  2024 Your Name
 * @license    http://www.gnu.org/copyleft/gpl.html GNU GPL v3 or later
 */

defined('MOODLE_INTERNAL') || die();

$string['pluginname'] = 'AI Summarizer';
$string['pluginnameplural'] = 'AI Summarizers';
$string['modulename'] = 'AI Summarizer';
$string['modulename_help'] = 'The AI Summarizer activity module allows students to upload text-based documents (like PDF or DOCX) and receive an AI-generated summary. This helps in quickly grasping the key points of a resource.';
$string['modulename_link'] = 'mod/aisummarizer/view';
$string['aisummarizer:addinstance'] = 'Add a new AI Summarizer';
$string['aisummarizer:view'] = 'View AI Summarizer';
$string['aisummarizer:submit'] = 'Submit a document for summary';
$string['aisummarizer:viewsummary'] = 'View own summary';
$string['aisummarizer:viewallsummaries'] = 'View all summaries';

// Form strings
$string['name'] = 'Activity name';
$string['intro'] = 'Introduction';
$string['intro_help'] = 'A description of the activity.';

// View page strings
$string['uploaddocument'] = 'Upload a document to summarize';
$string['uploaddocument_help'] = 'Upload a text-based file (PDF, DOCX, TXT). The content will be sent to an AI service to generate a summary.';
$string['submitford summarization'] = 'Generate Summary';
$string['pleasewait'] = 'Please wait, generating summary...';
$string['summarygenerated'] = 'Summary Generated Successfully';
$string['summary'] = 'Summary';
$string['error:filerequired'] = 'A file is required to generate a summary.';
$string['error:apierror'] = 'Could not connect to the AI service. Please contact the site administrator.';

// Settings page
$string['settings:header'] = 'AI Provider Settings';
$string['settings:explanation'] = 'Configure the API credentials for the AI service used for summarization.';
$string['settings:apikey'] = 'API Key';
$string['settings:apikey_desc'] = 'The API key for the AI service.';
$string['settings:apiendpoint'] = 'API Endpoint';
$string['settings:apiendpoint_desc'] = 'The URL for the AI service API endpoint.';
$string['settings:apimodel'] = 'AI Model';
$string['settings:apimodel_desc'] = 'The specific model to use for summarization (e.g., gpt-3.5-turbo, gemini-pro).';
