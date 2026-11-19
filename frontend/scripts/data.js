/**
 * OpenGlaze Data — UI constants only
 * Glaze and combination data is loaded from the API at runtime
 */

const FAMILY_ORDER = ['Reds', 'Yellows', 'Greens', 'Blues', 'Purples', 'Browns', 'Neutrals', 'Whites', 'Clears', 'Shinos', 'Crystals', 'Reactive'];

// The API and database store family as a singular lowercase key ("blue",
// "shino"). The UI — FAMILY_ORDER, the sidebar filters and family checks in
// components — uses the plural title-case keys above. normalizeFamily()
// translates API values onto UI keys so both vocabularies stay in one place.
const FAMILY_KEY_ALIASES = {
    red: 'Reds',
    yellow: 'Yellows',
    green: 'Greens',
    blue: 'Blues',
    purple: 'Purples',
    brown: 'Browns',
    neutral: 'Neutrals',
    white: 'Whites',
    clear: 'Clears',
    shino: 'Shinos',
    crystal: 'Crystals',
    reactive: 'Reactive',
};

function normalizeFamily(rawFamily) {
    if (!rawFamily) return null;
    const value = String(rawFamily).trim();
    if (FAMILY_ORDER.includes(value)) return value;
    return FAMILY_KEY_ALIASES[value.toLowerCase()] || null;
}

window.FAMILY_ORDER = FAMILY_ORDER;
window.FAMILY_KEY_ALIASES = FAMILY_KEY_ALIASES;
window.normalizeFamily = normalizeFamily;
