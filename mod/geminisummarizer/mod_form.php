<?php
/**
 * The form for editing the Gemini Summarizer activity module.
 *
 * @package    mod_geminisummarizer
 * @copyright  2024 Your Name
 * @license    http://www.gnu.org/copyleft/gpl.html GNU GPL v3 or later
 */

defined('MOODLE_INTERNAL') || die();

require_once($CFG->dirroot . '/course/moodleform_mod.php');

/**
 * The form for editing the Gemini Summarizer activity module.
 */
class mod_geminisummarizer_mod_form extends moodleform_mod {
    /**
     * Defines the form structure.
     */
    public function definition() {
        $mform = $this->_form;

        // Standard activity elements.
        $mform->addElement('header', 'general', get_string('general', 'form'));

        // Activity name.
        $mform->addElement('text', 'name', get_string('name', 'mod_geminisummarizer'), ['size' => '64']);
        if (!empty($CFG->formatstringstriptags)) {
            $mform->setType('name', PARAM_TEXT);
        } else {
            $mform->setType('name', PARAM_RAW);
        }
        $mform->addRule('name', null, 'required', null, 'client');
        $mform->addRule('name', get_string('maximumchars', '', 255), 'maxlength', 255, 'client');
        $mform->addHelpButton('name', 'name', 'mod_geminisummarizer');

        // Introduction editor.
        $this->add_intro_editor(true, get_string('intro', 'mod_geminisummarizer'));

        // Standard Moodle module elements.
        $this->standard_coursemodule_elements();

        // Action buttons.
        $this->add_action_buttons();
    }
}
