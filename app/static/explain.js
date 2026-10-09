/* Plain-English layer for StockLean.
   Loaded after the main script. It makes the page easier for beginners:
   friendly labels, tap-to-explain tips, a plain verdict, and a "Basics" section.
   index.html calls window.explainResult(data) after every prediction. */
(function () {
  "use strict";

  const NAMES = {
    AAPL: "Apple", MSFT: "Microsoft", NVDA: "Nvidia",
    TSLA: "Tesla", AMZN: "Amazon", GOOGL: "Google",
  };

  // [original label, friendly label, explanation]
  const LABELS = [
    ["Last close", "Last price",
      "The price of one share when the stock market closed on its most recent day."],
    ["Predicted move", "Guess for tomorrow",
      "How much the model thinks the price will change, in percent. Small numbers like +0.1% are normal for one day."],
    ["Typical day", "Usual daily change",
      "The average daily change in this stock's past. The lean compares the model's guess with this."],
  ];

  const BASICS = [
    ["What is a stock?",
      "A tiny piece of ownership in a company. If you own one share of Apple, you own a small slice of Apple."],
    ["What is a ticker?",
      "A short code for a company on the stock market. Apple is AAPL and Tesla is TSLA."],
    ["Why do prices move?",
      "Prices rise when more people want to buy than sell, and fall when more want to sell. News, profits and mood all play a part."],
    ["Can anyone predict it?",
      "Not reliably. That is why this site shows how often the model is right, not just its guess."],
  ];

  const CSS = `
    .tip{position:relative;display:inline-grid;place-items:center;width:18px;height:18px;margin-left:6px;padding:0;
      border-radius:50%;border:1px solid var(--line);background:transparent;color:var(--glow);
      font:700 11px var(--font);cursor:help;vertical-align:middle}
    .tip::before{content:"i"}
    .tip span{position:absolute;left:50%;bottom:calc(100% + 8px);transform:translateX(-50%);width:230px;
      padding:10px 12px;border-radius:10px;background:#1a1530;border:1px solid var(--line);color:var(--text);
      font-weight:400;font-size:.8rem;line-height:1.45;text-align:left;opacity:0;pointer-events:none;
      transition:opacity .15s;z-index:5}
    .tip:hover span,.tip:focus span{opacity:1}
    #plain{margin-top:12px;padding:14px 16px;border-left:3px solid var(--glow);
      background:rgba(139,92,246,.08);border-radius:4px;color:var(--text);max-width:64ch}
    #why ul{list-style:none;margin:14px 0 0;padding:0;display:grid;gap:10px}
    #why li{display:flex;gap:12px;align-items:flex-start;padding:12px 14px;border:1px solid var(--line);
      border-radius:12px;background:rgba(0,0,0,.25)}
    #why .tag{flex:none;font-weight:800;font-size:.8rem;padding:2px 10px;border-radius:999px;white-space:nowrap}
    #why .tag.up{color:var(--up);background:rgba(52,211,153,.12)}
    #why .tag.down{color:var(--down);background:rgba(251,113,133,.12)}`;

  function addStyles() {
    const style = document.createElement("style");
    style.textContent = CSS;
    document.head.appendChild(style);
  }

  function friendlyLabels() {
    document.querySelectorAll(".facts dt").forEach((dt) => {
      const row = LABELS.find((l) => l[0] === dt.textContent.trim());
      if (!row) return;
      dt.textContent = row[1];
      const tip = document.createElement("button");
      tip.type = "button";
      tip.className = "tip";
      tip.setAttribute("aria-label", "What does this mean? " + row[2]);
      const text = document.createElement("span");
      text.setAttribute("role", "tooltip");
      text.textContent = row[2];
      tip.appendChild(text);
      dt.appendChild(tip);
    });
  }

  function companyChips() {
    const form = document.getElementById("form");
    const input = document.getElementById("ticker");
    document.querySelectorAll(".chip").forEach((old) => {
      const ticker = old.textContent.trim();
      const chip = old.cloneNode(false); // drops the old click handler
      chip.textContent = NAMES[ticker] || ticker;
      chip.title = ticker;
      chip.addEventListener("click", () => {
        input.value = ticker;
        form.requestSubmit();
      });
      old.replaceWith(chip);
    });
  }

  function addBasics() {
    const section = document.createElement("section");
    section.className = "block center";
    section.id = "basics";
    section.innerHTML =
      '<span class="pill"><i></i>Basics</span>' +
      '<h2 class="title">Stocks in 60 seconds</h2>' +
      '<p class="lead">New to this? Here is all you need to read the results.</p>' +
      '<div class="cards">' +
      BASICS.map((b) => "<div class=\"card\"><h3>" + b[0] + "</h3><p>" + b[1] + "</p></div>").join("") +
      "</div>";
    document.getElementById("features").before(section);

    const links = document.querySelector(".links");
    const a = document.createElement("a");
    a.href = "#basics";
    a.textContent = "Basics";
    links.insertBefore(a, links.children[1]);
  }

  function plainIntro() {
    document.querySelector(".sub").textContent =
      "Type a company's ticker (its short code, like AAPL for Apple). A small computer model learns from " +
      "that stock's past prices, guesses which way it may move tomorrow, and shows how often models like this are right.";
    const meta = document.getElementById("meta");
    const plain = document.createElement("p");
    plain.id = "plain";
    meta.insertAdjacentElement("afterend", plain);
  }

  function renderWhy(reasons) {
    let panel = document.getElementById("why");
    if (!panel) {
      panel = document.createElement("div");
      panel.id = "why";
      panel.className = "panel";
      panel.style.marginTop = "16px";
      document.querySelector("#result .trust").before(panel);
    }
    panel.hidden = !reasons || !reasons.length;
    if (panel.hidden) return;
    panel.innerHTML =
      '<h3 style="font-size:1.25rem;margin:0 0 6px">Why does the model think this?</h3>' +
      '<p style="color:var(--muted);margin:0;max-width:64ch">These three things pushed the guess the most, ' +
      "compared with a typical day. They describe how the model works, not what will happen.</p><ul>" +
      reasons.map((r) =>
        '<li><span class="tag ' + r.effect + '">' + (r.effect === "up" ? "Pushes up" : "Pushes down") +
        "</span><span>" + r.text + "</span></li>").join("") +
      "</ul>";
  }

  window.explainResult = function (data) {
    renderWhy(data.reasons);
    const name = NAMES[data.ticker] || data.ticker;
    const up = data.lean === "up";

    document.getElementById("meta").textContent =
      name + " (" + data.ticker + "), for the next trading day after " + data.as_of;

    document.getElementById("plain").textContent =
      "In plain words: the model guesses tomorrow will be a " + (up ? "better" : "worse") +
      " day than usual for " + name + "'s stock. It is only a guess, not advice.";

    const right = Math.round(data.model_accuracy * 100);
    const always = Math.round(data.always_up_accuracy * 100);
    const edge = data.model_accuracy - 0.5;
    const verdict = edge < 0.02 ? "That is barely better than luck."
      : edge < 0.05 ? "That is only slightly better than luck."
      : "That is better than luck, but still wrong a lot of the time.";
    document.getElementById("trustText").textContent =
      "Imagine guessing the next day 100 times. A coin flip would be right about 50 times. " +
      "This model was right about " + right + " times. " + verdict +
      " Simply guessing 'up' every day would have been right about " + always + " times. " +
      "Please don't rely on this for money decisions.";
  };

  addStyles();
  plainIntro();
  friendlyLabels();
  companyChips();
  addBasics();
})();