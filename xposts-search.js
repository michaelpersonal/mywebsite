const searchInput = document.getElementById('search');
const mode = document.getElementById('search-mode');
const status = document.getElementById('search-status');
const cards = Array.from(document.querySelectorAll('.post-card'));
const grid = cards[0]?.parentElement;
const count = document.getElementById('results-count');
const empty = document.getElementById('no-results');
let tag = 'all';
let timer;
let controller;
let revision = 0;
let hits = null;
let completedQuery = '';

function render() {
    const query = searchInput.value.trim().toLowerCase();
    const scores = hits && new Map(hits.map(hit => [hit.id, hit.score]));
    let visible = 0;
    const ordered = scores ? [...cards].sort((a,b) => (scores.get(b.dataset.id) ?? -Infinity) - (scores.get(a.dataset.id) ?? -Infinity)) : cards;
    for (const card of ordered) {
        const tags = JSON.parse(card.dataset.tagList || '[]');
        const match = !query || (mode.value === 'semantic' ? completedQuery === searchInput.value.trim() && scores?.has(card.dataset.id) : card.textContent.toLowerCase().includes(query));
        const show = match && (tag === 'all' || tags.includes(tag));
        card.style.display = show ? 'block' : 'none';
        if (show) visible++;
        grid?.appendChild(card);
    }
    count.textContent = `${visible} post${visible === 1 ? '' : 's'}`;
    empty.style.display = !visible && (hits !== null || !status.textContent) ? 'block' : 'none';
}

async function search(version) {
    const query = searchInput.value.trim();
    if (!query || mode.value === 'keyword') {
        hits = null;
        status.textContent = '';
        render();
        return;
    }
    controller = new AbortController();
    status.textContent = 'Searching by meaning…';
    render();
    try {
        const response = await fetch(`/api/xposts-search?q=${encodeURIComponent(query)}`, {signal:controller.signal});
        if (!response.ok) throw new Error('Search unavailable');
        const data = await response.json();
        if (version !== revision) return;
        hits = data.results;
        completedQuery = query;
        status.textContent = !hits.length ? 'No relevant posts found.' : data.matchType === 'literal' ? 'Posts mentioning your search term' : 'Related posts, sorted by relevance';
        render();
    } catch (error) {
        if (version !== revision || error.name === 'AbortError') return;
        hits = null;
        mode.value = 'keyword';
        status.textContent = 'Semantic search is unavailable here; showing keyword matches. Use the local Tailscale site for search by meaning.';
        render();
    }
}

function schedule() {
    revision++;
    controller?.abort();
    clearTimeout(timer);
    hits = null;
    status.textContent = '';
    const version = revision;
    if (!searchInput.value.trim() || mode.value === 'keyword') search(version);
    else {
        status.textContent = 'Searching by meaning…';
        render();
        timer = setTimeout(() => search(version), 350);
    }
}
searchInput.addEventListener('input', schedule);
mode.addEventListener('change', schedule);
document.querySelectorAll('.filter-btn').forEach(button => button.addEventListener('click', () => {
    document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
    button.classList.add('active');
    tag = button.dataset.filter;
    render();
}));
render();
