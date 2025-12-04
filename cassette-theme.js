document.addEventListener('DOMContentLoaded', () => {
    const body = document.body;
    let cassetteContainer = null;

    // Observer to detect theme changes
    const observer = new MutationObserver((mutations) => {
        mutations.forEach((mutation) => {
            if (mutation.type === 'attributes' && mutation.attributeName === 'data-theme') {
                handleThemeChange(body.getAttribute('data-theme'));
            }
        });
    });

    observer.observe(body, { attributes: true });

    // Initial check
    handleThemeChange(body.getAttribute('data-theme'));

    function handleThemeChange(theme) {
        if (theme === 'cassette') {
            initCassetteTheme();
        } else {
            destroyCassetteTheme();
        }
    }

    function initCassetteTheme() {
        if (document.getElementById('cassette-container')) return;

        console.log('Initializing Cassette Theme...');

        // Create Main Container
        cassetteContainer = document.createElement('div');
        cassetteContainer.id = 'cassette-container';

        // Create Label Area
        const label = document.createElement('div');
        label.classList.add('cassette-label');

        // Create Window Area
        const windowArea = document.createElement('div');
        windowArea.classList.add('cassette-window');

        // Create Reels
        const reelLeft = document.createElement('div');
        reelLeft.classList.add('reel');
        const reelRight = document.createElement('div');
        reelRight.classList.add('reel');

        // Create Tape Connection (visual only)
        const tapeConnection = document.createElement('div');
        tapeConnection.classList.add('tape-connection');

        // Assemble
        windowArea.appendChild(tapeConnection);
        windowArea.appendChild(reelLeft);
        windowArea.appendChild(reelRight);

        cassetteContainer.appendChild(label);
        cassetteContainer.appendChild(windowArea);

        // Insert as first child of body to be background
        body.insertBefore(cassetteContainer, body.firstChild);
    }

    function destroyCassetteTheme() {
        const container = document.getElementById('cassette-container');
        if (container) {
            container.remove();
        }
    }
});
