@mod @mod_aisummarizer
Feature: A student can generate a summary from a file
  In order to quickly understand a document
  As a student
  I need to be able to upload a file and get a summary

  Background:
    Given the following "users" exist:
      | username | firstname | lastname | email |
      | teacher1 | Teacher | 1 | teacher1@example.com |
      | student1 | Student | 1 | student1@example.com |
    And the following "courses" exist:
      | fullname | shortname | category |
      | Course 1 | C1 | 0 |
    And the following "course enrolments" exist:
      | user | course | role |
      | teacher1 | C1 | editingteacher |
      | student1 | C1 | student |
    And I log in as "teacher1"
    And I am on "Course 1" course homepage with editing mode on
    And I add a "AI Summarizer" to section "1"
    And I set the following fields to these values:
      | Name | Test Summarizer |
      | Introduction | Please upload a file to summarize. |
    And I press "Save and display"
    And I log out
    # Note: For a real test of the AI feature, the Behat environment would
    # need a way to mock the external AI service call. This can be done with
    # custom step definitions and tools like WireMock. This example tests the UI flow.

  Scenario: A student uploads a file and sees a placeholder for the summary
    Given I log in as "student1"
    And I am on "Course 1" course homepage
    When I follow "Test Summarizer"
    Then I should see "Upload a document to summarize"
    And the "Generate Summary" "button" should be disabled
    # Step to upload a file. This requires a file in the Behat data directory.
    And I upload "mod/aisummarizer/tests/fixtures/sample.txt" to "userfile" filemanager
    And the "Generate Summary" "button" should be enabled
    # We cannot test the actual click and summary generation without mocking the API call.
    # A custom step could be: And I click "Generate Summary" and the AI service responds successfully
    # Then I should see "Summary Generated Successfully"
    # And I should see "This is a test summary." in the "summary-content" "css_element"
