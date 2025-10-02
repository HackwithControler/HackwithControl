/**
 * Article Page JavaScript
 * - TOC scroll highlighting
 * - Smooth scroll to sections
 */

document.addEventListener('DOMContentLoaded', function() {
    // Get all TOC links and article headings
    const tocLinks = document.querySelectorAll('.toc-link');
    const headings = document.querySelectorAll('.article-content h2, .article-content h3');

    if (tocLinks.length === 0 || headings.length === 0) {
        return;
    }

    // Smooth scroll to section when clicking TOC link
    tocLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            const targetId = this.getAttribute('href').substring(1);
            const targetElement = document.getElementById(targetId);

            if (targetElement) {
                const headerOffset = 100;
                const elementPosition = targetElement.getBoundingClientRect().top;
                const offsetPosition = elementPosition + window.pageYOffset - headerOffset;

                window.scrollTo({
                    top: offsetPosition,
                    behavior: 'smooth'
                });
            }
        });
    });

    // Highlight current section in TOC based on scroll position
    function highlightCurrentSection() {
        let currentHeading = null;
        const scrollPosition = window.scrollY + 150;

        // Find the current heading based on scroll position
        headings.forEach(heading => {
            const headingTop = heading.offsetTop;
            if (scrollPosition >= headingTop) {
                currentHeading = heading;
            }
        });

        // Remove all active classes
        tocLinks.forEach(link => link.classList.remove('active'));

        // Add active class to current section
        if (currentHeading) {
            const currentId = currentHeading.getAttribute('id');
            const currentLink = document.querySelector(`.toc-link[href="#${currentId}"]`);
            if (currentLink) {
                currentLink.classList.add('active');
            }
        }
    }

    // Throttle function to limit scroll event frequency
    function throttle(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }

    // Listen to scroll events with throttling
    const throttledHighlight = throttle(highlightCurrentSection, 100);
    window.addEventListener('scroll', throttledHighlight);

    // Initial highlight on page load
    highlightCurrentSection();

    // Add scroll progress indicator (optional enhancement)
    createScrollProgress();
});

/**
 * Create a scroll progress indicator at the top of the page
 */
function createScrollProgress() {
    const progressBar = document.createElement('div');
    progressBar.style.cssText = `
        position: fixed;
        top: 0;
        left: 0;
        height: 3px;
        background: var(--primary, #00ff41);
        width: 0%;
        z-index: 1000;
        transition: width 0.1s ease;
        box-shadow: 0 0 10px var(--primary, #00ff41);
    `;
    document.body.appendChild(progressBar);

    window.addEventListener('scroll', () => {
        const windowHeight = document.documentElement.scrollHeight - document.documentElement.clientHeight;
        const scrolled = (window.scrollY / windowHeight) * 100;
        progressBar.style.width = scrolled + '%';
    });
}
