"use strict";

/* ===============================
   NAVBAR SCRIPT
   =============================== */

document.addEventListener("DOMContentLoaded", function () {

    /* -------------------------------
       MOBILE MENU TOGGLE
    -------------------------------- */
    const navToggle = document.querySelector(".navigation__toggle");
    const navMenu = document.getElementById("navigation__level-one");

    if (navToggle && navMenu) {
        navToggle.addEventListener("click", function () {
            const expanded = this.getAttribute("aria-expanded") === "true";
            this.setAttribute("aria-expanded", String(!expanded));
            navMenu.classList.toggle("is-open");
        });
    }

    /* -------------------------------
       SUBMENU TOGGLE (MOBILE)
    -------------------------------- */
    document.querySelectorAll(".navigation__submenu-open-button").forEach(btn => {
        btn.addEventListener("click", function () {
            const target = document.querySelector(this.getAttribute("aria-controls"));
            if (target) target.classList.add("is-open");
        });
    });

    document.querySelectorAll(".navigation__submenu-close-button").forEach(btn => {
        btn.addEventListener("click", function () {
            const target = document.querySelector(this.getAttribute("aria-controls"));
            if (target) target.classList.remove("is-open");
        });
    });

});


/* ===============================
   LOGIN MODAL HANDLER (GLOBAL)
   =============================== */

/**
 * Called from navbar.html onclick
 */
function handleNavLoginClick() {
    const modal = document.getElementById("loginModal");

    if (!modal) {
        console.warn("Login modal not found");
        return;
    }

    // Bootstrap modal support
    if (typeof $ !== "undefined" && typeof $.fn.modal === "function") {
        $("#loginModal").modal("show");
    } else {
        // Fallback (non-bootstrap)
        modal.classList.add("show");
        modal.style.display = "flex";
        document.body.classList.add("modal-open");
    }
}
