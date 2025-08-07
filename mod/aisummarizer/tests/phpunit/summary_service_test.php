<?php
/**
 * Unit tests for the summary_service class.
 *
 * @package    mod_aisummarizer
 * @copyright  2024 Your Name
 * @license    http://www.gnu.org/copyleft/gpl.html GNU GPL v3 or later
 */

namespace mod_aisummarizer\tests;

defined('MOODLE_INTERNAL') || die();

use advanced_testcase;
use mod_aisummarizer\summary_service;

/**
 * Unit tests for the summary_service class.
 *
 * Note: Testing a class with external dependencies like http clients and file systems
 * typically requires mocking those dependencies. This is a simplified example.
 */
class summary_service_test extends advanced_testcase {

    /**
     * Test that the text extraction function works for plain text.
     */
    public function test_extract_text_from_plain_file() {
        $this->resetAfterTest();

        $testcontent = 'This is a test file content.';
        // In a real test, we would mock the stored_file object.
        // For this example, we create a temporary mock object.
        $mockfile = $this->createMock(\stored_file::class);
        $mockfile->method('get_mimetype')->willReturn('text/plain');
        $mockfile->method('get_content')->willReturn($testcontent);

        $extractedtext = summary_service::extract_text_from_file($mockfile);

        $this->assertEquals($testcontent, $extractedtext);
    }

    /**
     * Test that text extraction throws an error for unsupported file types.
     */
    public function test_extract_text_throws_exception_for_unsupported_type() {
        $this->resetAfterTest();

        $this->expectException(\moodle_exception::class);
        $this->expectExceptionMessage('error:unsupportedfiletype');

        $mockfile = $this->createMock(\stored_file::class);
        $mockfile->method('get_mimetype')->willReturn('image/jpeg');

        summary_service::extract_text_from_file($mockfile);
    }

    /**
     * Test that generate_summary throws an exception if API keys are not configured.
     *
     * @group moodleconfig
     */
    public function test_generate_summary_throws_exception_if_no_config() {
        $this->resetAfterTest();

        // Ensure config is not set for this test.
        unset_config('apikey', 'mod_aisummarizer');

        $this->expectException(\moodle_exception::class);
        $this->expectExceptionMessage('error:apiconfigmissing');

        summary_service::generate_summary('Some text');
    }
}
