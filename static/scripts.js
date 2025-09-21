// ===== THEME TOGGLE WITH SYSTEM DEFAULT + PERSISTENCE =====

// Apply theme immediately on page load
(function () {
  let savedTheme = localStorage.getItem("theme");

  if (savedTheme === "theme-light" || savedTheme === "theme-dark") {
    // Use saved preference
    document.documentElement.classList.add(savedTheme);
  } else {
    // No saved preference: follow system/browser theme
    if (window.matchMedia("(prefers-color-scheme: light)").matches) {
      document.documentElement.classList.add("theme-light");
    } else {
      document.documentElement.classList.add("theme-dark");
    }
  }
})();

document.addEventListener("DOMContentLoaded", function () {
  const root = document.documentElement;
  const toggleBtn = document.getElementById("toggleTheme");

  if (toggleBtn) {
    toggleBtn.addEventListener("click", () => {
      if (root.classList.contains("theme-dark")) {
        root.classList.remove("theme-dark");
        root.classList.add("theme-light");
        localStorage.setItem("theme", "theme-light");
      } else {
        root.classList.remove("theme-light");
        root.classList.add("theme-dark");
        localStorage.setItem("theme", "theme-dark");
      }
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
  const box = document.getElementById("quoteBox");
  if (!box) return;

  const choice = quotes[Math.floor(Math.random() * quotes.length)];
  const quoteTextEl = document.getElementById("quoteText");
  const quoteAuthorEl = document.getElementById("quoteAuthor");

  if (quoteTextEl && quoteAuthorEl) {
    quoteTextEl.innerText = `"${choice.text}"`;
    quoteTextEl.style.fontStyle = "italic";
    quoteAuthorEl.innerText = choice.author;
  }
}

showRandomQuote();
setInterval(showRandomQuote, 10000);

// ===== CLIMATE CLOCK =====
function updateClock() {
  const targetDate = new Date("2026-01-01T00:00:00");
  const now = new Date();
  const diff = targetDate - now;

  if (diff <= 0) return;

  const days = Math.floor(diff / (1000 * 60 * 60 * 24));
  const hours = Math.floor((diff / (1000 * 60 * 60)) % 24);
  const minutes = Math.floor((diff / (1000 * 60)) % 60);
  const seconds = Math.floor((diff / 1000) % 60);

  const d = document.getElementById("clockDays");
  const h = document.getElementById("clockHours");
  const m = document.getElementById("clockMinutes");
  const s = document.getElementById("clockSeconds");

  if (d && h && m && s) {
    d.textContent = days.toString().padStart(2, "0");
    h.textContent = hours.toString().padStart(2, "0");
    m.textContent = minutes.toString().padStart(2, "0");
    s.textContent = seconds.toString().padStart(2, "0");
  }
}

setInterval(updateClock, 1000);
updateClock();

// ===== FOOTER YEAR =====
const yearEl = document.getElementById("year");
if (yearEl) yearEl.textContent = new Date().getFullYear();

// ===== SEARCH BAR HANDLER =====
document.addEventListener("DOMContentLoaded", function () {
  const searchInput = document.getElementById("siteSearch");
  const searchBtn = document.getElementById("searchBtn");

  if (searchInput && searchBtn) {
    function doSearch() {
      const query = searchInput.value.trim();
      if (query) {
        window.location.href = `/search?q=${encodeURIComponent(query)}`;
      } else {
        window.location.href = `/search`;
      }
    }

    searchBtn.addEventListener("click", doSearch);
    searchInput.addEventListener("keydown", function (e) {
      if (e.key === "Enter") {
        e.preventDefault();
        doSearch();
      }
    });
  }
});

// ===== IMAGE + BACKGROUND FADE-IN =====
document.addEventListener("DOMContentLoaded", function () {
  // Fade-in for all <img>
  document.querySelectorAll("img").forEach(function (img) {
    if (img.complete) {
      img.classList.add("loaded");
    } else {
      img.addEventListener("load", function () {
        img.classList.add("loaded");
      });
    }
  });

  // Fade-in for background images
  document.querySelectorAll(".bg-fade").forEach(function (el) {
    const bg = window.getComputedStyle(el).backgroundImage;
    if (bg && bg !== "none") {
      const url = bg.slice(5, -2); // strip url("...")
      const img = new Image();
      img.src = url;
      img.onload = function () {
        el.classList.add("bg-loaded");
      };
    }
  });
});
