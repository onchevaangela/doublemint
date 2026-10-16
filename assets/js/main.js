(function () {
  const C = window.DM_CONFIG;
  const $ = (sel, root = document) => root.querySelector(sel);
  const money = (n) => "$" + n.toLocaleString("en-US");
  const esc = (s) => String(s).replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));

  const state = {
    size: "car",
    service: (C.services.find((s) => s.featured) || C.services[0]).id,
    addons: new Set(),
    date: null,
    time: null,
  };
  const service = () => C.services.find((s) => s.id === state.service);
  const sizeLabel = () => C.sizes.find((s) => s.id === state.size).label;
  const addonList = () => C.addons.filter((a) => state.addons.has(a.id));
  const total = () => service().prices[state.size] + addonList().reduce((n, a) => n + a.price, 0);
  const minutes = () => service().minutes + addonList().reduce((n, a) => n + a.minutes, 0);

  /* ---------------- pricing section ---------------- */
  const toggle = $("[data-size-toggle]");
  toggle.innerHTML = C.sizes.map((s) =>
    `<button type="button" role="radio" data-size="${s.id}">${s.label}s</button>`).join("");
  toggle.addEventListener("click", (e) => {
    const b = e.target.closest("[data-size]");
    if (b) setSize(b.dataset.size);
  });

  function renderCards() {
    $("[data-services]").innerHTML = C.services.map((s) => `
      <article class="card${s.featured ? " featured" : ""}">
        ${s.featured ? '<span class="badge">Most popular</span>' : ""}
        <h3>${esc(s.name)}</h3>
        <div class="price"><sup>$</sup><span>${s.prices[state.size]}</span></div>
        <p class="per">per ${sizeLabel().toLowerCase()}</p>
        <ul class="ticks">${s.includes.map((i) => `<li>${esc(i)}</li>`).join("")}</ul>
        <a href="#book" class="btn ${s.featured ? "btn-mint" : "btn-ghost"}" data-book="${s.id}">Book this</a>
      </article>`).join("");
    toggle.querySelectorAll("[data-size]").forEach((b) =>
      b.setAttribute("aria-checked", String(b.dataset.size === state.size)));
  }
  $("[data-services]").addEventListener("click", (e) => {
    const a = e.target.closest("[data-book]");
    if (!a) return;
    state.service = a.dataset.book;
    const input = $(`input[name="service"][value="${state.service}"]`);
    if (input) input.checked = true;
    onChoiceChange();
  });

  const ICONS = {
    engine: '<path d="M4 10h3l2-3h6v3h3v3h2v-4h1v8h-1v-2h-2v3h-4l-2 2H7v-4H4z"/><path d="M2 12v4"/>',
    pet: '<circle cx="6" cy="10" r="2"/><circle cx="10" cy="6" r="2"/><circle cx="14" cy="6" r="2"/><circle cx="18" cy="10" r="2"/><path d="M8 17c0-3 2-5 4-5s4 2 4 5c0 2-2 2-4 2s-4 0-4-2Z"/>',
  };
  $("[data-addons]").innerHTML = C.addons.map((a) => `
    <div class="addon">
      <div class="ico"><svg viewBox="0 0 24 24" aria-hidden="true">${ICONS[a.id] || ""}</svg></div>
      <div><h3>${esc(a.name)}</h3><p>Add to any detail</p></div>
      <div class="amt">+${money(a.price)}</div>
    </div>`).join("");

  /* ---------------- booking form ---------------- */
  const form = $("[data-booking]");
  $("[data-pick-service]").innerHTML = C.services.map((s) => `
    <label class="choice"><input type="radio" name="service" value="${s.id}"${s.id === state.service ? " checked" : ""}>
      <span>${esc(s.name)}<small data-svc-price="${s.id}"></small></span></label>`).join("");
  $("[data-pick-size]").innerHTML = C.sizes.map((s) => `
    <label class="choice"><input type="radio" name="size" value="${s.id}"${s.id === state.size ? " checked" : ""}>
      <span>${s.label}</span></label>`).join("");
  $("[data-pick-addons]").innerHTML = C.addons.map((a) => `
    <label class="choice"><input type="checkbox" name="addon" value="${a.id}">
      <span>${esc(a.name)}<small>+${money(a.price)}</small></span></label>`).join("");

  form.addEventListener("change", (e) => {
    const t = e.target;
    if (t.name === "service") state.service = t.value;
    else if (t.name === "size") return setSize(t.value);
    else if (t.name === "addon") t.checked ? state.addons.add(t.value) : state.addons.delete(t.value);
    else return;
    onChoiceChange();
  });

  function setSize(id) {
    state.size = id;
    const input = $(`input[name="size"][value="${id}"]`);
    if (input) input.checked = true;
    renderCards();
    onChoiceChange();
  }

  function onChoiceChange() {
    C.services.forEach((s) => { $(`[data-svc-price="${s.id}"]`).textContent = money(s.prices[state.size]); });
    renderSummary();
    if (state.date) loadSlots(); // duration may have changed
  }

  // days
  const days = [];
  for (let i = 0, d = new Date(); days.length < C.daysAhead && i < C.daysAhead * 2; i++) {
    const day = new Date(d.getFullYear(), d.getMonth(), d.getDate() + i);
    if (!C.closedWeekdays.includes(day.getDay())) days.push(day);
  }
  const iso = (d) => `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}-${String(d.getDate()).padStart(2, "0")}`;
  $("[data-days]").innerHTML = days.map((d) => `
    <button type="button" class="day" role="radio" aria-checked="false" data-date="${iso(d)}">
      <span class="dow">${d.toLocaleDateString("en-US", { weekday: "short" })}</span>
      <span class="dom">${d.getDate()}</span>
      <span class="mon">${d.toLocaleDateString("en-US", { month: "short" })}</span>
    </button>`).join("");
  $("[data-days]").addEventListener("click", (e) => {
    const b = e.target.closest("[data-date]");
    if (!b) return;
    state.date = b.dataset.date;
    state.time = null;
    $("[data-days]").querySelectorAll(".day").forEach((x) => x.setAttribute("aria-checked", String(x === b)));
    loadSlots();
    renderSummary();
  });

  const slotsEl = $("[data-slots]");
  slotsEl.innerHTML = '<p class="slots-msg">Pick a day to see open times.</p>';
  slotsEl.addEventListener("click", (e) => {
    const b = e.target.closest("[data-time]");
    if (!b) return;
    state.time = b.dataset.time;
    slotsEl.querySelectorAll(".slot").forEach((x) => x.setAttribute("aria-checked", String(x === b)));
    renderSummary();
  });

  // Without a booking backend, offer every half hour 8am–6pm that fits the job.
  function localSlots() {
    const out = [];
    for (let m = 8 * 60; m + minutes() <= 18 * 60; m += 30) out.push(`${String(m / 60 | 0).padStart(2, "0")}:${String(m % 60).padStart(2, "0")}`);
    return out;
  }

  let slotReq = 0;
  async function loadSlots() {
    const req = ++slotReq;
    let slots;
    if (C.bookingEndpoint) {
      slotsEl.innerHTML = '<p class="slots-msg">Checking the calendar…</p>';
      try {
        const url = `${C.bookingEndpoint}?action=slots&date=${state.date}&minutes=${minutes()}`;
        const res = await (await fetch(url)).json();
        if (!res.ok) throw new Error(res.error);
        slots = res.slots;
      } catch (err) {
        if (req === slotReq) slotsEl.innerHTML = '<p class="slots-msg">Couldn\'t load times. Please call or text us.</p>';
        return;
      }
    } else {
      slots = localSlots();
    }
    if (req !== slotReq) return;
    if (!slots.includes(state.time)) state.time = null;
    slotsEl.innerHTML = slots.length
      ? slots.map((t) => `<button type="button" class="slot" role="radio" aria-checked="${t === state.time}" data-time="${t}">${fmtTime(t)}</button>`).join("")
      : '<p class="slots-msg">Fully booked that day. Try another date.</p>';
    renderSummary();
  }

  function fmtTime(t) {
    const [h, m] = t.split(":").map(Number);
    return `${(h + 11) % 12 + 1}:${String(m).padStart(2, "0")} ${h < 12 ? "AM" : "PM"}`;
  }
  function fmtDate(s) {
    const [y, m, d] = s.split("-").map(Number);
    return new Date(y, m - 1, d).toLocaleDateString("en-US", { weekday: "short", month: "short", day: "numeric" });
  }
  function fmtDuration(min) {
    const h = Math.floor(min / 60), m = min % 60;
    return [h && `${h} hr`, m && `${m} min`].filter(Boolean).join(" ");
  }

  function renderSummary() {
    const rows = [
      ["Service", service().name],
      ["Vehicle", sizeLabel()],
      ...addonList().map((a) => [a.name, "+" + money(a.price)]),
      ["When", state.date ? fmtDate(state.date) + (state.time ? ", " + fmtTime(state.time) : "") : "Pick a time"],
      ["Takes about", fmtDuration(minutes())],
    ];
    $("[data-summary]").innerHTML = rows.map(([k, v]) => `<div><dt>${esc(k)}</dt><dd>${esc(v)}</dd></div>`).join("");
    $("[data-total]").textContent = money(total());
    $("[data-hint]").textContent = state.time ? "" : "Choose a date and time to continue.";
  }

  $("[data-mode-note]").textContent = C.bookingEndpoint
    ? "You'll get a calendar confirmation by email. Pay after the job."
    : "This opens a pre-filled text to us. We'll confirm your time.";

  const msg = $("[data-msg]");
  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    msg.className = "form-msg";
    msg.textContent = "";
    let bad = null;
    ["name", "phone"].forEach((n) => {
      const el = form.elements[n];
      const invalid = !el.value.trim();
      el.setAttribute("aria-invalid", String(invalid));
      if (invalid && !bad) bad = el;
    });
    const email = form.elements.email;
    if (email.value && !email.checkValidity()) { email.setAttribute("aria-invalid", "true"); bad = bad || email; }
    else email.setAttribute("aria-invalid", "false");
    if (!state.time) return fail("Please pick a date and time.");
    if (bad) { bad.focus(); return fail("Please add your name and phone number."); }

    const booking = {
      service: service().name,
      size: sizeLabel(),
      addons: addonList().map((a) => a.name),
      total: total(),
      minutes: minutes(),
      date: state.date,
      time: state.time,
      name: form.elements.name.value.trim(),
      phone: form.elements.phone.value.trim(),
      email: email.value.trim(),
      vehicle: form.elements.vehicle.value.trim(),
      notes: form.elements.notes.value.trim(),
    };

    if (!C.bookingEndpoint) return textBooking(booking);

    const btn = $("[data-submit]");
    btn.disabled = true;
    btn.textContent = "Booking…";
    try {
      // text/plain keeps this a "simple" request, which Apps Script accepts cross-origin
      const res = await (await fetch(C.bookingEndpoint, { method: "POST", headers: { "Content-Type": "text/plain;charset=utf-8" }, body: JSON.stringify(booking) })).json();
      if (!res.ok) throw new Error(res.error || "Booking failed");
      msg.className = "form-msg ok";
      msg.textContent = `You're booked for ${fmtDate(booking.date)} at ${fmtTime(booking.time)}. See you then!`;
      ["name", "phone", "email", "vehicle", "notes"].forEach((n) => { form.elements[n].value = ""; });
      state.time = null;
      loadSlots();
    } catch (err) {
      fail(err.message === "slot_taken" ? "Someone just grabbed that time. Please pick another." : "Something went wrong. Please call or text us.");
      if (err.message === "slot_taken") loadSlots();
    } finally {
      btn.disabled = false;
      btn.textContent = "Request booking";
    }
  });

  function fail(text) {
    msg.className = "form-msg err";
    msg.textContent = text;
  }

  function textBooking(b) {
    const body = [
      `Hi Double Mint! I'd like to book:`,
      `${b.service} (${b.size})${b.addons.length ? " + " + b.addons.join(", ") : ""}, ${money(b.total)}`,
      `${fmtDate(b.date)} at ${fmtTime(b.time)}`,
      `${b.name}, ${b.phone}`,
      b.vehicle && `Vehicle: ${b.vehicle}`,
      b.notes && `Notes: ${b.notes}`,
    ].filter(Boolean).join("\n");
    window.location.href = `sms:${C.phones[0].tel}?&body=${encodeURIComponent(body)}`;
    msg.className = "form-msg ok";
    msg.textContent = `Opening your messages app. If nothing opens, text or call ${C.phones.map((p) => p.label).join(" or ")}.`;
  }

  /* ---------------- footer ---------------- */
  $("[data-phones]").innerHTML = C.phones.map((p) => `<a href="tel:${p.tel}">${p.label}</a>`).join("");
  $("[data-year]").textContent = new Date().getFullYear();

  renderCards();
  onChoiceChange();
})();
