// --- Core Logic Functions ---

/**
 * Converts frequency in Hz to MHz.
 * @param {number} hz 
 * @returns {number}
 */
function hzToMhz(hz) {
    return hz / 1000000;
}

/**
 * Converts frequency in MHz to Hz.
 * @param {number|string} mhz 
 * @returns {number}
 */
function mhzToHz(mhz) {
    return mhz * 1000000;
}

/**
 * Parses the BTECH UV clipboard format.
 * @param {string} text - The text to parse.
 * @returns {Array} An array of channel objects with long names.
 */
function parseClipboardFormat(text) {
    try {
        const trimmed = text.trim();
        
        // 1. Try to find JSON first (by looking for { or [), as in the Python implementation
        const jsonStart = trimmed.search(/[\[\{]/);
        if (jsonStart !== -1) {
            const jsonStr = trimmed.substring(jsonStart);
            // We need to find the end of the JSON structure. 
            // Since JSON can contain nested braces, a simple regex might not be enough if there's trailing text.
            // But for this specific use case, we can try to find the last matching brace.
            let jsonEnd = -1;
            let braceCount = 0;
            for (let i = 0; i < jsonStr.length; i++) {
                if (jsonStr[i] === '{' || jsonStr[i] === '[') {
                    braceCount++;
                } else if (jsonStr[i] === '}' || jsonStr[i] === ']') {
                    braceCount--;
                    if (braceCount === 0) {
                        jsonEnd = i;
                        break;
                    }
                }
            }

            const finalJsonStr = jsonEnd !== -1 ? jsonStr.substring(0, jsonEnd + 1) : jsonStr;
            const parsed = JSON.parse(finalJsonStr);

            // Extract the array of channels
            let channelsArray = [];
            if (Array.isArray(parsed)) {
                channelsArray = parsed;
            } else if (parsed && parsed.chs && Array.isArray(parsed.chs)) {
                channelsArray = parsed.chs;
            }

            // Map short names to long names and perform conversions
            return channelsArray.map(ch => {
                const name = ch.name || ch.n || '';
                
                // Frequency conversion (handle both MHz and Hz)
                const parseFreq = (val) => {
                    const f = parseFloat(val);
                    if (isNaN(f)) return 0;
                    return f < 1000 ? f * 1000000 : f;
                };
                
                const rx_freq_hz = parseFreq(ch.rx_freq_hz || ch.rf || 0);
                const tx_freq_hz = parseFreq(ch.tx_freq_hz || ch.tf || 0);
                
                // Sub-audio conversion (handle both kHz and Hz)
                const parseSubAudio = (val) => {
                    const f = parseFloat(val);
                    if (isNaN(f)) return 0;
                    return f < 1.0 ? f * 1000 : f;
                };
                
                const tx_sub_audio_hz = parseSubAudio(ch.tx_sub_audio_hz || ch.ts || 0);
                const rx_sub_audio_hz = parseSubAudio(ch.rx_sub_audio_hz || ch.rs || 0);
                
                // Scan conversion
                const scan = String(ch.scan !== undefined ? ch.scan : (ch.s !== undefined ? ch.s : '0'))
                    .trim() === '1' || String(ch.scan).toLowerCase() === 'true' || String(ch.s).toLowerCase() === 'true';
        
                // Power conversion
                const parsePower = (val) => {
                    const p = String(val || 'M').toUpperCase();
                    if (p === 'H' || p.includes('4.0W')) return 'H';
                    if (p === 'M' || p.includes('2.5W')) return 'M';
                    if (p === 'L' || p.includes('1.0W')) return 'L';
                    return p;
                };
                const tx_power = parsePower(ch.tx_power || ch.p || 'M');
        
                return {
                    name: name,
                    rx_freq_hz: rx_freq_hz,
                    tx_freq_hz: tx_freq_hz,
                    tx_sub_audio_hz: tx_sub_audio_hz,
                    rx_sub_audio_hz: rx_sub_audio_hz,
                    scan: scan,
                    tx_power: tx_power
                };
            });
        }

        // 2. If no JSON found, check for specific headers (fallback/CSV placeholder)
        const commonHeaders = [
            'Copy this text and start BTECH UV',
            'Copy this text and start BWE/BTECH JSON',
            'BTECH UV'
        ];
        
        if (commonHeaders.some(h => trimmed.startsWith(h))) {
            // In a real implementation, we could add CSV parsing here.
            // For now, we just return empty as we don't have a CSV parser in JS.
            return [];
        }

        return [];
    } catch (e) {
        console.error("Error parsing clipboard format:", e);
        return [];
    }
}

/**
 * Formats an array of channels into the BATCH BTECH UV clipboard format (short names).
 * @param {Array} channels - An array of channel objects with long names.
 * @returns {string} The formatted string.
 */
function formatClipboard(channels) {
    const header = 'Copy this text and start BTECH UV';
    const chs = channels.map(ch => ({
        n: ch.name,
        rf: ch.rx_freq_hz / 1000000,
        tf: ch.tx_freq_hz / 1000000,
        ts: ch.tx_sub_audio_hz / 1000,
        rs: ch.rx_sub_audio_hz / 1000,
        s: ch.scan ? 1 : 0,
        p: ch.tx_power
    }));
    
    const jsonStr = JSON.stringify({chs: chs}, null, 0);
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
        mergeChannels,
        hzToMhz,
        mhzToHz
    };
}
