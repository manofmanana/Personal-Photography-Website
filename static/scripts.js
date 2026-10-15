// The initial theme is applied by an inline script in base.html's <head>,
// so the page never flashes the wrong colors before this file loads.

// ===== THEME TOGGLE =====
document.addEventListener("DOMContentLoaded", function () {
  const root = document.documentElement;
  const toggleBtn = document.getElementById("toggleTheme");

  if (toggleBtn) {
    toggleBtn.addEventListener("click", () => {
      const next = root.classList.contains("theme-dark") ? "theme-light" : "theme-dark";
      root.classList.remove("theme-dark", "theme-light");
      root.classList.add(next);
      try { localStorage.setItem("theme", next); } catch (e) {}
    });
  }
});

// ===== FOOD FOR THOUGHT QUOTES =====
const quotes = [
  { text: "Hope is the thing with feathers that perches in the soul.", author: "Emily Dickinson" },
  { text: "Freedom lies in being bold.", author: "Robert Frost" },
  { text: "Mother Nature never breaks her own laws.", author: "Leonardo da Vinci" },
  { text: "Photography is the story I fail to put into words.", author: "Destin Sparks" },
  { text: "The mountains are calling and I must go.", author: "John Muir" },
  { text: "What we see depends mainly on what we look for.", author: "John Lubbock" },
  { text: "Art is freedom. Being able to bend things most see as a straight line.", author: "Unknown" }
];

function showRandomQuote() {
  const quoteTextEl = document.getElementById("quoteText");
  const quoteAuthorEl = document.getElementById("quoteAuthor");
  if (!quoteTextEl || !quoteAuthorEl) return;

  const choice = quotes[Math.floor(Math.random() * quotes.length)];
  quoteTextEl.innerText = `"${choice.text}"`;
  quoteTextEl.style.fontStyle = "italic";
  quoteAuthorEl.innerText = choice.author;
}

if (document.getElementById("quoteBox")) {
  showRandomQuote();
  setInterval(showRandomQuote, 10000);
}

// ===== FOOTER YEAR =====
const yearEl = document.getElementById("year");
if (yearEl) yearEl.textContent = new Date().getFullYear();

// ===== IMAGE FADE-IN =====
document.addEventListener("DOMContentLoaded", function () {
  document.querySelectorAll("img").forEach(function (img) {
    if (img.complete) {
      img.classList.add("loaded");
    } else {
      // show on error too, so a failed image still displays its alt text
      const show = function () { img.classList.add("loaded"); };
      img.addEventListener("load", show);
      img.addEventListener("error", show);
    }
  });
});
