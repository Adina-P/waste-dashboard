// Dark/light mode toggle. Loaded on every page (unlike app.js, which some
// pages skip). The early attribute-setting happens inline in <head> to avoid
// a flash of the wrong theme; this file just wires up the toggle button.
(function () {
  function effectiveTheme() {
    const stored = localStorage.getItem("theme");
    if (stored) return stored;
    return window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light";
  }

  function updateButton() {
    const btn = document.getElementById("theme-toggle");
    if (!btn) return;
    const dark = effectiveTheme() === "dark";
    btn.setAttribute("aria-label", dark ? "עבור למצב בהיר" : "עבור למצב כהה");
    btn.querySelector(".icon-sun").style.display = dark ? "block" : "none";
    btn.querySelector(".icon-moon").style.display = dark ? "none" : "block";
  }

  document.addEventListener("DOMContentLoaded", function () {
    updateButton();
    const btn = document.getElementById("theme-toggle");
    if (!btn) return;
    btn.addEventListener("click", function () {
      const next = effectiveTheme() === "dark" ? "light" : "dark";
      localStorage.setItem("theme", next);
      document.documentElement.setAttribute("data-theme", next);
      updateButton();
    });
  });
})();
