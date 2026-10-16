/**
 * Double Mint Detailing booking backend (Google Apps Script).
 * Puts every website booking on ONE Google Calendar, checks for double-bookings,
 * and emails the owner. Setup steps: booking/README.md
 */

// ---- settings -------------------------------------------------------------
var CALENDAR_ID = 'primary';            // 'primary' = the calendar of the Google account that deploys this
var OWNER_EMAIL = '';                   // where new-booking alerts go; empty = the deploying account
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
var SEND_CUSTOMER_INVITE = true;        // add the customer as a guest so they get a calendar invite
// ---------------------------------------------------------------------------

function doGet(e) {
  try {
    var p = e.parameter;
    if (p.action !== 'slots') return json({ ok: false, error: 'unknown_action' });
    return json({ ok: true, slots: openSlots(p.date, clampMinutes(p.minutes)) });
  } catch (err) {
    return json({ ok: false, error: String(err.message || err) });
  }
}

function doPost(e) {
  var lock = LockService.getScriptLock();
  try {
    var b = JSON.parse(e.postData.contents);
    ['service', 'size', 'date', 'time', 'name', 'phone'].forEach(function (k) {
      if (!b[k] || String(b[k]).length > 200) throw new Error('missing_' + k);
    });
    var minutes = clampMinutes(b.minutes);
    lock.waitLock(20000);
    if (openSlots(b.date, minutes).indexOf(b.time) === -1) return json({ ok: false, error: 'slot_taken' });

    var start = at(b.date, b.time);
    var end = new Date(start.getTime() + minutes * 60000);
    var addons = (b.addons || []).map(String).slice(0, 10);
    var title = b.service + ' · ' + b.size + ' · ' + clean(b.name);
    var details = [
      'Customer: ' + clean(b.name),
      'Phone: ' + clean(b.phone),
      b.email ? 'Email: ' + clean(b.email) : '',
      b.vehicle ? 'Vehicle: ' + clean(b.vehicle) : '',
      'Service: ' + b.service + ' (' + b.size + ')',
      addons.length ? 'Add-ons: ' + addons.join(', ') : '',
      'Quoted total: $' + Number(b.total || 0),
      b.notes ? '\nNotes: ' + clean(b.notes) : '',
      '\nBooked online at doublemint website',
    ].filter(String).join('\n');

    var opts = { description: details };
    if (SEND_CUSTOMER_INVITE && /^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(b.email || '')) {
      opts.guests = b.email;
      opts.sendInvites = true;
    }
    var ev = calendar().createEvent(title, start, end, opts);
    ev.setColor(CalendarApp.EventColor.GREEN);
    ev.addPopupReminder(60);

    MailApp.sendEmail(OWNER_EMAIL || Session.getEffectiveUser().getEmail(),
      'New booking: ' + title + ' — ' + Utilities.formatDate(start, tz(), 'EEE MMM d, h:mm a'),
      details);
    return json({ ok: true });
  } catch (err) {
    return json({ ok: false, error: String(err.message || err) });
  } finally {
    lock.releaseLock();
  }
}

function openSlots(dateStr, minutes) {
  if (!/^\d{4}-\d{2}-\d{2}$/.test(dateStr || '')) throw new Error('bad_date');
  var dayStart = at(dateStr, '00:00');
  var hours = OPEN_HOURS[Number(Utilities.formatDate(dayStart, tz(), 'u')) % 7];
  if (!hours) return [];
  var now = new Date();
  if (dayStart.getTime() > now.getTime() + MAX_DAYS_AHEAD * 864e5) return [];

  var open = at(dateStr, hours[0]), close = at(dateStr, hours[1]);
  var busy = calendar().getEvents(open, close).filter(function (ev) {
    return !ev.isAllDayEvent(); // all-day events (birthdays, reminders) don't block; add a timed "Closed" event to block time
  }).map(function (ev) {
    return [ev.getStartTime().getTime(), ev.getEndTime().getTime() + BUFFER_MIN * 60000];
  });
  var earliest = now.getTime() + MIN_NOTICE_HOURS * 36e5;

  var slots = [];
  for (var t = open.getTime(); t + minutes * 60000 <= close.getTime(); t += SLOT_STEP_MIN * 60000) {
    var end = t + minutes * 60000;
    if (t < earliest) continue;
    var clash = busy.some(function (r) { return t < r[1] && end > r[0]; });
    if (!clash) slots.push(Utilities.formatDate(new Date(t), tz(), 'HH:mm'));
  }
  return slots;
}

// ---- helpers ----------------------------------------------------------------
function calendar() { return CalendarApp.getCalendarById(CALENDAR_ID) || CalendarApp.getDefaultCalendar(); }
function tz() { return calendar().getTimeZone(); }
function at(dateStr, hhmm) { return Utilities.parseDate(dateStr + ' ' + hhmm, tz(), 'yyyy-MM-dd HH:mm'); }
function clampMinutes(m) { return Math.min(600, Math.max(30, Number(m) || 60)); }
function clean(s) { return String(s || '').slice(0, 500); }
function json(obj) {
  return ContentService.createTextOutput(JSON.stringify(obj)).setMimeType(ContentService.MimeType.JSON);
}
