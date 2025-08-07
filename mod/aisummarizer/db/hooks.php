<?php
/**
 * Hooks definition for the AI Summarizer module.
 *
 * @package    mod_aisummarizer
 * @copyright  2024 Your Name
 * @license    http://www.gnu.org/copyleft/gpl.html GNU GPL v3 or later
 */

defined('MOODLE_INTERNAL') || die();

$hooks = [
    'after_summary_generated' => [
        'description' => 'Allows other plugins to take action after a summary has been generated and saved.',
        'since' => '4.3',
        'callback_signature' => [
            'name' => 'callback',
            'since' => '4.3',
            'parameters' => [
                [
                    'name' => 'summary',
                    'type' => 'stdClass',
                    'description' => 'The summary record from the database.',
                ],
                [
                    'name' => 'aisummarizer',
                    'type' => 'stdClass',
                    'description' => 'The aisummarizer activity instance record.',
                ],
            ],
            'return' => [
                'type' => 'void',
                'description' => 'The callback is not expected to return a value.',
            ],
        ],
    ],
];
