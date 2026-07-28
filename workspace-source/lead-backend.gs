/**
 * Huntsville Workspaces — Lead Backend (Google Apps Script)
 * ---------------------------------------------------------
 * Receives every "Request pricing & a tour" form submission from
 * work-spacehuntsville.web.app and:
 *   1. Appends the full lead (all attribution fields) to the "Leads" sheet
 *   2. Emails you a notification with every field
 *   3. Redirects the visitor to the site's thank-you page
 *
 * SETUP (do this inside a Google Sheet):
 *   Extensions → Apps Script → paste this whole file → Deploy → New deployment
 *   → Web app → Execute as: Me → Who has access: Anyone → Deploy.
 *   Copy the URL ending in /exec — that becomes LEAD_ENDPOINT in
 *   workspace_generator.py.
 *
 * Full step-by-step: see LEAD-TRACKING.md in this folder.
 */

// Where lead notifications are emailed. Change if you prefer another inbox.
var NOTIFY_EMAIL = "ajfreightservicesllc@gmail.com";

// Tab name for the ledger inside the spreadsheet.
var SHEET_NAME = "Leads";

// Fallback redirect if the form's _next field is ever missing.
var FALLBACK_REDIRECT = "https://work-spacehuntsville.web.app/thank-you/";

// Every field the site's forms send, in ledger column order.
var FIELDS = [
  "lead_id", "captured_at", "space_name", "space_address", "source", "metro",
  "name", "email", "phone", "space_type", "team_size",
  "page_url", "page_path", "referrer", "first_touch_at", "landing_page",
  "utm_source", "utm_medium", "utm_campaign", "utm_term", "utm_content", "gclid"
];

function doPost(e) {
  var p = (e && e.parameter) || {};
  try {
    // Honeypot: real visitors never fill _gotcha; silently drop bot spam.
    if (p._gotcha) return redirectPage(p._next);

    // 1) Append to the ledger sheet (created with headers on first lead).
    var ss = SpreadsheetApp.getActiveSpreadsheet();
    var sh = ss.getSheetByName(SHEET_NAME);
    if (!sh) {
      sh = ss.insertSheet(SHEET_NAME);
      sh.appendRow(["received_at"].concat(FIELDS));
      sh.setFrozenRows(1);
    }
    var row = [new Date()];
    for (var i = 0; i < FIELDS.length; i++) row.push(p[FIELDS[i]] || "");
    sh.appendRow(row);

    // 2) Email notification with every field.
    var subject = (p._subject || "New workspace lead") +
                  (p.space_name ? " — " + p.space_name : "");
    var lines = [];
    for (var j = 0; j < FIELDS.length; j++) {
      lines.push(FIELDS[j] + ": " + (p[FIELDS[j]] || ""));
    }
    MailApp.sendEmail(NOTIFY_EMAIL, subject, lines.join("\n"));
  } catch (err) {
    // Never strand the visitor on an error page — still redirect.
  }
  // 3) Send the visitor to the thank-you page.
  return redirectPage(p._next);
}

function redirectPage(url) {
  var target = url || FALLBACK_REDIRECT;
  var html = "<!doctype html>" +
    '<meta http-equiv="refresh" content="0;url=' + target + '">' +
    "<script>location.replace(" + JSON.stringify(target) + ")<\/script>" +
    "Redirecting…";
  return HtmlService.createHtmlOutput(html);
}

/** Optional: run once from the editor to confirm email permissions work. */
function testEmail() {
  MailApp.sendEmail(NOTIFY_EMAIL, "Lead backend test",
    "If you can read this, the lead backend can send you lead emails.");
}
