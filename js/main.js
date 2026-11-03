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

  /* Contact form: front-end confirmation only, nothing is sent. */
  var contactForm = document.getElementById("contact-form");
  var confirmation = document.getElementById("contact-confirmation");

  if (contactForm && confirmation) {
    contactForm.addEventListener("submit", function (event) {
      event.preventDefault();

      var name = contactForm.elements.name;
      var email = contactForm.elements.email;
      var message = contactForm.elements.message;
      var firstInvalid = null;

      var checks = [
        [name, name.value.trim() ? "" : "Please enter your name."],
        [email, /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email.value.trim()) ? "" : "Please enter a valid email address."],
        [message, message.value.trim() ? "" : "Please enter a message."]
      ];

      checks.forEach(function (check) {
        setFieldError(check[0], check[1]);
        if (check[1] && !firstInvalid) firstInvalid = check[0];
      });

      if (firstInvalid) {
        firstInvalid.focus();
        return;
      }

      // [PLACEHOLDER] Connect to a form service or backend before launch.
      contactForm.reset();
      contactForm.hidden = true;
      confirmation.hidden = false;
      confirmation.focus();
    });
  }
})();
