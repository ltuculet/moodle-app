<?php
/**
 * A renderable class for the main view of the Gemini Summarizer.
 *
 * @package    mod_geminisummarizer
 * @copyright  2024 Your Name
 * @license    http://www.gnu.org/copyleft/gpl.html GNU GPL v3 or later
 */

namespace mod_geminisummarizer\output;

defined('MOODLE_INTERNAL') || die();

use renderable;
use templatable;
use stdClass;
use context_module;

class main_view implements renderable, templatable {
    /** @var stdClass The geminisummarizer activity record. */
    protected $geminisummarizer;

    /** @var context_module The context of the module. */
    protected $context;

    /** @var bool Whether the user has a valid OAuth token. */
    protected $hastoken;

    /**
     * Constructor.
     *
     * @param stdClass $geminisummarizer The activity record.
     * @param context_module $context The module context.
     * @param bool $hastoken Whether the user has a valid token.
     */
    public function __construct(stdClass $geminisummarizer, context_module $context, bool $hastoken) {
        $this->geminisummarizer = $geminisummarizer;
        $this->context = $context;
        $this->hastoken = $hastoken;
    }

    /**
     * Export this data so it can be used as the context for a template.
     *
     * @param \renderer_base $output
     * @return stdClass
     */
    public function export_for_template(\renderer_base $output): stdClass {
        $data = new stdClass();
        $data->id = $this->geminisummarizer->id;
        $data->name = $this->geminisummarizer->name;
        $data->contextid = $this->context->id;
        $data->cmid = $this->context->instanceid;
        $data->hastoken = $this->hastoken;

        // The URL to start the OAuth flow.
        $data->authurl = new \moodle_url('/mod/geminisummarizer/auth_start.php', ['cmid' => $this->context->instanceid]);

        // Check if the user has permission to submit.
        $data->cansubmit = has_capability('mod/geminisummarizer:submit', $this->context);

        return $data;
    }
}
