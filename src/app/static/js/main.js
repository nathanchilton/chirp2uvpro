document.addEventListener('DOMContentLoaded', () => {
    console.log("Converter UI loaded");

    let pendingText = null;

    // 0. Handle Location Retrieval (using event delegation)
    document.addEventListener('click', (event) => {
        const locationBtn = event.target.closest('#get-location-btn');
        if (!locationBtn) return;

        if (!navigator.geolocation) {
            alert("Geolocation is not supported by your browser");
            return;
        }

        locationBtn.textContent = "Locating...";
        locationBtn.disabled = true;

        navigator.geolocation.getCurrentPosition(
            async (position) => {
                const lat = position.coords.latitude;
                const lon =
                    position.coords.longitude;

                try {
                    const response = await fetch('/api/location', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json'
                        },
                        body: JSON.stringify({
                            latitude: lat,
                            longitude: lon
                        })
                    });

                    const result = await response.json();

                    if (response.ok) {
                        alert(`Location found: ${lat.toFixed(4)}, ${lon.toFixed(4)}`);
                        locationBtn.textContent = "Location Updated";
                    } else {
                        alert(`Error: ${result.error}`);
                        locationBtn.textContent = "Get Location";
                        locationBtn.disabled = false;
                    }
                } catch (error) {
                    console.error("Error sending location:", error);
                    alert("Failed to send location to server");
                    locationBtn.textContent = "Get enough";
                    locationBtn.disabled = false;
                }
            },
            (error) => {
                console.error("Error getting location:", error);
                alert(`Error getting location: ${error.message}`);
                locationBtn.textContent = "Get Location";
                locationBtn.disabled = false;
            }
        );
    });

    // 1. Listen for file changes
    document.addEventListener('change', (event) => {
        if (event.target && event.target.id === 'file-input') {
            const file = event.target.files[0];
            if (!file) return;

            const reader = new FileReader();
            reader.onload = (e) => {
                const content = e.target.result;
                pendingText = content;

                // If the textarea is already in the DOM, update it immediately
                const textarea = document.querySelector('textarea[name="content"]');
                if (textarea) {
                    textarea.value = content;
                }
            };
            reader.readAsText(file);
        }
    });

    // 2. Handle tab switching by toggling visibility
    document.addEventListener('click', (event) => {
        const tab = event.target.closest('.nav-link');
        if (tab) {
            const container = tab.closest('.nav-tabs');
            if (container) {
                // Update active class on tabs
                const links = container.querySelectorAll('.nav-link');
                links.forEach(link => link.classList.remove('active'));
                tab.classList.add('active');

                // Toggle visibility of tab content
                const tabId = tab.id; // 'upload-tab' or 'text-tab'
                const uploadContent = document.getElementById('upload-tab-content');
                const textContent = document.getElementById('text-tab-content');

                if (uploadContent && textContent) {
                    if (tabId === 'upload-tab') {
                        uploadContent.classList.remove('hidden');
                        textContent.classList.add('hidden');
                    } else {
                        uploadContent.classList.add('hidden');
                        textContent.classList.remove('hidden');
                    }
                }
            }
        }
    });

    // 3. Listen for HTMX swaps to populate the textarea if pendingText exists
    // This is useful if HTMX is used for anything that might re-render the form
    document.addEventListener('htmx:afterSwap', (event) => {
        const target = event.detail.target;
        if (target && (target.id === 'converter-tab-content' || target.closest('#converter-tab-content'))) {
            if (pendingText) {
                const textarea = document.querySelector('textarea[name="content"]');
                if (textarea) {
                    textarea.value = pendingText;
                }
            }
        }
    });
});