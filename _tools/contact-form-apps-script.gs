/**
 * Contact form receiver for flcassociates.com (Google Apps Script web app).
 *
 * Setup (once, signed in to the firm's Google Workspace account):
 * 1. Create a Google Sheet named "Website enquiries" and open Extensions > Apps Script.
 * 2. Paste this file, save, then Deploy > New deployment > Web app:
 *    Execute as: Me; Who has access: Anyone.
 * 3. Copy the web app URL into FORM_ENDPOINT in contact.html (build.py).
 *
 * Each enquiry is added as a row and emailed to NOTIFY_TO. Nothing else is stored.
 */
var NOTIFY_TO = "info@flcassociates.com";

function doPost(e) {
  var d = {};
  try { d = JSON.parse(e.postData.contents); } catch (err) { return out_("bad request"); }
  if (d.website) return out_("ok");                      // spam trap
  var clip = function (v, n) { return String(v || "").slice(0, n); };
  var row = [new Date(), clip(d.name, 120), clip(d.email, 160), clip(d.phone, 40), clip(d.area, 60), clip(d.message, 3000)];
  if (!row[1] || !row[2] || !row[5]) return out_("missing fields");
  SpreadsheetApp.getActiveSpreadsheet().getSheets()[0].appendRow(row);
  MailApp.sendEmail({
    to: NOTIFY_TO,
    replyTo: row[2],
    subject: "Website enquiry: " + row[4] + " (" + row[1] + ")",
    body: "Name: " + row[1] + "\nEmail: " + row[2] + "\nTelephone: " + row[3] + "\nArea: " + row[4] + "\n\n" + row[5]
  });
  return out_("ok");
}

function out_(msg) {
  return ContentService.createTextOutput(msg).setMimeType(ContentService.MimeType.TEXT);
}
