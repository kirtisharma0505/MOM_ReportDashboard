# Setting Up Google Sheets API Credentials

Follow these steps to create and set up your Google Cloud credentials for accessing Google Sheets:

## 1. Create a Google Cloud Project

1. Go to the [Google Cloud Console](https://console.cloud.google.com/)
2. Click on "New Project" and create a new project
3. Give it a name (e.g., "Afina Sales Dashboard")
4. Click "Create"

## 2. Enable the Google Sheets API

1. In your project, go to "APIs & Services" > "Library"
2. Search for "Google Sheets API"
3. Click on it and then click "Enable"
4. Also enable the "Google Drive API" (search for it and enable)

## 3. Create Service Account Credentials

1. Go to "APIs & Services" > "Credentials"
2. Click "Create Credentials" > "Service Account"
3. Enter a name for your service account (e.g., "sheets-access")
4. Click "Create and Continue"
5. For Role, select "Project" > "Editor" (or a more restrictive role if you prefer)
6. Click "Continue" and then "Done"

## 4. Generate and Download JSON Key

1. In the Credentials page, click on the service account you just created
2. Go to the "Keys" tab
3. Click "Add Key" > "Create New Key"
4. Choose "JSON" and click "Create"
5. The JSON key file will be downloaded to your computer

## 5. Place the Credentials File in Your Project

1. Rename the downloaded JSON file to `credentials.json`
2. Place it in the same directory as your `main.py` file

## 6. Share Your Google Sheet

1. Open your Google Sheet
2. Click the "Share" button in the top right
3. Add the email address from your service account (found in the JSON file under "client_email")
4. Give it "Editor" access
5. Uncheck "Notify people" and click "Share"

## 7. Update Your Code

1. In `main.py`, make sure the `SHEET_NAME` variable matches the name of your sheet tab (usually "Sheet1")
2. Make sure the `SHEET_ID` is correct (it's the long string in your Google Sheet URL)

Now your application should be able to access your Google Sheet! 