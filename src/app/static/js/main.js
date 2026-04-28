document.addEventListener('DOMContentLoaded', () => {
    console.log("Converter UI loaded");

    let pendingText = null;

    // --- Helpers ---

    function parseClipboardFormat(text) {
        try {
            const lines = text.trim().split('\n');
            if (lines.length < 3 || lines[0] !== 'Copy this text and start BTECH UV' || lines[1] !== 'chs') {
                return [];
            }
            const jsonStr = lines.slice(2).join('\n');
            return JSON.parse(jsonStr);
        } catch (e) {
            console.error("Error parsing clipboard format:", e);
            return [];
        }
    }

    function formatClipboard(channels) {
        const header = 'Copy this text and start BTECH UV\nchs';
        const jsonStr = JSON.stringify(channels, null, 0);
        return `${header}\n${jsonStr}`;
    }

    // --- Event Listeners ---

    // 0. Handle Location & Import (using event delegation)
    document.addEventListener('click', async (event) => {
        const locationBtn = event.target.closest('#get-location-btn');
        const importBtn = event.target.closest('#import-repeaters-btn');

        if (importBtn) {
            handleImportRepeaters(importBtn);
            return;
        }

        if (locationBtn) {
            if (!navigator.geolocation) {
                alert("Geolocation is or not supported by your browser");
                return;
            }

            locationBtn.textContent = "Locating...";
            locationBtn.disabled = true;

            navigator.geolocation.getCurrentPosition(
                async (position) => {
                    const lat = position.coords.latitude;
                    const lon = position.coords.longitude;

                    try {
                        const response = await fetch('/api/location', {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify({ latitude: lat, longitude: lon })
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
                        locationBtn.textContent = "Get Location";
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
        }
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

                const textarea = document.querySelector('textarea[name="content"]');
                if (textarea) {
                    textarea.value = content;
                }
            };
            reader.readAsText(file);
        }
    });

    // 2. Handle tab switching
    document.addEventListener('click', (event) => {
        const tab = event.target.closest('.nav-clip-link'); // Wait, I should check the actual class in HTML
        // I will use a more generic selector or check the actual class from the HTML
        // Looking at previous edits, it was .nav-link
        const navLink = event.target.closest('.nav-link');
        if (navLink) {
            const container = navLink.closest('.nav-tabs');
            if (container) {
                const links = container.querySelectorAll('.nav-link');
                links.forEach(link => link.classList.remove('active'));
                navLink.classList.add('active');

                const tabId = navLink.id;
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

    // 3. Listen for HTMX swaps
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

    // 4. Handle "Result:" label click to copy to clipboard
    document.addEventListener('click', (event) => {
        const label = event.target.closest('label.form-label');
        if (label && label.textContent.trim() === 'Result:') {
            const container = label.parentElement;
            const textarea = container.querySelector('textarea');
            if (textarea && textarea.value) {
                navigator.clipboard.writeText(textarea.value).then(() => {
                    const originalText = label.textContent;
                    label.textContent = 'Result: (Copied!)';
                    label.classList.add('text-success');
                    setTimeout(() => {
                        label.textContent = originalText;
                        label.classList.remove('text-success');
                    }, 2000);
                }).catch(err => {
                    console.error('Failed to copy text: ', err);
                });
            }
        }
    });


    // --- Core Logic Functions ---

    async function handleImportRepeaters(importBtn) {
        if (!navigator.geolocation) {
            alert("Geolocation is not supported by your browser");
            return;
        }

        const originalText = importBtn.textContent;
        importBtn.textContent = "Locating...";
        importBtn.disabled = true;

        navigator.geolocation.getCurrentPosition(
            async (position) => {
                const lat = position.coords.latitude;
                const lon = position.coords.longitude;

                try {
                    const response = await fetch('/api/import-repeaters', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ latitude: lat, longitude: lon })
                    });

                    const data = await response.json();
                    if (!response.ok) throw new Error(data.error);

                    const newRepeaters = data.repeaters;
                    const textarea = document.querySelector('textarea[name="content"]');
                    const currentContent = textarea ? textarea.value : '';
                    const existingChannels = parseClipboardFormat(currentContent);

                    if (existingChannels.length === 0) {
                        // Just import all new ones (up to 30)
                        textarea.value = formatClipboard(newRepeaters.slice(0, 30));
                        alert("Imported 30 new repeaters!");
                    } else {
                        // Show pinning UI
                        showPinningUI(existingChannels, newRepeaters);
                    }

                    importBtn.textContent = originalText;
                    importBtn.disabled = false;
                } catch (error) {
                    console.error("Import failed:", error);
                    alert(`Import failed: ${error.message}`);
                    importBtn.textContent = originalText;
                    importBtn.disabled = false;
                }
            },
            (error) => {
                console.error("Error getting location:", error);
                alert(`Error getting location: ${error.message}`);
                importBtn.textContent = originalText;
                importBtn.disabled = false;
            }
        );
    }

    function showPinningUI(existingChannels, newRepeaters) {
        const resultDiv = document.getElementById('result');
        let html = `
            <div class="card mt-3">
                <div class="card-header">Pin existing channels to keep them during import</div>
                <div class="card-body" style="max-height: 300px; overflow-y: auto;">
                    <ul class="list-group list-group-flush">
        `;

        existingChannels.forEach((ch, index) => {
            html += `
                <li class="list-group-item">
                    <div class="form-check">
                        <input class="form-check-input channel-pin-check" type="checkbox" value="${index}" id="pin-${index}" checked>
                        <label class="form-check-label" for="pin-${index}">
                            ${ch.n} (${ch.rf} MHz)
                        </label>
                    </div>
                </li>
            `;
        });

        html += `
                    </ul>
                </div>
                <div class="card-footer text-end">
                    <button id="apply-import-btn" class="btn btn-success">Apply Import</button>
                    <button id="cancel-import-btn" class="btn btn-secondary">Cancel</button>
                </div>
            </div>
        `;

        resultDiv.innerHTML = html;

        // Attach events to new buttons
        document.getElementById('apply-import-btn').onclick = () => {
            const checkedIndices = Array.from(document.querySelectorAll('.channel-pin-check:checked')).map(el => parseInt(el.value));
            const pinnedChannels = checkedIndices.map(idx => existingChannels[idx]);
            
            // Merge pinned with new (limit 30)
            const merged = [...pinnedChannels, ...newRepeaters].slice(0, 30);
            
            const textarea = document.querySelector('textarea[name="content"]');
            textarea.value = formatClipboard(merged);
            
            resultDiv.innerHTML = '';
            alert("Import applied successfully!");
        };

        document.getElementById('cancel-import-btn').onclick = () => {
            resultDiv.innerHTML = '';
        };
    }
});
