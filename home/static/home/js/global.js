/**
 * HireFlow Global UI Javascript - App Modular Version
 * Controls global components, responsive states, scroll behaviors, and common UI animations.
 */

document.addEventListener("DOMContentLoaded", () => {
    // 1. Initialize Bootstrap Tooltips and Popovers
    initBootstrapTooltips();

    // 2. Active Navigation Class Handler (Runs after navbar loads)
    document.addEventListener("componentLoaded", (e) => {
        if (e.detail.name === "navbar") {
            setActiveNavigationLink();
            initNavbarScrollEffect();
        }
    });
});

/**
 * Automatically initializes all Bootstrap 5 Tooltips on the page.
 */
function initBootstrapTooltips() {
    if (typeof bootstrap !== 'undefined') {
        const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        tooltipTriggerList.map(function (tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });
    }
}

/**
 * Checks the current URL and applies the '.active' class to the correct navigation item.
 */
function setActiveNavigationLink() {
    const currentPath = window.location.pathname;
    const navLinks = document.querySelectorAll(".nav-link");
    
    navLinks.forEach(link => {
        const href = link.getAttribute("href");
        if (!href) return;
        
        // Clean href queries or hashes for clean path checking
        const cleanHref = href.split('#')[0].split('?')[0];
        
        // Check if page path matches link href path
        if (currentPath.endsWith(cleanHref) || (currentPath === "/" && cleanHref.endsWith("index.html"))) {
            link.classList.add("active");
            link.setAttribute("aria-current", "page");
        } else {
            link.classList.remove("active");
        }
    });
}

/**
 * Adds styling (shadows/blur background) to the header navbar when the user scrolls down.
 */
function initNavbarScrollEffect() {
    const navbar = document.querySelector(".navbar");
    if (!navbar) return;
    
    const handleScroll = () => {
        if (window.scrollY > 20) {
            navbar.classList.add("glassmorphism", "shadow-sm", "border-bottom");
            navbar.style.borderBottomColor = "var(--hf-border-color)";
        } else {
            navbar.classList.remove("glassmorphism", "shadow-sm", "border-bottom");
        }
    };
    
    handleScroll();
    window.addEventListener("scroll", handleScroll);
}
