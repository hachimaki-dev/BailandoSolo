document.addEventListener('DOMContentLoaded', () => {
    const body = document.body;
    let ps2Container = null;

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
        if (theme === 'ps2') {
            initPS2Theme();
        } else {
            destroyPS2Theme();
        }
    }

    function initPS2Theme() {
        if (document.getElementById('ps2-background')) return;

        console.log('Initializing PS2 Theme Effects...');

        ps2Container = document.createElement('div');
        ps2Container.id = 'ps2-background';
        
        // Create Fog/Nebula Layers
        for (let i = 0; i < 4; i++) {
            const fog = document.createElement('div');
            fog.classList.add('ps2-fog');
            fog.style.animationDelay = `${i * -8}s`;
            fog.style.opacity = 0.3 + (i * 0.1);
            ps2Container.appendChild(fog);
        }

        // Create Crystals (Towers)
        const crystalCount = 20;
        for (let i = 0; i < crystalCount; i++) {
            const crystal = document.createElement('div');
            crystal.classList.add('ps2-crystal');
            
            // Random properties
            const size = Math.random() * 40 + 20; // 20px to 60px width
            const height = size * (Math.random() * 3 + 1); // Taller
            const x = Math.random() * 100;
            const y = Math.random() * 100;
            const depth = Math.random(); // 0 to 1 (1 is closer)
            
            crystal.style.width = `${size}px`;
            crystal.style.height = `${height}px`;
            crystal.style.left = `${x}%`;
            crystal.style.top = `${y}%`;
            
            // Store depth for parallax
            crystal.dataset.depth = depth + 0.2; // Base depth
            
            // Random float animation delay
            crystal.style.animationDelay = `${Math.random() * -5}s`;

            ps2Container.appendChild(crystal);
        }

        // Insert as first child of body to be background
        body.insertBefore(ps2Container, body.firstChild);
        
        document.addEventListener('mousemove', handleParallax);
    }

    function destroyPS2Theme() {
        const container = document.getElementById('ps2-background');
        if (container) {
            container.remove();
        }
        document.removeEventListener('mousemove', handleParallax);
    }

    function handleParallax(e) {
        if (body.getAttribute('data-theme') !== 'ps2') return;

        const mouseX = (e.clientX / window.innerWidth) - 0.5;
        const mouseY = (e.clientY / window.innerHeight) - 0.5;

        const crystals = document.querySelectorAll('.ps2-crystal');
        crystals.forEach(crystal => {
            const depth = parseFloat(crystal.dataset.depth);
            // Move opposite to mouse for background feel
            const moveX = mouseX * -100 * depth; 
            const moveY = mouseY * -50 * depth;
            
            crystal.style.setProperty('--parallax-x', `${moveX}px`);
            crystal.style.setProperty('--parallax-y', `${moveY}px`);
            
            // Rotate slightly based on mouse position for 3D feel
            const rotateY = mouseX * 20 * depth;
            const rotateX = mouseY * -20 * depth;
            crystal.style.setProperty('--rotate-x', `${rotateX}deg`);
            crystal.style.setProperty('--rotate-y', `${rotateY}deg`);
        });
        
        // Move fog
        const fogs = document.querySelectorAll('.ps2-fog');
        fogs.forEach((fog, index) => {
            const speed = (index + 1) * 30;
            fog.style.transform = `translate(${mouseX * speed}px, ${mouseY * speed}px) scale(1.2)`;
        });
    }
});
