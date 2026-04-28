// --- Core Logic Functions ---

/**
 * Parses the BTECH UV clipboard format.
 * @param {string} text - The text to parse.
 * @returns {Array} An array of channel objects.
 */
function parseClipboardFormat(text) {
    try {
        const trimmed = text.trim();
        const header = 'Copy this text and start BTECH UV';
        
        if (!trimmed.startsWith(header)) {
            return [];
        }

        // Find the start of the JSON (either '{' or '[')
        const jsonStart = trimmed.search(/[\[\{]/);
        if (jsonStart === -1) {
            return [];
        }

        const jsonStr = trimmed.substring(jsonStart);
        const parsed = JSON.parse(jsonStr);

        // If it's the object format {"chs": [...]}, extract the array
        if (parsed && parsed.chs && Array.isArray(parsed.chs)) {
            return parsed.chs;
        }

        // If it's already an array, return it
        if (Array.isArray(parsed)) {
            return parsed;
        }

        return [];
    } catch (e) {
        console.error("Error parsing clipboard format:", e);
        return [];
    }
}

/**
 * Formats an array of channels into the BTECH UV clipboard format.
 * @param {Array} channels - An array of channel objects.
 * @returns {string} The formatted string.
 */
function formatClipboard(channels) {
    const header = 'Copy this text and start BTECH UV';
    const jsonStr = JSON.stringify({chs: channels}, null, 0);
    return `${header}${jsonStr}`;
}

/**
 * Merges pinned channels with new repeater channels, up to a specified limit.
 * @param {Array} pinnedChannels - Array of channels the user wants to keep.
 * @param {Array} newRepeaters - Array of new channels to add.
 * @param {number} [limit=30] - Maximum number of channels in the resulting list.
 * @returns {Array} The merged and truncated array of channels.
 */
function mergeChannels(pinnedChannels, newRepeaters, limit = 30) {
    return [...pinnedChannels, ...newRepeaters].slice(0, limit);
}

// Expose to global scope for testing (if running in Node/test environment)
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        parseClipboardFormat,
        formatClipboard,
        mergeChannels
    };
}
