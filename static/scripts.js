// The initial theme is applied by an inline script in base.html's <head>,
// so the page never flashes the wrong colors before this file loads.

const prefersReducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

// ===== THEME TOGGLE =====
document.getElementById("toggleTheme")?.addEventListener("click", () => {
  const root = document.documentElement;
  const next = root.classList.contains("theme-dark") ? "theme-light" : "theme-dark";
  root.classList.remove("theme-dark", "theme-light");
  root.classList.add(next);
  try { localStorage.setItem("theme", next); } catch (e) {}
});

// ===== MOBILE MENU =====
const menuToggle = document.getElementById("menuToggle");
function setMenu(open) {
  document.body.classList.toggle("nav-open", open);
  menuToggle.setAttribute("aria-expanded", String(open));
  menuToggle.setAttribute("aria-label", open ? "Close menu" : "Open menu");
}
menuToggle?.addEventListener("click", () => setMenu(!document.body.classList.contains("nav-open")));
document.addEventListener("keydown", (e) => {
  if (e.key === "Escape" && document.body.classList.contains("nav-open")) setMenu(false);
});

// ===== HEADER: solid once you scroll past the top (homepage floats it over the hero) =====
const header = document.getElementById("siteHeader");
function updateHeader() { header?.classList.toggle("is-scrolled", window.scrollY > 40); }
updateHeader();
window.addEventListener("scroll", updateHeader, { passive: true });

// ===== FLASH MESSAGES =====
document.querySelectorAll(".flash").forEach((flash) => {
  flash.querySelector("[data-dismiss]")?.addEventListener("click", () => flash.remove());
  setTimeout(() => flash.remove(), 7000);
});

// ===== IMAGE FADE-IN =====
document.querySelectorAll("img.fade-img").forEach((img) => {
  const show = () => img.classList.add("is-loaded");
  if (img.complete) show();
  else {
    img.addEventListener("load", show);
    img.addEventListener("error", show); // still show alt text if it fails
  }
});

// ===== REVEAL ON SCROLL =====
const revealEls = document.querySelectorAll(".reveal");
if ("IntersectionObserver" in window && !prefersReducedMotion) {
  const io = new IntersectionObserver((entries) => {
    entries.forEach((entry) => {
      if (entry.isIntersecting) {
        entry.target.classList.add("is-visible");
        io.unobserve(entry.target);
      }
    });
  }, { rootMargin: "0px 0px -8% 0px" });
  revealEls.forEach((el) => io.observe(el));
} else {
  revealEls.forEach((el) => el.classList.add("is-visible"));
}

// ===== HERO SLIDESHOW =====
(function () {
  const slides = [...document.querySelectorAll(".hero-slide")];
  const dots = [...document.querySelectorAll(".hero-dots button")];
  if (slides.length < 2) return;

  let current = 0;
  let timer;

  // Load the other slides only after the first one is on screen
  function loadRest() {
    slides.forEach((s) => { if (s.dataset.src) { s.src = s.dataset.src; delete s.dataset.src; } });
  }
  if (slides[0].complete) loadRest(); else slides[0].addEventListener("load", loadRest);

  function show(i) {
    slides[current].classList.remove("is-active");
    dots[current]?.setAttribute("aria-current", "false");
    current = (i + slides.length) % slides.length;
    slides[current].classList.add("is-active");
    dots[current]?.setAttribute("aria-current", "true");
  }
  function start() { if (!prefersReducedMotion) timer = setInterval(() => show(current + 1), 6000); }

  dots.forEach((dot, i) => dot.addEventListener("click", () => { clearInterval(timer); show(i); start(); }));
  document.addEventListener("visibilitychange", () => { clearInterval(timer); if (!document.hidden) start(); });
  start();
})();

// ===== GALLERY FILTERS + LIGHTBOX =====
(function () {
  const grid = document.querySelector("[data-gallery]");
  if (!grid) return;
  const tiles = [...grid.querySelectorAll(".tile")];
  const chips = [...document.querySelectorAll(".chip[data-filter]")];

  function applyFilter(filter) {
    chips.forEach((c) => c.setAttribute("aria-pressed", String(c.dataset.filter === filter)));
    tiles.forEach((t) => { t.hidden = filter !== "all" && t.dataset.tag !== filter; });
    const url = new URL(window.location);
    if (filter === "all") url.searchParams.delete("filter"); else url.searchParams.set("filter", filter);
    history.replaceState({}, "", url);
  }
  chips.forEach((chip) => chip.addEventListener("click", () => applyFilter(chip.dataset.filter)));
  const initial = new URLSearchParams(window.location.search).get("filter");
  if (initial && chips.some((c) => c.dataset.filter === initial)) applyFilter(initial);

  // Lightbox
  const box = document.getElementById("lightbox");
  if (!box || typeof box.showModal !== "function") return;
  const img = box.querySelector("img");
  const counter = box.querySelector("[data-counter]");
  const caption = box.querySelector("[data-caption]");
  let visible = [];
  let index = 0;

  function render() {
    const tile = visible[index];
    img.classList.add("is-loading");
    img.onload = () => img.classList.remove("is-loading");
    img.src = tile.dataset.full;
    img.alt = tile.querySelector("img").alt;
    counter.textContent = `${index + 1} / ${visible.length}`;
    caption.textContent = tile.dataset.tag;
    // warm the cache for the neighbours
    [index - 1, index + 1].forEach((n) => {
      const t = visible[(n + visible.length) % visible.length];
      if (t) new Image().src = t.dataset.full;
    });
  }
  function open(tile) {
    visible = tiles.filter((t) => !t.hidden);
    index = visible.indexOf(tile);
    render();
    box.showModal();
  }
  function step(d) { index = (index + d + visible.length) % visible.length; render(); }

  tiles.forEach((tile) => tile.addEventListener("click", () => open(tile)));
  box.querySelector("[data-prev]").addEventListener("click", () => step(-1));
  box.querySelector("[data-next]").addEventListener("click", () => step(1));
  box.querySelector("[data-close]").addEventListener("click", () => box.close());
  box.addEventListener("keydown", (e) => {
    if (e.key === "ArrowLeft") step(-1);
    if (e.key === "ArrowRight") step(1);
  });
  // click on the dark area (not the photo or buttons) closes
  box.addEventListener("click", (e) => { if (e.target.classList.contains("lightbox-stage")) box.close(); });

  // swipe on touch screens
  let startX = null;
  box.addEventListener("touchstart", (e) => { startX = e.touches[0].clientX; }, { passive: true });
  box.addEventListener("touchend", (e) => {
    if (startX === null) return;
    const dx = e.changedTouches[0].clientX - startX;
    if (Math.abs(dx) > 50) step(dx < 0 ? 1 : -1);
    startX = null;
  });
})();
