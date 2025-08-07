<?php
/**
 * The renderer for the AI Summarizer activity module.
 *
 * @package    mod_aisummarizer
 * @copyright  2024 Your Name
 * @license    http://www.gnu.org/copyleft/gpl.html GNU GPL v3 or later
 */

namespace mod_aisummarizer\output;

defined('MOODLE_INTERNAL') || die();

use plugin_renderer_base;
use renderable;
use stdClass;

/**
 * The renderer for the AI Summarizer activity module.
 */
class renderer extends plugin_renderer_base {

    /**
     * Renders the main view page for the AI Summarizer.
     *
     * This method prepares the data for the template that displays the
     * file upload form and the area for the generated summary.
     *
     * @param renderable $page The renderable object representing the view page.
     * @return string The rendered HTML.
     */
    protected function render_summary_view(renderable $page): string {
        $data = $page->export_for_template($this);
        return $this->render_from_template('mod_aisummarizer/summary_view', $data);
    }
}
