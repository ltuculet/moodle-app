<?php
/**
 * The renderer for the Gemini Summarizer activity module.
 *
 * @package    mod_geminisummarizer
 * @copyright  2024 Your Name
 * @license    http://www.gnu.org/copyleft/gpl.html GNU GPL v3 or later
 */

namespace mod_geminisummarizer\output;

defined('MOODLE_INTERNAL') || die();

use plugin_renderer_base;
use renderable;

class renderer extends plugin_renderer_base {

    /**
     * Renders the main view page for the Gemini Summarizer.
     *
     * @param main_view $page The renderable object representing the view page.
     * @return string The rendered HTML.
     */
    protected function render_main_view(main_view $page): string {
        $data = $page->export_for_template($this);
        return $this->render_from_template('mod_geminisummarizer/gemini_view', $data);
    }
}
