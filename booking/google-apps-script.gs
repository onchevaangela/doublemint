/**
 * Double Mint Detailing booking backend (Google Apps Script).
 *
 * 1. Customer requests a time on the website -> a yellow "REQUEST" event goes on the calendar
 *    (the time is held so nobody else can take it) and the customer gets a "request received" email.
 * 2. The owners get an email with a "Review" button -> Confirm or Decline.
 * 3. Confirm -> event turns green, customer gets "you're confirmed" with a calendar file attached.
 *    Decline -> event is removed, customer gets a polite "please pick another time" email.
 * 4. Confirmed customers get a reminder email the evening before.
 *
 * Setup steps: booking/README.md
 */

// ---- settings -------------------------------------------------------------
var BUSINESS_NAME = 'Double Mint Detailing';
var PHONES = '862 238 0550 or 219 786 9863';
var SITE_URL = '';                      // e.g. 'https://doublemintdetailing.com' (shows the logo in emails)
var OWNER_EMAILS = [];                  // who gets new-request emails, e.g. ['a@gmail.com', 'b@gmail.com']; empty = this account
var CALENDAR_ID = 'primary';            // 'primary' = the calendar of the Google account that deploys this
var OPEN_HOURS = {                      // 24h "HH:MM" per weekday (0 = Sunday); missing = closed
  1: ['08:00', '18:00'],
  2: ['08:00', '18:00'],
  3: ['08:00', '18:00'],
  4: ['08:00', '18:00'],
  5: ['08:00', '18:00'],
  6: ['08:00', '18:00'],
};
var SLOT_STEP_MIN = 30;                 // start times offered every N minutes
var BUFFER_MIN = 15;                    // gap kept free after each job
var MIN_NOTICE_HOURS = 2;               // can't book sooner than this
var MAX_DAYS_AHEAD = 60;
var REMINDER_HOUR = 18;                 // reminder emails go out around this hour the day before
// ---------------------------------------------------------------------------

var PENDING = '⏳ REQUEST · ';

/** Run this once from the editor (select "setup", press Run). It asks for permissions and turns on reminders. */
function setup() {
  secret_();
  ScriptApp.getProjectTriggers().forEach(function (t) {
    if (t.getHandlerFunction() === 'sendReminders') ScriptApp.deleteTrigger(t);
  });
  ScriptApp.newTrigger('sendReminders').timeBased().everyDays(1).atHour(REMINDER_HOUR).create();
  Logger.log('Setup done. Calendar: ' + calendar_().getName() + ' (' + tz_() + ')');
}

// ---- web endpoints ----------------------------------------------------------

function doGet(e) {
  var p = e.parameter;
  try {
    if (p.action === 'slots') return json_({ ok: true, slots: openSlots_(p.date, clampMinutes_(p.minutes)) });
    if (p.action === 'review') return reviewPage_(p.id, p.sig);
    return json_({ ok: false, error: 'unknown_action' });
  } catch (err) {
    return json_({ ok: false, error: String(err.message || err) });
  }
}

function doPost(e) {
  var lock = LockService.getScriptLock();
  try {
    var b = JSON.parse(e.postData.contents);
    ['service', 'size', 'date', 'time', 'name', 'phone', 'email'].forEach(function (k) {
      if (!b[k] || String(b[k]).length > 200) throw new Error('missing_' + k);
    });
    if (!isEmail_(b.email)) throw new Error('bad_email');
    var minutes = clampMinutes_(b.minutes);
    lock.waitLock(20000);
    if (openSlots_(b.date, minutes).indexOf(b.time) === -1) return json_({ ok: false, error: 'slot_taken' });

    var start = at_(b.date, b.time);
    var end = new Date(start.getTime() + minutes * 60000);
    var info = {
      name: clean_(b.name).slice(0, 80), phone: clean_(b.phone).slice(0, 30), email: clean_(b.email).slice(0, 100), vehicle: clean_(b.vehicle).slice(0, 80),
      service: clean_(b.service), size: clean_(b.size), notes: clean_(b.notes).slice(0, 300),
      addons: (b.addons || []).slice(0, 5).map(function (a) { return clean_(a).slice(0, 40); }), total: Number(b.total) || 0,
    };
    var ev = calendar_().createEvent(PENDING + title_(info), start, end, { description: description_(info) });
    ev.setColor(CalendarApp.EventColor.YELLOW);
    ev.setTag('status', 'pending');
    ev.setTag('info', JSON.stringify(info));

    var when = whenText_(start);
    send_(info.email, 'We got your request: ' + when,
      '<h1>Thanks, ' + esc_(first_(info.name)) + '!</h1>' +
      '<p>We received your appointment request and will confirm it shortly. ' +
      'You\'ll get another email as soon as it\'s confirmed.</p>' + detailsTable_(info, when) +
      '<p class="muted">Need to change something? Call or text ' + PHONES + '.</p>');

    var link = ScriptApp.getService().getUrl() + '?action=review&id=' + encodeURIComponent(ev.getId()) +
      '&sig=' + sign_(ev.getId());
    send_(owners_().join(','), 'New request: ' + info.service + ' · ' + info.size + ' · ' + when,
      '<h1>New booking request</h1>' + detailsTable_(info, when) +
      '<p><b>Phone:</b> <a href="tel:' + esc_(info.phone) + '">' + esc_(info.phone) + '</a><br>' +
      '<b>Email:</b> ' + esc_(info.email) + (info.vehicle ? '<br><b>Vehicle:</b> ' + esc_(info.vehicle) : '') +
      (info.notes ? '<br><b>Notes:</b> ' + esc_(info.notes) : '') + '</p>' +
      '<p><a class="btn" href="' + link + '">Review &amp; confirm</a></p>' +
      '<p class="muted">The time is held on the calendar as a yellow REQUEST until you confirm or decline.</p>',
      info.email);
    return json_({ ok: true });
  } catch (err) {
    return json_({ ok: false, error: String(err.message || err) });
  } finally {
    lock.releaseLock();
  }
}

// ---- confirm / decline ------------------------------------------------------

function reviewPage_(id, sig) {
  var t = HtmlService.createTemplate(REVIEW_HTML);
  t.id = id; t.sig = sig; t.state = 'ok';
  var ev = verified_(id, sig);
  if (!ev) t.state = 'gone';
  else {
    t.info = JSON.parse(ev.getTag('info'));
    t.when = whenText_(ev.getStartTime());
    t.status = ev.getTag('status');
  }
  return t.evaluate().setTitle('Review booking').addMetaTag('viewport', 'width=device-width, initial-scale=1');
}

/** Called from the review page's buttons. */
function decide(id, sig, decision) {
  var ev = verified_(id, sig);
  if (!ev) return 'This request no longer exists.';
  if (ev.getTag('status') !== 'pending') return 'Already ' + ev.getTag('status') + '.';
  var info = JSON.parse(ev.getTag('info'));
  var start = ev.getStartTime(), end = ev.getEndTime(), when = whenText_(start);

  if (decision === 'confirm') {
    ev.setTitle(title_(info));
    ev.setColor(CalendarApp.EventColor.GREEN);
    ev.setTag('status', 'confirmed');
    ev.addPopupReminder(60);
    send_(info.email, 'Confirmed: ' + when,
      '<h1>You\'re confirmed! ✅</h1>' +
      '<p>Your appointment is confirmed for <b>' + esc_(when) + '</b>. See you then!</p>' +
      detailsTable_(info, when) +
      '<p><a class="btn" href="' + googleCalLink_(info, start, end) + '">Add to Google Calendar</a></p>' +
      '<p class="muted">On iPhone, open the attached file to add it to your calendar. ' +
      'Need to reschedule? Call or text ' + PHONES + '.</p>',
      null, [Utilities.newBlob(ics_(info, start, end), 'text/calendar', 'double-mint-appointment.ics')]);
    return 'Confirmed. ' + first_(info.name) + ' has been emailed.';
  }
  if (decision === 'decline') {
    ev.deleteEvent();
    send_(info.email, 'About your ' + when + ' request',
      '<h1>Sorry, ' + esc_(first_(info.name)) + '</h1>' +
      '<p>We can\'t make <b>' + esc_(when) + '</b> work. Please pick another time on our website, ' +
      'or call or text ' + PHONES + ' and we\'ll find a slot for you.</p>' +
      (SITE_URL ? '<p><a class="btn" href="' + SITE_URL + '/#book">Pick another time</a></p>' : ''));
    return 'Declined. ' + first_(info.name) + ' has been emailed and the time is free again.';
  }
  return 'Unknown action.';
}

/** Runs daily (see setup): reminds tomorrow's confirmed customers. */
function sendReminders() {
  var now = new Date();
  var tomorrow = Utilities.formatDate(new Date(now.getTime() + 864e5), tz_(), 'yyyy-MM-dd');
  calendar_().getEvents(at_(tomorrow, '00:00'), at_(tomorrow, '23:59')).forEach(function (ev) {
    if (ev.getTag('status') !== 'confirmed' || ev.getTag('reminded')) return;
    var info = JSON.parse(ev.getTag('info'));
    var when = whenText_(ev.getStartTime());
    send_(info.email, 'Reminder: see you tomorrow at ' + Utilities.formatDate(ev.getStartTime(), tz_(), 'h:mm a'),
      '<h1>See you tomorrow!</h1><p>Just a reminder of your appointment on <b>' + esc_(when) + '</b>.</p>' +
      detailsTable_(info, when) + '<p class="muted">Need to change it? Call or text ' + PHONES + '.</p>');
    ev.setTag('reminded', 'yes');
  });
}

// ---- availability -----------------------------------------------------------

function openSlots_(dateStr, minutes) {
  if (!/^\d{4}-\d{2}-\d{2}$/.test(dateStr || '')) throw new Error('bad_date');
  var dayStart = at_(dateStr, '00:00');
  var hours = OPEN_HOURS[Number(Utilities.formatDate(dayStart, tz_(), 'u')) % 7];
  if (!hours) return [];
  var now = new Date();
  if (dayStart.getTime() > now.getTime() + MAX_DAYS_AHEAD * 864e5) return [];

  var open = at_(dateStr, hours[0]), close = at_(dateStr, hours[1]);
  // pending requests block too; all-day events (birthdays, reminders) don't — add a timed "Closed" event to block time
  var busy = calendar_().getEvents(open, close).filter(function (ev) { return !ev.isAllDayEvent(); })
    .map(function (ev) { return [ev.getStartTime().getTime(), ev.getEndTime().getTime() + BUFFER_MIN * 60000]; });
  var earliest = now.getTime() + MIN_NOTICE_HOURS * 36e5;

  var slots = [];
  for (var t = open.getTime(); t + minutes * 60000 <= close.getTime(); t += SLOT_STEP_MIN * 60000) {
    var end = t + minutes * 60000;
    if (t < earliest) continue;
    if (!busy.some(function (r) { return t < r[1] && end > r[0]; })) slots.push(Utilities.formatDate(new Date(t), tz_(), 'HH:mm'));
  }
  return slots;
}

// ---- emails -----------------------------------------------------------------

function send_(to, subject, inner, replyTo, attachments) {
  var logo = SITE_URL ? '<img src="' + SITE_URL + '/assets/img/logo-email.png" alt="' + BUSINESS_NAME + '" width="220" style="display:block;margin:0 auto 8px">'
                      : '<div style="font:900 italic 24px Arial;color:#fff;text-align:center">DOUBLE <span style="color:#3BEA6B">MINT</span></div>';
  var html = '<div style="background:#f3f5f3;padding:24px 12px;font-family:Arial,Helvetica,sans-serif">' +
    '<div style="max-width:560px;margin:0 auto;background:#fff;border-radius:14px;overflow:hidden">' +
    '<div style="background:#0A0D0B;padding:22px">' + logo + '</div>' +
    '<div style="padding:24px 28px;color:#1b211d;font-size:15px;line-height:1.55">' +
    inner.replace(/<h1>/g, '<h1 style="font-size:22px;margin:0 0 12px">')
         .replace(/class="btn"/g, 'style="display:inline-block;background:#3BEA6B;color:#0A0D0B;font-weight:bold;padding:12px 22px;border-radius:999px;text-decoration:none"')
         .replace(/class="muted"/g, 'style="color:#6b756f;font-size:13px"') +
    '</div></div></div>';
  var opts = { to: to, subject: subject, htmlBody: html, name: BUSINESS_NAME };
  if (replyTo) opts.replyTo = replyTo;
  if (attachments) opts.attachments = attachments;
  MailApp.sendEmail(opts);
}

function detailsTable_(info, when) {
  var rows = [['When', when], ['Service', info.service + ' (' + info.size + ')']];
  if (info.addons.length) rows.push(['Add-ons', info.addons.join(', ')]);
  rows.push(['Total', '$' + info.total]);
  return '<table style="width:100%;border-collapse:collapse;margin:16px 0;font-size:15px">' + rows.map(function (r) {
    return '<tr><td style="padding:8px 0;color:#6b756f;border-bottom:1px solid #e6ebe7">' + r[0] +
      '</td><td style="padding:8px 0;text-align:right;font-weight:bold;border-bottom:1px solid #e6ebe7">' + esc_(r[1]) + '</td></tr>';
  }).join('') + '</table>';
}

function googleCalLink_(info, start, end) {
  var f = function (d) { return Utilities.formatDate(d, 'UTC', "yyyyMMdd'T'HHmmss'Z'"); };
  return 'https://calendar.google.com/calendar/render?action=TEMPLATE&text=' +
    encodeURIComponent(BUSINESS_NAME + ': ' + info.service) + '&dates=' + f(start) + '/' + f(end) +
    '&details=' + encodeURIComponent('Questions? Call or text ' + PHONES);
}

function ics_(info, start, end) {
  var f = function (d) { return Utilities.formatDate(d, 'UTC', "yyyyMMdd'T'HHmmss'Z'"); };
  return ['BEGIN:VCALENDAR', 'VERSION:2.0', 'PRODID:-//Double Mint//Booking//EN', 'METHOD:PUBLISH', 'BEGIN:VEVENT',
    'UID:' + Utilities.getUuid() + '@doublemint', 'DTSTAMP:' + f(new Date()), 'DTSTART:' + f(start), 'DTEND:' + f(end),
    'SUMMARY:' + BUSINESS_NAME + ': ' + info.service, 'DESCRIPTION:Questions? Call or text ' + PHONES,
    'END:VEVENT', 'END:VCALENDAR'].join('\r\n');
}

// ---- helpers ----------------------------------------------------------------

function title_(i) { return i.service + ' · ' + i.size + ' · ' + i.name; }
function description_(i) {
  return ['Customer: ' + i.name, 'Phone: ' + i.phone, 'Email: ' + i.email, i.vehicle ? 'Vehicle: ' + i.vehicle : '',
    'Service: ' + i.service + ' (' + i.size + ')', i.addons.length ? 'Add-ons: ' + i.addons.join(', ') : '',
    'Quoted total: $' + i.total, i.notes ? '\nNotes: ' + i.notes : '', '\nBooked online'].filter(String).join('\n');
}
function verified_(id, sig) {
  if (!id || !sig || sign_(id) !== sig) return null;
  try { return calendar_().getEventById(id); } catch (e) { return null; }
}
function secret_() {
  var props = PropertiesService.getScriptProperties();
  var s = props.getProperty('SECRET');
  if (!s) { s = Utilities.getUuid() + Utilities.getUuid(); props.setProperty('SECRET', s); }
  return s;
}
function sign_(id) { return Utilities.base64EncodeWebSafe(Utilities.computeHmacSha256Signature(id, secret_())).replace(/=+$/, ''); }
function owners_() { return OWNER_EMAILS.length ? OWNER_EMAILS : [Session.getEffectiveUser().getEmail()]; }
function calendar_() { return CalendarApp.getCalendarById(CALENDAR_ID) || CalendarApp.getDefaultCalendar(); }
function tz_() { return calendar_().getTimeZone(); }
function at_(dateStr, hhmm) { return Utilities.parseDate(dateStr + ' ' + hhmm, tz_(), 'yyyy-MM-dd HH:mm'); }
function whenText_(d) { return Utilities.formatDate(d, tz_(), "EEEE, MMMM d 'at' h:mm a"); }
function clampMinutes_(m) { return Math.min(600, Math.max(30, Number(m) || 60)); }
function clean_(s) { return String(s || '').slice(0, 500); }
function first_(name) { return String(name).split(' ')[0]; }
function isEmail_(s) { return /^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(s || ''); }
function esc_(s) { return String(s).replace(/[&<>"]/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]; }); }
function json_(obj) { return ContentService.createTextOutput(JSON.stringify(obj)).setMimeType(ContentService.MimeType.JSON); }

var REVIEW_HTML = [
  '<!doctype html><html><head><base target="_top"><style>',
  'body{margin:0;background:#0A0D0B;color:#F2F6F3;font:16px/1.5 Arial,Helvetica,sans-serif;padding:24px 16px}',
  '.card{max-width:480px;margin:0 auto;background:#141a16;border:1px solid #27302a;border-radius:16px;padding:24px}',
  'h1{font-size:22px;margin:0 0 4px}.muted{color:#9AA59E}.row{display:flex;justify-content:space-between;padding:8px 0;border-bottom:1px solid #27302a}',
  '.row b{text-align:right}button{font:bold 16px Arial;border:0;border-radius:999px;padding:14px;width:100%;margin-top:12px;cursor:pointer}',
  '.yes{background:#3BEA6B;color:#0A0D0B}.no{background:transparent;color:#ff8a8a;border:1px solid #5a2a2a}#msg{margin-top:16px;font-weight:bold;color:#3BEA6B}',
  'a{color:#3BEA6B}</style></head><body><div class="card">',
  '<? if (state === "gone") { ?><h1>Request not found</h1><p class="muted">It was already declined or removed.</p>',
  '<? } else { ?><h1><?= info.name ?></h1><p class="muted"><?= when ?></p>',
  '<div class="row"><span class="muted">Service</span><b><?= info.service ?> (<?= info.size ?>)</b></div>',
  '<? if (info.addons.length) { ?><div class="row"><span class="muted">Add-ons</span><b><?= info.addons.join(", ") ?></b></div><? } ?>',
  '<div class="row"><span class="muted">Total</span><b>$<?= info.total ?></b></div>',
  '<div class="row"><span class="muted">Phone</span><b><a href="tel:<?= info.phone ?>"><?= info.phone ?></a></b></div>',
  '<div class="row"><span class="muted">Email</span><b><?= info.email ?></b></div>',
  '<? if (info.vehicle) { ?><div class="row"><span class="muted">Vehicle</span><b><?= info.vehicle ?></b></div><? } ?>',
  '<? if (info.notes) { ?><p class="muted">Notes: <?= info.notes ?></p><? } ?>',
  '<? if (status === "pending") { ?><div id="actions" data-id="<?= id ?>" data-sig="<?= sig ?>"><button class="yes" onclick="go(\'confirm\')">Confirm appointment</button>',
  '<button class="no" onclick="go(\'decline\')">Decline</button></div><? } else { ?><p class="muted">Already <?= status ?>.</p><? } ?>',
  '<p id="msg"></p>',
  '<script>function go(d){if(d==="decline"&&!confirm("Decline this request? The customer will be emailed."))return;',
  'var a=document.getElementById("actions");a.style.display="none";document.getElementById("msg").textContent="Working…";',
  'google.script.run.withSuccessHandler(function(m){document.getElementById("msg").textContent=m;})',
  '.withFailureHandler(function(e){document.getElementById("msg").textContent="Error: "+e.message;})',
  '.decide(a.dataset.id,a.dataset.sig,d);}</script>',
  '<? } ?></div></body></html>',
].join('\n');
