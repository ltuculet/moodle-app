@mod @mod_geminisummarizer
Feature: A student can connect their Google account and generate a summary
  In order to use the Gemini Summarizer
  As a student
  I need to be able to authorize the plugin with my Google account.

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
    And I add a "Gemini Summarizer" to section "1"
    And I set the following fields to these values:
      | Name | Test Gemini Summarizer |
    And I press "Save and display"
    And I log out
    # Note: A real test of the OAuth flow requires custom Behat steps
    # to mock the browser's redirect to an external site (Google) and
    # to mock the callback to our Moodle instance.

  Scenario: A student connects their account for the first time
    Given I log in as "student1"
    And I am on "Course 1" course homepage
    When I follow "Test Gemini Summarizer"
    Then I should see "Connect Google Account"
    And I should see a link with the text "Connect Google Account"
    # The following steps are conceptual and would require custom definitions.
    # And I click the "Connect Google Account" link
    # And the browser should be redirected to "accounts.google.com"
    # And I simulate a successful Google OAuth callback with user "student.one@gmail.com"
    # Then I should be redirected back to the "Test Gemini Summarizer" activity page
    # And I should see "Upload a document to summarize"
    # And I should not see "Connect Google Account"
