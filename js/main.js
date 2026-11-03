/* PlainCover shared site script. No dependencies. */
(function () {
  "use strict";

  document.documentElement.classList.remove("no-js");

  /* Mobile navigation toggle */
  var toggle = document.querySelector(".nav-toggle");
  var nav = document.getElementById("site-nav");

  if (toggle && nav) {
    toggle.addEventListener("click", function () {
      var open = toggle.getAttribute("aria-expanded") === "true";
      toggle.setAttribute("aria-expanded", String(!open));
      nav.classList.toggle("is-open", !open);
    });

    document.addEventListener("keydown", function (event) {
      if (event.key === "Escape" && toggle.getAttribute("aria-expanded") === "true") {
        toggle.setAttribute("aria-expanded", "false");
        nav.classList.remove("is-open");
        toggle.focus();
      }
    });
  }

  /* Current year in footer */
  var yearEls = document.querySelectorAll("[data-year]");
  for (var i = 0; i < yearEls.length; i++) {
    yearEls[i].textContent = String(new Date().getFullYear());
  }

  /* Shared form validation helper (used by contact form and calculator) */
  function setFieldError(field, message) {
    var errorEl = document.getElementById(field.id + "-error");
    if (message) {
      field.setAttribute("aria-invalid", "true");
      if (errorEl) {
        errorEl.textContent = message;
        errorEl.hidden = false;
      }
    } else {
      field.removeAttribute("aria-invalid");
      if (errorEl) errorEl.hidden = true;
    }
  }
  window.SiteForms = { setFieldError: setFieldError };

  /* Contact form.
   * Sends to the form service URL in the form's data-endpoint attribute (for example Formspree).
   * If no endpoint is set, the form stays hidden and only the email option is shown. */
  var contactForm = document.getElementById("contact-form");
  var confirmation = document.getElementById("contact-confirmation");
  var fallback = document.getElementById("contact-fallback");
  var formError = document.getElementById("form-error");

  if (contactForm && confirmation) {
    var endpoint = (contactForm.getAttribute("data-endpoint") || "").trim();

    if (/^https:\/\//.test(endpoint)) {
      contactForm.hidden = false;
      contactForm.setAttribute("action", endpoint);
      if (fallback) fallback.hidden = true;
    }

    contactForm.addEventListener("submit", function (event) {
      event.preventDefault();

      var name = contactForm.elements.name;
      var email = contactForm.elements.email;
      var message = contactForm.elements.message;
      var privacy = contactForm.elements.privacy_consent;
      var firstInvalid = null;

      var checks = [
        [name, name.value.trim() ? "" : "Please enter your name."],
        [email, /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email.value.trim()) ? "" : "Please enter a valid email address."],
        [message, message.value.trim() ? "" : "Please enter a message."],
        [privacy, privacy.checked ? "" : "Please confirm that you agree to the Privacy Policy."]
      ];

      checks.forEach(function (check) {
        setFieldError(check[0], check[1]);
        if (check[1] && !firstInvalid) firstInvalid = check[0];
      });

      if (firstInvalid) {
        firstInvalid.focus();
        return;
      }

      var button = contactForm.querySelector('button[type="submit"]');
      button.disabled = true;
      if (formError) formError.hidden = true;

      fetch(endpoint, {
        method: "POST",
        body: new FormData(contactForm),
        headers: { Accept: "application/json" }
      })
        .then(function (response) {
          if (!response.ok) throw new Error("Request failed");
          contactForm.reset();
          contactForm.hidden = true;
          confirmation.hidden = false;
          confirmation.focus();
        })
        .catch(function () {
          if (formError) {
            formError.hidden = false;
            formError.focus && formError.focus();
          }
        })
        .then(function () {
          button.disabled = false;
        });
    });
  }
})();
