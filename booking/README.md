# Online booking → one Google Calendar (also visible in Apple Calendar)

Bookings made on the website become events on **one Google Calendar**. You see them on your phone in
Google Calendar *or* the iPhone/Mac Calendar app. No paid service needed. Takes about 10 minutes, one time.

```
Customer books on website  →  Google Apps Script (free, runs in your Google account)
                           →  event on your Google Calendar + email to you + invite to the customer
                           →  shows up in Apple Calendar too (step 4)
```

## 1. Pick the Google account

Use the one email you want all appointments in (for example a new `doublemintdetailing@gmail.com`).
Sign in to it before the next steps.

## 2. Create the script

1. Go to <https://script.google.com> → **New project**. Name it `Double Mint Booking`.
2. Delete what's in `Code.gs`, paste everything from [`google-apps-script.gs`](google-apps-script.gs).
3. At the top, set your real hours in `OPEN_HOURS` (default: Mon–Sat 8 AM–6 PM, Sunday closed).
   Change `OWNER_EMAIL` if alerts should go to a different email.
4. Click **Save**.

## 3. Publish it and connect the website

1. **Deploy → New deployment** → gear icon → **Web app**.
2. *Execute as:* **Me**. *Who has access:* **Anyone**. Click **Deploy**.
3. Google asks for permission (Calendar + send email). Choose your account → *Advanced* → *Go to Double Mint Booking* → **Allow**.
   (The "unverified app" warning is normal: it's your own script.)
4. Copy the **Web app URL** (ends in `/exec`).
5. Paste it into `assets/js/config.js`:
   ```js
   bookingEndpoint: "https://script.google.com/macros/s/XXXX/exec",
   ```

Done. The site now shows only times that are actually free on your calendar, and blocks double-booking.
To block time off (lunch, day off), just add a normal timed event like "Closed" to that calendar.

If you edit the script later: **Deploy → Manage deployments → Edit → Version: New version → Deploy** (keeps the same URL).

## 4. See appointments in Apple Calendar (iPhone / Mac)

- **iPhone:** Settings → Apps → Calendar → Calendar Accounts → Add Account → **Google** → sign in with the booking email.
  Turn on *Calendars*. Appointments now appear in the iPhone Calendar app with alerts.
- **Mac:** Calendar → Settings → Accounts → **+** → Google.

Two people (both owners) can each add the same Google account to their phones, or the owner can share the
calendar with the other person's email from Google Calendar → Settings → *Share with specific people*.

## Before the backend is set up

With `bookingEndpoint` empty, the booking form still works: it opens a pre-filled text message to
862 238 0550 with the service, vehicle size, price and requested time.

## Prefer zero code?

Google Calendar has a built-in **Appointment schedule** (Google Calendar → Create → Appointment schedule)
that gives you a booking page on the same calendar. You could link the site's "Book" button to it instead,
but you lose the service/size/price picker and the times wouldn't account for how long each detail takes.
