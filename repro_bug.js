const { parseClipboardFormat, formatClipboard } = require('./src/app/static/js/logic.js');

const testCases = [
    {
        name: "Empty text",
        input: "",
        expectedChannels: 0
    },
    {
        name: "BTECH UV format (with header)",
        input: 'Copy this text and start BTECH UV{"chs":[{"n":"Test","rf":462.5,"tf":462.5}]}',
        expectedChannels: 1
    },
    {
        name: "JSON only (without header)",
        input: '{"chs":[{"n":"Test","rf":462.5,"tf":462.5}]}',
        expectedChannels: 1
    },
    {
        name: "BTECH UV format (with extra text before JSON)",
        input: 'Some random text before {"chs":[{"n":"Test","rf":462.5,"tf":462.5}]}',
        expectedChannels: 1
    },
    {
        name: "Malformed JSON",
        input: 'Copy this text and start BTECH UV{"chs":[',
        expectedChannels: 0
    },
    {
        name: "JSON with trailing text (The Bug!)",
        input: 'Copy this．text and start BTECH UV{"chs":[{"n":"Test","rf":462.5,"tf":462.5}]}} Extra text',
        expectedChannels: 1
    }
];

testCases.forEach(tc => {
    try {
        const channels = parseClipboardFormat(tc.input);
        const count = channels.length;
        if (count === tc.expectedChannels) {
            console.log(`✅ PASS: ${tc.name} (found ${count} channels)`);
        } else {
            console.error(`❌ FAIL: ${tc.name} (expected ${tc.expectedChannels}, found ${count})`);
        }
    } catch (e) {
        console.error(`❌ ERROR: ${tc.name} - ${e.message}`);
    }
});
