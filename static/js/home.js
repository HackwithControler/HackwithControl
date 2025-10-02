/**
 * Home Page JavaScript
 * - Matrix rain background
 * - Typing effect
 * - Stats counter animation
 * - Article filtering and search
 * - Tags cloud generation
 */

document.addEventListener('DOMContentLoaded', function() {
    initMatrixRain();
    initTypingEffect();
    initStatsCounter();
    initArticleFilters();
    initTagsCloud();
    initSmoothScroll();
});

/**
 * Matrix Rain Background Effect
 */
function initMatrixRain() {
    const canvas = document.getElementById('matrix-canvas');
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;

    const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789@#$%^&*()';
    const charArray = chars.split('');
    const fontSize = 14;
    const columns = canvas.width / fontSize;
    const drops = [];

    for (let i = 0; i < columns; i++) {
        drops[i] = Math.random() * -100;
    }

    function draw() {
        ctx.fillStyle = 'rgba(4, 7, 20, 0.05)';
        ctx.fillRect(0, 0, canvas.width, canvas.height);

        ctx.fillStyle = '#00ff41';
        ctx.font = fontSize + 'px monospace';

        for (let i = 0; i < drops.length; i++) {
            const text = charArray[Math.floor(Math.random() * charArray.length)];
            ctx.fillText(text, i * fontSize, drops[i] * fontSize);

            if (drops[i] * fontSize > canvas.height && Math.random() > 0.975) {
                drops[i] = 0;
            }
            drops[i]++;
        }
    }

    setInterval(draw, 33);

    window.addEventListener('resize', () => {
        canvas.width = window.innerWidth;
        canvas.height = window.innerHeight;
    });
}

/**
 * Terminal Typing Effect
 */
function initTypingEffect() {
    const typedTextElement = document.getElementById('typed-text');
    if (!typedTextElement) return;

    const commands = [
        'cat /etc/shadow',
        'nmap -sC -sV target',
        'python3 exploit.py',
        './pwn root.txt',
        'echo "pwned!"'
    ];

    let commandIndex = 0;
    let charIndex = 0;
    let isDeleting = false;

    function type() {
        const currentCommand = commands[commandIndex];

        if (isDeleting) {
            typedTextElement.textContent = currentCommand.substring(0, charIndex - 1);
            charIndex--;
        } else {
            typedTextElement.textContent = currentCommand.substring(0, charIndex + 1);
            charIndex++;
        }

        let typingSpeed = isDeleting ? 50 : 100;

        if (!isDeleting && charIndex === currentCommand.length) {
            typingSpeed = 2000;
            isDeleting = true;
        } else if (isDeleting && charIndex === 0) {
            isDeleting = false;
            commandIndex = (commandIndex + 1) % commands.length;
            typingSpeed = 500;
        }

        setTimeout(type, typingSpeed);
    }

    setTimeout(type, 1000);
}

/**
 * Stats Counter Animation
 */
function initStatsCounter() {
    const statNumbers = document.querySelectorAll('.stat-number');

    const observerOptions = {
        threshold: 0.5
    };

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const target = parseInt(entry.target.getAttribute('data-target'));
                animateCounter(entry.target, target);
                observer.unobserve(entry.target);
            }
        });
    }, observerOptions);

    statNumbers.forEach(stat => observer.observe(stat));
}

function animateCounter(element, target) {
    let current = 0;
    const increment = target / 50;
    const duration = 1500;
    const stepTime = duration / 50;

    const timer = setInterval(() => {
        current += increment;
        if (current >= target) {
            element.textContent = target;
            clearInterval(timer);
        } else {
            element.textContent = Math.floor(current);
        }
    }, stepTime);
}

/**
 * Article Filtering and Search
 */
function initArticleFilters() {
    const filterButtons = document.querySelectorAll('.filter-btn');
    const searchInput = document.getElementById('search-input');
    const articleCards = document.querySelectorAll('.article-card');

    // Filter by difficulty
    filterButtons.forEach(button => {
        button.addEventListener('click', function() {
            // Update active button
            filterButtons.forEach(btn => btn.classList.remove('active'));
            this.classList.add('active');

            const filter = this.getAttribute('data-filter');

            articleCards.forEach(card => {
                const difficulty = card.querySelector('.card-difficulty');
                if (!difficulty) return;

                const difficultyClass = Array.from(difficulty.classList)
                    .find(cls => ['easy', 'medium', 'hard', 'insane'].includes(cls));

                if (filter === 'all' || difficultyClass === filter) {
                    card.classList.remove('hidden');
                } else {
                    card.classList.add('hidden');
                }
            });
        });
    });

    // Search functionality
    if (searchInput) {
        searchInput.addEventListener('input', function(e) {
            const searchTerm = e.target.value.toLowerCase();

            articleCards.forEach(card => {
                const title = card.querySelector('.card-title')?.textContent.toLowerCase() || '';
                const description = card.querySelector('.card-description')?.textContent.toLowerCase() || '';
                const tags = Array.from(card.querySelectorAll('.card-tag'))
                    .map(tag => tag.textContent.toLowerCase())
                    .join(' ');

                const matchesSearch = title.includes(searchTerm) ||
                                    description.includes(searchTerm) ||
                                    tags.includes(searchTerm);

                if (matchesSearch) {
                    card.classList.remove('hidden');
                } else {
                    card.classList.add('hidden');
                }
            });
        });
    }
}

/**
 * Generate Tags Cloud from Articles
 */
function initTagsCloud() {
    const tagsCloudContainer = document.getElementById('tags-cloud');
    if (!tagsCloudContainer) return;

    // Collect all tags from articles
    const allTags = [];
    document.querySelectorAll('.card-tag').forEach(tagElement => {
        const tagText = tagElement.textContent.trim();
        allTags.push(tagText);
    });

    // Count tag frequency
    const tagCount = {};
    allTags.forEach(tag => {
        tagCount[tag] = (tagCount[tag] || 0) + 1;
    });

    // Sort by frequency
    const sortedTags = Object.entries(tagCount)
        .sort((a, b) => b[1] - a[1])
        .slice(0, 15); // Top 15 tags

    // Generate tag cloud HTML
    sortedTags.forEach(([tag, count]) => {
        const sizeClass = count >= 3 ? 'size-3' : count >= 2 ? 'size-2' : 'size-1';
        const tagElement = document.createElement('span');
        tagElement.className = `tag-cloud-item ${sizeClass}`;
        tagElement.textContent = `${tag} (${count})`;
        tagElement.addEventListener('click', () => filterByTag(tag));
        tagsCloudContainer.appendChild(tagElement);
    });
}

function filterByTag(tag) {
    const searchInput = document.getElementById('search-input');
    if (searchInput) {
        searchInput.value = tag;
        searchInput.dispatchEvent(new Event('input'));
        // Smooth scroll to articles
        document.getElementById('articles')?.scrollIntoView({ behavior: 'smooth' });
    }
}

/**
 * Smooth Scroll for Internal Links
 */
function initSmoothScroll() {
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
}
