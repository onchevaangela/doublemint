// Everything the owner may want to change lives here.
window.DM_CONFIG = {
  phones: [
    { label: "862 238 0550", tel: "+18622380550" },
    { label: "219 786 9863", tel: "+12197869863" },
  ],

  // Paste the Web App URL from booking/google-apps-script.gs (see booking/README.md).
  // Leave empty and the booking form falls back to a pre-filled text message.
  bookingEndpoint: "",

  sizes: [
    { id: "car", label: "Car" },
    { id: "suv", label: "SUV" },
    { id: "truck", label: "Truck" },
  ],

  // minutes = how long the appointment blocks the calendar
  services: [
    {
      id: "exterior",
      name: "Exterior Cleaning",
      prices: { car: 60, suv: 80, truck: 100 },
      minutes: 90,
      includes: ["Hand wash", "Wheels & tires cleaned", "Tire shine", "Windows cleaned"],
    },
    {
      id: "interior",
      name: "Interior Detail",
      prices: { car: 200, suv: 240, truck: 240 },
      minutes: 180,
      includes: ["Deep vacuum", "Seats & carpets shampooed", "Dashboard & panels cleaned", "Windows cleaned", "Door jambs cleaned"],
    },
    {
      id: "full",
      name: "Interior & Exterior",
      prices: { car: 230, suv: 260, truck: 280 },
      minutes: 240,
      featured: true,
      includes: ["Complete interior detail", "Hand wash & exterior detail", "Wheels & tires cleaned", "Windows cleaned"],
    },
  ],

  addons: [
    { id: "engine", name: "Engine Bay Cleaning", price: 50, minutes: 30 },
    { id: "pet", name: "Pet Hair Removal", price: 60, minutes: 45 },
  ],

  // Shown in the date picker; the Apps Script has its own copy that is the source of truth.
  daysAhead: 30,
  closedWeekdays: [0], // 0 = Sunday
};
