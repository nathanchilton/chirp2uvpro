const { parseClipboardFormat, formatClipboard, mergeChannels } = require('../src/app/static/js/logic.js');

// --- Tests ---

const test = (name, fn) => {
    try {
        fn();
        console.log(`✅ ${name}`);
    } catch (e) {
        console.error(`❌ ${name}`);
        console.error(e);
        process.exit(1);
    }
    return true;
};

test('parseClipboardFormat - standard format (object)', () => {
    const input = 'Copy this text and start BTECH UV{"chs":[{"n":"Test","rf":"146.0"}]}';
    const result = parseClipboardFormat(input);
    if (result.length !== 1 || result[0].n !== 'Test') throw new Error('Failed to parse standard format');
});

test('parseClipboardFormat - array format', () => {
    const input = 'Copy this text and start BTECH UV[{"n":"Test","rf":"146.0"}]';
    const result = parseClipboardFormat(input);
    if (result.length !== 1 || result[0].n !== 'Test') throw new Error('Failed to parse array format');
});

test('parseClipboardFormat - invalid header', () => {
    const input = 'Wrong header [{"n":"Test"}]';
    const result = parseClipboardFormat(input);
    if (result.length !== 0) throw new Error('Should return empty array for invalid header');
});

test('formatClipboard - produces correct format (object)', () => {
    const channels = [{n: "Test", rf: "146.0"}];
    const output = formatClipboard(channels);
    if (!output.startsWith('Copy this text and start BTECH UV')) throw new Error('Invalid header');
    if (!output.includes('{"chs":[{"n":"Test","rf":"146.0"}]')) throw new Error('Missing data in correct format');
});

test('mergeChannels - merges and respects limit', () => {
    const pinned = [{n: "P1"}, {n: "P2"}];
    const newRpts = [{n: "N1"}, {n: "N2"}, {n: "N3"}];
    const result = mergeChannels(pinned, newRpts, 3);
    if (result.length !== 3) throw new Error('Failed to respect limit');
    if (result[0].n !== "P1" || result[2].n !== "N1") throw new Error('Incorrect merge order');
});

test('mergeChannels - respects limit with many channels', () => {
    const pinned = Array(20).fill(0).map((_, i) => ({n: `P${i}`}));
    const newRpts = Array(20).fill(0).map((_, i) => ({n: `N${i}`}));
    const result = mergeChannels(pinned, newRpts, 30);
    if (result.length !== 30) throw new Error('Failed to respect limit');
    if (result[0].n !== "P0" || result[29].n !== "N9") throw new Error('Incorrect merge order');
});

console.log("All tests passed!");
