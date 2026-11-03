/* CoverCompass rough estimate calculator.
 *
 * IMPORTANT: Every number below is an ILLUSTRATIVE SAMPLE value for demonstration.
 * None of it is real insurer pricing or actuarial data. Results are labeled
 * "Rough estimate only, not a quote". Review and adjust before launch.
 */

/* ---------- Illustrative constants (edit here) ---------- */

// Sample annual base rates in US dollars, before any multipliers.
const BASE_RATES = {
  car: 1500,
  home: 1400
};

// Width of the displayed range around the point estimate (0.25 = plus/minus 25%).
const RANGE_SPREAD = 0.25;

// Sample state multipliers: [car, home]. 1.00 = sample national baseline.
const STATE_FACTORS = {
  AL: ["Alabama",        [0.95, 1.20]],
  AK: ["Alaska",         [0.90, 0.75]],
  AZ: ["Arizona",        [1.00, 0.95]],
  AR: ["Arkansas",       [0.95, 1.25]],
  CA: ["California",     [1.15, 0.90]],
  CO: ["Colorado",       [1.10, 1.30]],
  CT: ["Connecticut",    [1.05, 0.95]],
  DE: ["Delaware",       [1.10, 0.70]],
  FL: ["Florida",        [1.35, 1.80]],
  GA: ["Georgia",        [1.10, 1.05]],
  HI: ["Hawaii",         [0.80, 0.50]],
  ID: ["Idaho",          [0.75, 0.75]],
  IL: ["Illinois",       [0.95, 1.00]],
  IN: ["Indiana",        [0.80, 0.95]],
  IA: ["Iowa",           [0.75, 1.10]],
  KS: ["Kansas",         [0.95, 1.50]],
  KY: ["Kentucky",       [1.10, 1.15]],
  LA: ["Louisiana",      [1.40, 1.70]],
  ME: ["Maine",          [0.70, 0.75]],
  MD: ["Maryland",       [1.15, 0.90]],
  MA: ["Massachusetts",  [0.95, 1.00]],
  MI: ["Michigan",       [1.30, 0.95]],
  MN: ["Minnesota",      [0.95, 1.20]],
  MS: ["Mississippi",    [1.00, 1.30]],
  MO: ["Missouri",       [1.00, 1.30]],
  MT: ["Montana",        [0.95, 1.10]],
  NE: ["Nebraska",       [0.90, 1.60]],
  NV: ["Nevada",         [1.25, 0.70]],
  NH: ["New Hampshire",  [0.75, 0.75]],
  NJ: ["New Jersey",     [1.15, 0.80]],
  NM: ["New Mexico",     [0.95, 1.00]],
  NY: ["New York",       [1.30, 1.00]],
  NC: ["North Carolina", [0.80, 1.05]],
  ND: ["North Dakota",   [0.80, 1.15]],
  OH: ["Ohio",           [0.80, 0.85]],
  OK: ["Oklahoma",       [1.00, 1.70]],
  OR: ["Oregon",         [0.95, 0.70]],
  PA: ["Pennsylvania",   [1.00, 0.80]],
  RI: ["Rhode Island",   [1.10, 1.00]],
  SC: ["South Carolina", [1.05, 1.10]],
  SD: ["South Dakota",   [0.85, 1.20]],
  TN: ["Tennessee",      [0.90, 1.10]],
  TX: ["Texas",          [1.15, 1.60]],
  UT: ["Utah",           [0.95, 0.70]],
  VT: ["Vermont",        [0.70, 0.75]],
  VA: ["Virginia",       [0.85, 0.85]],
  WA: ["Washington",     [1.00, 0.80]],
  WV: ["West Virginia",  [0.95, 0.90]],
  WI: ["Wisconsin",      [0.80, 0.85]],
  WY: ["Wyoming",        [0.85, 1.00]]
};

// Sample age-range multipliers: [car, home].
const AGE_FACTORS = {
  "18-24": [1.80, 1.15],
  "25-34": [1.15, 1.05],
  "35-49": [1.00, 1.00],
  "50-64": [0.92, 0.95],
  "65+":   [1.00, 0.95]
};

// Sample car mileage multipliers.
const MILEAGE_FACTORS = {
  "low": 0.90,
  "medium": 1.00,
  "high": 1.10,
  "very-high": 1.20
};

// Sample home rebuild-value multipliers.
const HOME_VALUE_FACTORS = {
  "under-200k": 0.65,
  "200-400k": 1.00,
  "400-700k": 1.55,
  "700k-1m": 2.20,
  "over-1m": 3.00
};

// Sample coverage-level multipliers: [car, home].
const COVERAGE_FACTORS = {
  basic: [0.55, 0.85],
  standard: [1.00, 1.00],
  premium: [1.30, 1.25]
};

/* ---------- Calculator logic ---------- */
(function () {
  "use strict";

  const form = document.getElementById("estimate-form");
  if (!form) return;

  const result = document.getElementById("estimate-result");
  const stateSelect = form.elements.state;
  const carField = form.querySelector('[data-for="car"]');
  const homeField = form.querySelector('[data-for="home"]');
  const setFieldError = (window.SiteForms && window.SiteForms.setFieldError) || function () {};

  // Populate all 50 states, sorted by name.
  Object.keys(STATE_FACTORS)
    .sort((a, b) => STATE_FACTORS[a][0].localeCompare(STATE_FACTORS[b][0]))
    .forEach((code) => {
      const option = document.createElement("option");
      option.value = code;
      option.textContent = STATE_FACTORS[code][0];
      stateSelect.appendChild(option);
    });

  function currentType() {
    return form.elements.type.value === "home" ? "home" : "car";
  }

  function updateTypeFields() {
    const isHome = currentType() === "home";
    carField.hidden = isHome;
    homeField.hidden = !isHome;
    form.elements.mileage.required = !isHome;
    form.elements.homeValue.required = isHome;
    result.hidden = true;
  }

  Array.prototype.forEach.call(form.elements.type, (radio) => {
    radio.addEventListener("change", updateTypeFields);
  });
  updateTypeFields();

  const currency = new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
    maximumFractionDigits: 0
  });

  function roundTo(value, step) {
    return Math.round(value / step) * step;
  }

  form.addEventListener("submit", (event) => {
    event.preventDefault();

    const type = currentType();
    const idx = type === "car" ? 0 : 1;
    const required = [
      [form.elements.state, "Please select a state."],
      [form.elements.age, "Please select an age range."],
      type === "car"
        ? [form.elements.mileage, "Please select your annual mileage."]
        : [form.elements.homeValue, "Please select a home value bracket."],
      [form.elements.coverage, "Please select a coverage level."]
    ];

    // Clear errors on the hidden field.
    setFieldError(type === "car" ? form.elements.homeValue : form.elements.mileage, "");

    let firstInvalid = null;
    required.forEach(([field, message]) => {
      const error = field.value ? "" : message;
      setFieldError(field, error);
      if (error && !firstInvalid) firstInvalid = field;
    });

    if (firstInvalid) {
      result.hidden = true;
      firstInvalid.focus();
      return;
    }

    let estimate = BASE_RATES[type];
    estimate *= STATE_FACTORS[form.elements.state.value][1][idx];
    estimate *= AGE_FACTORS[form.elements.age.value][idx];
    estimate *= type === "car"
      ? MILEAGE_FACTORS[form.elements.mileage.value]
      : HOME_VALUE_FACTORS[form.elements.homeValue.value];
    estimate *= COVERAGE_FACTORS[form.elements.coverage.value][idx];

    const low = roundTo(estimate * (1 - RANGE_SPREAD), 50);
    const high = roundTo(estimate * (1 + RANGE_SPREAD), 50);

    document.getElementById("result-low").textContent = currency.format(low);
    document.getElementById("result-high").textContent = currency.format(high);
    document.getElementById("result-monthly").textContent =
      "That is roughly " + currency.format(low / 12) + " to " + currency.format(high / 12) +
      " per month. Monthly payment plans may include extra fees.";

    result.hidden = false;
    result.focus();
  });
})();
