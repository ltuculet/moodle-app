define([
    'jquery',
    'core/config',
    'core/ajax',
    'core/notification',
    'core_file/filepicker'
], function($, config, ajax, notification, filepicker) {

    var Summarizer = {
        init: function(containerSelector) {
            this.container = $(containerSelector);
            this.contextid = this.container.data('contextid');
            this.btn = this.container.find('#generate-summary-btn-' + this.getUniqid());
            this.fileUploadArea = this.container.find('#file-upload-area-' + this.getUniqid());
            this.loadingSpinner = this.container.find('#loading-spinner-' + this.getUniqid());
            this.summaryContent = this.container.find('#summary-content-' + this.getUniqid());
            this.errorMessage = this.container.find('#error-message-' + this.getUniqid());

            this.setupFilePicker();
            this.bindEvents();
        },

        getUniqid: function() {
            return this.container.attr('id').replace('aisummarizer-container-', '');
        },

        setupFilePicker: function() {
            var options = {
                contextid: this.contextid,
                itemid: 0, // 0 for draft files.
                accepted_types: ['.txt', '.pdf', '.docx'], // Example file types.
                maxfiles: 1
            };

            filepicker.init(this.fileUploadArea.attr('id'), options);

            // Enable the button when a file is selected.
            this.fileUploadArea.on('file-added', function() {
                this.btn.prop('disabled', false);
            }.bind(this));

            // Disable the button when the file is removed.
            this.fileUploadArea.on('file-removed', function() {
                this.btn.prop('disabled', true);
            }.bind(this));
        },

        bindEvents: function() {
            this.btn.on('click', function() {
                this.generateSummary();
            }.bind(this));
        },

        generateSummary: function() {
            this.showLoading(true);
            var formData = this.fileUploadArea.find('form').serialize();
            var params = new URLSearchParams(formData);
            var fileItemId = params.get('userfileitemid');

            var promise = ajax.call([{
                methodname: 'mod_aisummarizer_generate_summary',
                args: {
                    contextid: this.contextid,
                    jsonformdata: JSON.stringify({ userfile: fileItemId }),
                    aisummarizerid: config.cmid // Assuming cmid is the aisummarizerid, might need adjustment.
                },
                done: this.handleSuccess.bind(this),
                fail: this.handleFailure.bind(this)
            }]);
        },

        showLoading: function(show) {
            if (show) {
                this.loadingSpinner.removeClass('d-none');
                this.summaryContent.addClass('d-none');
                this.errorMessage.addClass('d-none');
                this.btn.prop('disabled', true);
            } else {
                this.loadingSpinner.addClass('d-none');
                this.btn.prop('disabled', false);
            }
        },

        handleSuccess: function(response) {
            this.showLoading(false);
            this.summaryContent.find('.card-body').html(response.summary);
            this.summaryContent.removeClass('d-none');
        },

        handleFailure: function(ex) {
            this.showLoading(false);
            this.errorMessage.text(ex.message || 'An unknown error occurred.');
            this.errorMessage.removeClass('d-none');
            notification.exception(ex);
        }
    };

    return {
        init: function(containerSelector) {
            Summarizer.init(containerSelector);
        }
    };
});
