# Gemini Summarizer (mod_geminisummarizer)

## Description

The Gemini Summarizer is a Moodle activity module that allows students to generate AI-powered summaries of text documents.

This plugin uses a "Bring Your Own Key" model. Each student must connect their own Google account, and all API usage is billed to their personal Google Cloud project associated with that account. This allows for granular control and avoids a single, site-wide API key and quota.

## Installation

1.  **Get the code:** Place the `geminisummarizer` directory in the `mod/` directory of your Moodle installation. The path should be `/path/to/moodle/mod/geminisummarizer`.
2.  **Log in to Moodle:** Log in to your Moodle site as an administrator.
3.  **Upgrade Moodle database:** Navigate to `Site administration > Notifications`. Moodle will detect the new plugin and guide you through the installation process.

## Configuration (Required)

This plugin requires setting up Google OAuth 2.0 credentials. This is a multi-step process.

### Step 1: Configure Google Cloud Project

1.  Go to the [Google Cloud Console](https://console.cloud.google.com/).
2.  Create a new project or select an existing one.
3.  **Enable APIs:** In the navigation menu, go to `APIs & Services > Library`. Search for and enable the **"Generative Language API"** (or "Vertex AI API" if you prefer).
4.  **Configure OAuth Consent Screen:** Go to `APIs & Services > OAuth consent screen`.
    *   Choose **"External"** user type.
    *   Fill in the required app information (app name, user support email, developer contact).
    *   **Add Scopes:** You do not need to add scopes here. The plugin will request them dynamically.
    *   **Add Test Users:** While your app is in "Testing" mode, you must add the Google accounts of all users who will test it.

### Step 2: Create OAuth 2.0 Credentials

1.  Go to `APIs & Services > Credentials`.
2.  Click `+ CREATE CREDENTIALS` and select `OAuth client ID`.
3.  **Application type:** Select `Web application`.
4.  **Name:** Give your client ID a descriptive name (e.g., "Moodle Gemini Plugin").
5.  **Authorized redirect URIs:** This is the most important step.
    *   Click `+ ADD URI`.
    *   Enter the full URL to the callback script in your Moodle installation. It will be:
        `https://your.moodle.site/mod/geminisummarizer/oauth_callback.php`
    *   Replace `your.moodle.site` with your Moodle's domain name.
6.  Click `CREATE`. You will be shown your **Client ID** and **Client Secret**. Copy these immediately as you will need them in the next step.

### Step 3: Configure the Plugin in Moodle

1.  Log in to Moodle as an administrator.
2.  Navigate to `Site administration > Plugins > Activity modules > Gemini Summarizer`.
3.  Enter the **Google OAuth Client ID** and **Google OAuth Client Secret** that you copied from the Google Cloud Console.
4.  Click "Save changes".

The plugin is now configured and ready to be used in courses.

## How to Use

1.  As a teacher, add the "Gemini Summarizer" activity to a course.
2.  When a student visits the activity for the first time, they will be prompted to "Connect Google Account".
3.  The student will be taken through the Google consent flow.
4.  After authorizing the app, they will be returned to the activity page and will now see the file upload interface.
5.  The student can then upload a `.txt` file and click "Generate Summary".

## License

This plugin is licensed under the [GNU GPL v3 or later](http://www.gnu.org/copyleft/gpl.html).
