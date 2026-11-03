/* PlainCover third-party integrations: Google AdSense and (optional) Google Analytics 4.
 *
 * Nothing loads until real IDs are configured, so the site works and stays fast before launch.
 *
 * ADSENSE SETUP
 * 1. Replace "ca-pub-XXXXXXXXXXXXXXXX" in the <meta name="google-adsense-account"> tag of every
 *    HTML page (one find-and-replace across the project) and in ads.txt (without "ca-").
 * 2. That alone loads the AdSense script, which enables Auto ads once you turn them on in AdSense.
 * 3. Optional: to also fill the manual ad positions placed inside articles, create "Display" ad
 *    units in AdSense and paste their numeric slot IDs into AD_SLOTS below. Empty = position stays hidden.
 * 4. In AdSense > Privacy & messaging, enable the consent message for EEA/UK/Switzerland and
 *    the US state regulations message. Those are served by the AdSense script itself.
 *
 * ANALYTICS SETUP (optional)
 * Paste your GA4 measurement ID (G-XXXXXXXXXX) into GA_MEASUREMENT_ID and describe it in the privacy policy.
 */

const AD_SLOTS = {
  inArticle: "",   // first in-article position in guides
  inArticle2: "",  // position before "The bottom line" in guides
  inContent: ""    // position on car, home and calculator pages
};

const GA_MEASUREMENT_ID = "";

(function () {
  "use strict";

  function loadScript(src, attrs) {
    var s = document.createElement("script");
    s.async = true;
    s.src = src;
    Object.keys(attrs || {}).forEach(function (k) {
      s.setAttribute(k, attrs[k]);
    });
    document.head.appendChild(s);
  }

  /* ---------- AdSense ---------- */
  var meta = document.querySelector('meta[name="google-adsense-account"]');
  var client = meta ? meta.getAttribute("content") : "";

  if (/^ca-pub-\d{16}$/.test(client)) {
    loadScript(
      "https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=" + client,
      { crossorigin: "anonymous" }
    );

    window.adsbygoogle = window.adsbygoogle || [];
    var slots = document.querySelectorAll(".ad-slot[data-ad-key]");

    Array.prototype.forEach.call(slots, function (container) {
      var slotId = AD_SLOTS[container.getAttribute("data-ad-key")];
      if (!slotId) return;

      var ins = document.createElement("ins");
      ins.className = "adsbygoogle";
      ins.style.display = "block";
      ins.setAttribute("data-ad-client", client);
      ins.setAttribute("data-ad-slot", slotId);
      ins.setAttribute("data-ad-format", "auto");
      ins.setAttribute("data-full-width-responsive", "true");

      container.appendChild(ins);
      container.hidden = false;
      try {
        window.adsbygoogle.push({});
      } catch (e) {
        container.hidden = true;
      }
    });
  }

  /* ---------- "Privacy settings" buttons ----------
   * Reopens Google's consent message (AdSense Privacy & messaging) so visitors can change their choice.
   * Before AdSense is active, the button opens the cookie policy instead. */
  var adsActive = /^ca-pub-\d{16}$/.test(client);
  if (adsActive) {
    window.googlefc = window.googlefc || {};
    window.googlefc.callbackQueue = window.googlefc.callbackQueue || [];
  }
  document.addEventListener("click", function (event) {
    var trigger = event.target.closest && event.target.closest("[data-privacy-settings]");
    if (!trigger) return;
    event.preventDefault();
    if (adsActive) {
      window.googlefc.callbackQueue.push(function () {
        window.googlefc.showRevocationMessage();
      });
    } else {
      var base = document.querySelector('link[rel="stylesheet"]').getAttribute("href").replace("css/styles.css", "");
      window.location.href = base + "cookie-policy.html#manage";
    }
  });

  /* ---------- Google Analytics 4 (optional) ---------- */
  if (/^G-[A-Z0-9]+$/.test(GA_MEASUREMENT_ID)) {
    loadScript("https://www.googletagmanager.com/gtag/js?id=" + GA_MEASUREMENT_ID);
    window.dataLayer = window.dataLayer || [];
    window.gtag = function () {
      window.dataLayer.push(arguments);
    };
    window.gtag("js", new Date());
    window.gtag("config", GA_MEASUREMENT_ID);
  }
})();
