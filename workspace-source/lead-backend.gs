// Huntsville Workspaces - Lead Backend (Google Apps Script)
// Receives form submissions from work-spacehuntsville.web.app:
// 1) appends the lead to the "Leads" sheet
// 2) emails you a notification
// 3) redirects the visitor to the thank-you page
//
// Setup (inside the "Huntsville Workspaces - Leads" Google Sheet):
//   Extensions > Apps Script > paste this file > Save
//   Run testEmail once to grant permissions
//   Deploy > New deployment > Web app
//     Execute as: Me | Who has access: Anyone
//   Copy the URL ending in /exec -> becomes LEAD_ENDPOINT in
//   workspace_generator.py. Full guide: LEAD-TRACKING.md.
//
// Note: ASCII-only and line comments throughout so copy/paste into the
// Apps Script editor can never mangle a block comment into a syntax error.

var NOTIFY_EMAIL = "ajfreightservicesllc@gmail.com";
var SHEET_NAME = "Leads";
var FALLBACK_REDIRECT = "https://flexworkspace.online/thank-you/";

var FIELDS = [
  "lead_id", "captured_at", "space_name", "space_address", "source", "metro",
  "name", "email", "phone", "space_type", "team_size",
  "page_url", "page_path", "referrer", "first_touch_at", "landing_page",
  "utm_source", "utm_medium", "utm_campaign", "utm_term", "utm_content", "gclid"
];

function doPost(e) {
  var p = (e && e.parameter) || {};
  try {
    // Honeypot: bots fill _gotcha; drop them silently.
    if (p._gotcha) return redirectPage(p._next);

    // 1) Append to the ledger (headers created on first lead).
    var ss = SpreadsheetApp.getActiveSpreadsheet();
    var sh = ss.getSheetByName(SHEET_NAME);
    if (!sh) {
      sh = ss.insertSheet(SHEET_NAME);
      sh.appendRow(["received_at"].concat(FIELDS));
      sh.setFrozenRows(1);
    }
    var row = [new Date()];
    for (var i = 0; i < FIELDS.length; i++) {
      row.push(p[FIELDS[i]] || "");
    }
    sh.appendRow(row);

    // 2) Email notification with every field.
    var subject = (p._subject || "New workspace lead");
    if (p.space_name) subject = subject + " - " + p.space_name;
    var lines = [];
    for (var j = 0; j < FIELDS.length; j++) {
      lines.push(FIELDS[j] + ": " + (p[FIELDS[j]] || ""));
    }
    MailApp.sendEmail(NOTIFY_EMAIL, subject, lines.join("\n"));
  } catch (err) {
    // Never strand the visitor - still redirect below.
  }
  // 3) Send the visitor to the thank-you page.
  return redirectPage(p._next);
}

function redirectPage(url) {
  var target = url || FALLBACK_REDIRECT;
  var html = "<!doctype html>" +
    "<meta http-equiv='refresh' content='0;url=" + target + "'>" +
    "<a href='" + target + "'>Continue</a>";
  return HtmlService.createHtmlOutput(html);
}

// Optional: run this once from the editor to confirm email permission works.
function testEmail() {
  MailApp.sendEmail(NOTIFY_EMAIL, "Lead backend test",
    "If you can read this, the lead backend can send you lead emails.");
}
