<?php
/**
 * The summary_generated event class.
 *
 * @package    mod_aisummarizer
 * @copyright  2024 Your Name
 * @license    http://www.gnu.org/copyleft/gpl.html GNU GPL v3 or later
 */

namespace mod_aisummarizer\event;

defined('MOODLE_INTERNAL') || die();

/**
 * The summary_generated event class.
 *
 * This event is triggered when a user successfully generates a summary.
 */
class summary_generated extends \core\event\base {

    /**
     * Init method.
     */
    protected function init() {
        $this->data['crud'] = 'c'; // c for created.
        $this->data['edulevel'] = self::LEVEL_PARTICIPATING;
        $this->data['objecttable'] = 'aisummarizer_summaries';
    }

    /**
     * Returns a description of the event.
     *
     * @return string
     */
    public function get_description(): string {
        return "The user with id '{$this->userid}' generated a new summary with id '{$this->objectid}' in the aisummarizer activity with course module id '{$this->contextinstanceid}'.";
    }

    /**
     * Returns the URL related to the event.
     *
     * @return \moodle_url
     */
    public function get_url(): \moodle_url {
        return new \moodle_url('/mod/aisummarizer/view.php', ['id' => $this->contextinstanceid]);
    }

    /**
     * Returns the legacy event data for backwards compatibility.
     *
     * @return array
     */
    public static function get_legacy_mapping(): array {
        return []; // No legacy event to map to.
    }
}
