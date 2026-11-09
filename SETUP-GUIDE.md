# Going live: step-by-step

Two parts, about 30 minutes total. Do them in order.

- **Part 1:** put the website online with Cloudflare (free, plus about $10–11 a year for a domain)
- **Part 2:** turn on online booking with Google Calendar (free)

Use the business Gmail (for example `doublemintdetailing@gmail.com`) for Part 2.

---

## Part 1: Publish the website on Cloudflare

### 1. Create the account
1. Go to **dash.cloudflare.com** and sign up (free).

### 2. Buy the domain (optional, you can do it later)
1. In the left menu: **Domain Registration → Register Domains**.
2. Search `doublemintdetailing.com` (or your choice), add it, check out. Turn on **auto-renew**.
   Skip extra add-ons: privacy and SSL are already included free.

### 3. Connect the website
1. Left menu: **Workers & Pages → Create**.
2. Choose the **Pages** tab → **Import an existing Git repository**.
   (If Cloudflare suggests "Workers" instead, look for the *Pages* tab or a "Get started with Pages" link.)
3. Click **Connect GitHub**, sign in, and allow access to the **doublemint** repository.
4. Pick **doublemint** → **Begin setup**, then fill in:
   | Setting | Value |
   |---|---|
   | Project name | `doublemintdetailing` (this becomes `doublemintdetailing.pages.dev`) |
   | Production branch | `main` |
   | Framework preset | None |
   | Build command | *(leave empty)* |
   | Build output directory | `/` |
5. **Save and Deploy.** After about a minute the site is live at `https://doublemintdetailing.pages.dev`.

### 4. Add your domain (if you bought one)
1. Open the Pages project → **Custom domains → Set up a custom domain**.
2. Type `doublemintdetailing.com` → Continue → Activate. Repeat for `www.doublemintdetailing.com`.
3. Wait a few minutes. The padlock (https) is automatic.

From now on, every change saved to the `main` branch on GitHub goes live automatically within a minute or two.

---

## Part 2: Online booking with Google Calendar

### How it works

```
Customer clicks "Request appointment"
  ├─ A yellow "⏳ REQUEST" event goes on your Google Calendar (the time is held, nobody else can book it)
  ├─ Customer gets an email: "We got your request, we'll confirm shortly"
  └─ You (the owners) get an email with a "Review & confirm" button
        ├─ Confirm → event turns green, customer gets "You're confirmed for Tuesday at 9:00 AM"
        │            with a file to add it to their own calendar (works on iPhone and Android)
        └─ Decline → event is removed, customer gets "Sorry, please pick another time or call us"

The evening before, confirmed customers get a reminder email automatically.
```

All emails come from the business Gmail with the name "Double Mint Detailing".

### 1. Create the script
1. Sign in to the business Gmail, then go to **script.google.com → New project**.
2. Click "Untitled project" at the top and rename it **Double Mint Booking**.
3. Delete everything in the editor and paste in **all** of [`booking/google-apps-script.gs`](booking/google-apps-script.gs).
4. Change the settings at the top:
   - `OWNER_EMAILS`: who gets new requests, e.g. `['owner1@gmail.com', 'owner2@gmail.com']`.
     Leave it as `[]` to send them only to the business Gmail.
   - `OPEN_HOURS`: your real hours (right now Mon–Sat 8:00–18:00, Sunday closed).
   - `SITE_URL`: your website address once it's live, e.g. `'https://doublemintdetailing.com'`. This shows your logo in the emails.
5. Click **Save** (the disk icon).

### 2. Give it permission (one time)
1. In the toolbar's function dropdown, pick **setup**, then click **Run**.
2. Google asks for permission → choose the business account → **Advanced → Go to Double Mint Booking (unsafe) → Allow**.
   The warning appears because it's your own script, not an app from the store. That's normal.
3. The log should say "Setup done". This also turns on the reminder emails.

### 3. Publish it
1. **Deploy → New deployment** → click the gear → **Web app**.
2. *Execute as:* **Me** · *Who has access:* **Anyone** → **Deploy**.
3. Copy the **Web app URL** (it ends in `/exec`).

### 4. Connect it to the website
Send the URL to Claude, or do it yourself:
1. On GitHub open `assets/js/config.js` → pencil icon (Edit).
2. Paste the URL between the quotes: `bookingEndpoint: "https://script.google.com/macros/s/.../exec",`
3. **Commit changes**. Cloudflare updates the live site in a minute or two.

### 5. Test it
1. Book a test appointment on the website using your own email.
2. Check: yellow event on the calendar, "we got your request" email, owner email with **Review & confirm**.
3. Tap **Review & confirm → Confirm appointment**. The event turns green and the "confirmed" email arrives.
4. Delete the test event from the calendar.

### See bookings on your phones
- **iPhone:** Settings → Apps → Calendar → Calendar Accounts → Add Account → **Google** → sign in with the business Gmail (only *Calendars* needs to be on).
- **Android:** open Google Calendar → your profile picture → Add another account.
- Yellow = waiting for you to confirm. Green = confirmed.

### Good to know
- **Blocking time off:** add a normal event like "Closed" or "Lunch" to the calendar and the website won't offer those times.
- **Customer cancels by phone:** just delete the event; the time opens up again.
- **Changing the script later:** Deploy → Manage deployments → pencil → Version: **New version** → Deploy. The URL stays the same.
- **Email limit:** a free Gmail can send about 100 emails a day. Each booking uses 3–4, so that's plenty
  for roughly 25 bookings a day. Google Workspace raises the limit.
- **Before booking is connected,** the button opens a pre-filled text message to 862 238 0550 instead.
