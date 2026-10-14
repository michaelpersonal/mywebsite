// Canonical website retrieval policy; publish-website copies this into the site.
function literalMatches(query, posts) {
    const trimmed = query.trim();
    const quoted = /^".*"$/.test(trimmed);
    const phrase = (quoted ? trimmed.slice(1,-1) : trimmed).toLowerCase();
    if (!phrase) return quoted ? [] : null;
    if (!quoted && phrase.split(/\s+/).length > 3) return null;
    const escaped = phrase.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
    const pattern = /^[a-z0-9]/i.test(phrase) && /[a-z0-9]$/i.test(phrase)
        ? new RegExp(`(^|[^a-z0-9_])${escaped}($|[^a-z0-9_])`, 'i') : null;
    const matches = posts.filter(p => pattern ? pattern.test(p.text || '') : (p.text || '').toLowerCase().includes(phrase));
    return matches.length || quoted ? matches : null;
}
function relevantHits(hits, limit=50) {
    const ranked = [...hits].sort((a,b) => b.score-a.score);
    if (!ranked.length) return [];
    const cutoff = Math.max(0.5, ranked[0].score-0.12);
    return ranked.filter(hit => hit.score >= cutoff).slice(0,limit);
}
function filterPosts(posts, {topic, tag, language}={}) {
    return posts.filter(p => (!topic || topic === 'all' || (p.topics || []).includes(topic))
        && (!tag || tag === 'all' || (p.tags || []).some(t => t.toLowerCase() === tag.toLowerCase()))
        && (!language || language === 'all' || (p.languages || []).includes(language)));
}
module.exports = {literalMatches, relevantHits, filterPosts};
