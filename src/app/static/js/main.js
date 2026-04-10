console.log("Converter UI loaded");

document.addEventListener('DOMContentLoaded', () => {
    // The logic for form submission and file uploads is now handled by HTMX.
    // This file is being kept for any specialized client-side behavior that HTMX cannot easily handle.
});


                const data = await response.json();

                if (response.ok) {
                    let message = `Success: ${data.message}`;
                    if (data.warning) {
                        message += `\n\nWarning: ${data.warning}`;
                    }
                    if (data.output_filename) {
                        message += `\n\nOutput file: ${data.output_filename}`;
                    }
                    resultDiv.innerText = message;
                } else {
                    resultDiv.innerText = `Error: ${data.error || 'Unknown error occurred'}`;
                }
            } catch (error) {
                resultDiv.innerText = `Error: ${error.message}`;
            }
        });
    }

    // Handle file uploads
    const fileInput = document.getElementById('file-upload-input');
    if (fileInput) {
        fileInput.addEventListener('change', async (event) => {
            const file = event.target.files[0];
            if (!file) return;

            const formData = new FormData();
            formData.append('file', file);

            resultDiv.innerText = 'Uploading and converting...';

            try {
                const response = await fetch('/api/convert/upload', {
                    method: 'POST',
                    body: formData,
                });

                const data = await response.json();

                    if (response.ok) {
                        resultDiv.innerText = `Success: ${data.message}`;
                    } else {
                    resultDiv.innerText = `Error: ${data.error || 'Unknown error occurred'}`;
                }
            } catch (error) {
                resultDiv.innerText = `Error: ${error.message}`;
            }
        });
    }
});
