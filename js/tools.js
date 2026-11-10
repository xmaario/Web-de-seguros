/* UnpackInsurance free tools: gap insurance quiz and liability limits calculator.
 * Everything runs in the browser. Nothing is sent or stored. Results are general information. */
(function () {
  "use strict";

  function num(el) {
    var n = parseFloat(String(el && el.value || "").replace(/[^0-9.]/g, ""));
    return isFinite(n) && n > 0 ? n : 0;
  }
  function money(n) {
    return "$" + Math.round(n).toLocaleString("en-US");
  }
  function radio(form, name) {
    var el = form.querySelector('input[name="' + name + '"]:checked');
    return el ? el.value : "";
  }
  function show(section) {
    section.hidden = false;
    section.focus();
    if (section.scrollIntoView) section.scrollIntoView({ behavior: "smooth", block: "start" });
  }

  /* ---------- Gap insurance quiz ---------- */
  var gap = document.getElementById("gap-quiz");
  if (gap) {
    var loanBlock = gap.querySelector("[data-gap-loan]");
    var syncPay = function () {
      loanBlock.hidden = radio(gap, "pay") === "cash";
    };
    gap.addEventListener("change", syncPay);
    syncPay();

    gap.addEventListener("submit", function (event) {
      event.preventDefault();
      var pay = radio(gap, "pay");
      var verdict, explain;
      var amountEl = document.getElementById("gap-amount");
      amountEl.hidden = true;

      if (pay === "cash") {
        verdict = "You likely don't need it";
        explain = "Gap insurance pays off a loan or lease balance. If you paid in full, there is no balance to cover. Collision and comprehensive coverage still pay up to the car's actual cash value.";
      } else {
        var score = ["down", "term", "roll", "new", "miles"].reduce(function (s, k) {
          return s + parseInt(radio(gap, k) || "0", 10);
        }, 0);
        var owe = num(document.getElementById("gap-owe"));
        var value = num(document.getElementById("gap-value"));
        var diff = owe && value ? owe - value : null;

        if (diff !== null) {
          amountEl.hidden = false;
          amountEl.textContent = diff > 0
            ? "Based on your numbers, you owe about " + money(diff) + " more than the car is worth today. That is the amount gap coverage would be designed to pay if the car were totaled now, minus any terms and limits in the policy."
            : "Based on your numbers, the car is worth about " + money(-diff) + " more than you owe, so you have no gap today.";
        }

        if (diff !== null && diff <= 0) {
          verdict = "Probably not needed right now";
          explain = "You currently owe less than the car is worth. If you already pay for gap coverage, ask whether you can cancel it and get a refund of any unused portion.";
        } else if (score >= 3 || (diff !== null && diff > 0)) {
          verdict = "Gap coverage is worth considering";
          explain = "Your answers include several situations that often lead to owing more than the car is worth, especially in the first years of a loan. Compare gap coverage from your insurer, lender and dealer before you decide.";
        } else if (score >= 1) {
          verdict = "Worth checking your numbers";
          explain = "You have some risk factors. Ask your lender for a payoff amount and compare it with your car's current value. If you owe more, gap coverage may be worth it.";
        } else {
          verdict = "You may not need it";
          explain = "Your answers suggest you likely owe less than the car is worth. Check again if your situation changes.";
        }
        if (pay === "lease") {
          explain += " Many leases already include a gap waiver, so read your lease contract before buying separate coverage.";
        }
      }
      document.getElementById("gap-verdict").textContent = verdict;
      document.getElementById("gap-explain").textContent = explain;
      show(document.getElementById("gap-result"));
    });
  }

  /* ---------- Liability limits calculator ---------- */
  var li = document.getElementById("liability-form");
  if (li) {
    var LEVELS = [
      { cover: 100000, label: "100/300/100", text: "$100,000 per person, $300,000 per accident for injuries, and $100,000 for property damage" },
      { cover: 250000, label: "250/500/100", text: "$250,000 per person, $500,000 per accident for injuries, and $100,000 for property damage" }
    ];
    li.addEventListener("submit", function (event) {
      event.preventDefault();
      var assets = num(document.getElementById("li-equity")) + num(document.getElementById("li-savings")) + num(document.getElementById("li-other"));
      var income = parseInt(document.getElementById("li-income").value, 10) || 0;
      var extra = parseInt(radio(li, "teen"), 10) + parseInt(radio(li, "drive"), 10) + (income === 2 ? 1 : 0);

      var idx = assets <= LEVELS[0].cover ? 0 : 1;
      var reasons = [];
      if (extra > 0) {
        idx += 1;
        reasons.push("one level higher because of " + (extra > 1 ? "several" : "an") + " added exposure factor" + (extra > 1 ? "s" : "") + " you selected");
      }
      var umbrella = 0;
      if (assets > LEVELS[1].cover || idx > 1) {
        umbrella = Math.max(1, Math.ceil(Math.max(assets - LEVELS[1].cover, 0) / 1000000));
      }
      var level = LEVELS[Math.min(idx, 1)];

      document.getElementById("li-limits").textContent = level.label + (umbrella ? " + umbrella" : "");
      document.getElementById("li-assets").textContent = "Assets you entered: " + money(assets) + ". Suggested car liability: " + level.text + ".";
      document.getElementById("li-explain").textContent = "This compares your assets with common limit levels" + (reasons.length ? ", " + reasons.join(", ") : "") + ". Limits above your state's minimum help protect your savings and future income if you cause a serious accident.";
      var um = document.getElementById("li-umbrella");
      um.hidden = !umbrella;
      um.textContent = umbrella
        ? "Consider an umbrella policy of about $" + umbrella + " million. Umbrella insurers usually require underlying limits such as 250/500/100 on your car policy and similar liability on your home policy."
        : "";
      show(document.getElementById("liability-result"));
    });
  }
})();
