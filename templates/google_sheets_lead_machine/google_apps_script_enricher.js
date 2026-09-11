/**
 * Google Sheets 1-Click B2B Lead Extractor
 * Powered by Apify Google Maps Business Search (captainhandsome/googlemaps)
 *
 * How to install:
 * 1. In your Google Sheet, click Extensions > Apps Script.
 * 2. Delete any existing code, paste this entire file, and click Save (disk icon).
 * 3. Refresh your spreadsheet. A new menu "Lead Machine" will appear at the top.
 */

function onOpen() {
  const ui = SpreadsheetApp.getUi();
  ui.createMenu('Lead Machine')
    .addItem('Fetch Fresh Leads', 'fetchGoogleMapsLeads')
    .addToUi();
}

function fetchGoogleMapsLeads() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const configSheet = ss.getSheetByName('Settings') || ss.getActiveSheet();
  
  // Read configuration parameters from Settings sheet
  const apiKey = configSheet.getRange('B1').getValue().toString().trim();
  const query = configSheet.getRange('B2').getValue().toString().trim();
  const location = configSheet.getRange('B3').getValue().toString().trim();
  const maxResults = parseInt(configSheet.getRange('B4').getValue(), 10) || 25;

  if (!apiKey || apiKey === 'YOUR_APIFY_TOKEN') {
    SpreadsheetApp.getUi().alert('Please enter your Apify API Token in cell B1 of the Settings sheet.');
    return;
  }

  if (!query) {
    SpreadsheetApp.getUi().alert('Please enter a Search Term (e.g., HVAC Contractors) in cell B2.');
    return;
  }

  const leadsSheet = ss.getSheetByName('Leads') || ss.insertSheet('Leads');
  
  // Set up header row if sheet is empty
  if (leadsSheet.getLastRow() === 0) {
    const headers = [
      'Business Name',
      'Phone',
      'Website',
      'Rating',
      'Review Count',
      'Category',
      'Address',
      'Google Maps URL'
    ];
    leadsSheet.appendRow(headers);
    leadsSheet.getRange(1, 1, 1, headers.length).setFontWeight('bold').setBackground('#E2E8F0');
  }

  SpreadsheetApp.getActiveSpreadsheet().toast('Starting Apify search for: ' + query + ' (' + location + ')...', 'Working', 5);

  const actorUrl = 'https://api.apify.com/v2/acts/captainhandsome~googlemaps/run-sync-get-dataset-items?token=' + encodeURIComponent(apiKey);
  
  const payload = {
    searchQueries: [query + ' in ' + location],
    maxResultsPerQuery: maxResults
  };

  const options = {
    method: 'post',
    contentType: 'application/json',
    payload: JSON.stringify(payload),
    muteHttpExceptions: true
  };

  try {
    const response = UrlFetchApp.fetch(actorUrl, options);
    const statusCode = response.getResponseCode();
    
    if (statusCode !== 200 && statusCode !== 201) {
      SpreadsheetApp.getUi().alert('Apify API Error (' + statusCode + '): ' + response.getContentText().substring(0, 300));
      return;
    }

    const items = JSON.parse(response.getContentText());
    if (!Array.isArray(items) || items.length === 0) {
      SpreadsheetApp.getUi().alert('Search finished, but no leads were returned. Check query or location.');
      return;
    }

    const rows = [];
    for (var i = 0; i < items.length; i++) {
      var item = items[i];
      rows.push([
        item.title || item.name || '',
        item.phone || item.phoneNumber || '',
        item.website || item.url || '',
        item.totalScore || item.rating || '',
        item.reviewsCount || item.reviews || 0,
        item.categoryName || item.category || '',
        item.address || '',
        item.placeUrl || item.mapsUrl || ''
      ]);
    }

    if (rows.length > 0) {
      const startRow = leadsSheet.getLastRow() + 1;
      leadsSheet.getRange(startRow, 1, rows.length, rows[0].length).setValues(rows);
      SpreadsheetApp.getUi().alert('Success! Added ' + rows.length + ' new leads to the Leads tab.');
    }
  } catch (err) {
    SpreadsheetApp.getUi().alert('Execution failed: ' + err.message);
  }
}
