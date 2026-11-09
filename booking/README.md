# Online booking

`google-apps-script.gs` is the booking backend. It runs free inside the business Google account:

- website requests go on the Google Calendar as yellow **REQUEST** events (the time is held),
- the customer gets a "request received" email, the owners get a **Review & confirm** email,
- Confirm turns the event green and emails the customer their confirmation (with a calendar file),
  Decline removes it and asks the customer to pick another time,
- confirmed customers get a reminder email the evening before.

**Setup steps:** see [Part 2 of SETUP-GUIDE.md](../SETUP-GUIDE.md#part-2-online-booking-with-google-calendar).
