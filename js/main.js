/* UnpackInsurance shared site script. No dependencies. */
(function () {
  "use strict";

  document.documentElement.classList.remove("no-js");

  /* When shown inside a preview frame, start each page at the top. */
  if (window.self !== window.top && !window.location.hash) {
    window.addEventListener("load", function () {
      window.scrollTo(0, 0);
      try {
        document.body.scrollIntoView({ block: "start" });
      } catch (e) {}
    });
  }

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



  /* Header shadow once the page is scrolled */
  var header = document.querySelector(".site-header");
  if (header) {
    var onScroll = function () {
      header.classList.toggle("is-scrolled", window.scrollY > 8);
    };
    window.addEventListener("scroll", onScroll, { passive: true });
    onScroll();
  }

  /* Gentle fade-in of sections as they scroll into view */
  var reduceMotion = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  if (!reduceMotion && "IntersectionObserver" in window) {
    var targets = document.querySelectorAll(
      ".tile, .trust-item, .steps li, .card, .section-title, .section-sub, .takeaways, .toc, .guide-art, .related h2, .glossary dt, .form, .result"
    );
    if (targets.length) {
      document.documentElement.classList.add("js-anim");
      var observer = new IntersectionObserver(function (entries) {
        entries.forEach(function (entry) {
          if (entry.isIntersecting) {
            var el = entry.target;
            el.classList.add("is-visible");
            observer.unobserve(el);
            /* Once shown, drop the animation classes so hover effects work normally */
            window.setTimeout(function () {
              el.classList.remove("reveal", "is-visible");
              el.style.removeProperty("--reveal-delay");
            }, 1300);
          }
        });
      }, { rootMargin: "0px 0px -8% 0px", threshold: 0.08 });
      Array.prototype.forEach.call(targets, function (el) {
        var siblings = el.parentElement ? Array.prototype.indexOf.call(el.parentElement.children, el) : 0;
        el.style.setProperty("--reveal-delay", Math.min(siblings, 5) * 0.07 + "s");
        el.classList.add("reveal");
        observer.observe(el);
      });
      /* Never hide content when printing */
      window.addEventListener("beforeprint", function () {
        document.documentElement.classList.remove("js-anim");
      });
    }
  }

  /* Guide search on the guides page: filters the cards as you type. */
  var searchInput = document.getElementById("guide-search-input");
  if (searchInput) {
    var cards = Array.prototype.slice.call(document.querySelectorAll(".page-collection .card"));
    var headings = Array.prototype.slice.call(document.querySelectorAll(".page-collection h2.section-title"));
    var status = document.getElementById("guide-search-status");
    searchInput.addEventListener("input", function () {
      var q = searchInput.value.trim().toLowerCase();
      var shown = 0;
      cards.forEach(function (card) {
        var match = !q || card.textContent.toLowerCase().indexOf(q) !== -1;
        card.hidden = !match;
        if (match) shown++;
      });
      headings.forEach(function (h) {
        var grid = h.nextElementSibling;
        var any = grid && grid.querySelector(".card:not([hidden])");
        h.hidden = !any;
        if (grid) grid.hidden = !any;
      });
      status.textContent = q ? (shown ? shown + (shown === 1 ? " guide found" : " guides found") : "No guides match. Try another word.") : "";
    });
  }

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
