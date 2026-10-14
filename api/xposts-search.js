const fs = require('node:fs');
const path = require('node:path');
const {literalMatches, relevantHits} = require('../lib/xposts-ranking');
let index;
const MODEL = 'embeddinggemma-2';
const DIMENSIONS = 768;

module.exports = async function handler(req, res) {
    res.setHeader('Cache-Control', 'no-store');
    if (req.method !== 'GET') {
        res.setHeader('Allow', 'GET');
        return res.status(405).json({error: 'Use GET'});
    }
    const query = typeof req.query.q === 'string' ? req.query.q.trim() : '';
    if (!query || query.length > 500) {
        return res.status(400).json({error: 'Enter a query of 1–500 characters.'});
    }
    try {
        if (!index) {
            index = JSON.parse(fs.readFileSync(path.join(process.cwd(), 'xposts-embeddings.json'), 'utf8'));
            if (index.model !== MODEL || index.dimensions !== DIMENSIONS) {
                index = null;
                throw new Error('Incompatible index');
            }
        }
        const direct = literalMatches(query, index.posts);
        if (direct !== null) {
            return res.status(200).json({results:direct.slice(0,50).map(p => ({id:p.id,score:1})),matchType:'literal'});
        }
        const token = process.env.EMBED_TOKEN;
        if (!token) return res.status(503).json({error: 'Semantic search is not configured.'});
        const base = (process.env.X_EMBEDDING_BASE_URL || 'https://michael-macbook-pro.tailf96f46.ts.net:8443/v1').replace(/\/$/, '');
        const response = await fetch(`${base}/embeddings`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json', Authorization: `Bearer ${token}`},
            body: JSON.stringify({input: [query], prompt_name: 'query', dimensions: DIMENSIONS, model: MODEL, encoding_format: 'float'}),
            signal: AbortSignal.timeout(12000),
        });
        if (!response.ok) throw new Error(`Embedding service status ${response.status}`);
        const data = await response.json();
        const vector = data.data?.[0]?.embedding;
        if (data.model !== MODEL || !Array.isArray(vector) || vector.length !== DIMENSIONS || !vector.every(Number.isFinite)) {
            throw new Error('Invalid query embedding');
        }
        const norm = Math.hypot(...vector);
        if (!norm) throw new Error('Zero query embedding');
        const results = index.posts.map(post => ({
            id: post.id,
            score: post.vector.reduce((sum, value, i) => sum + value * vector[i] / norm, 0),
        })).sort((a, b) => b.score - a.score).slice(0, 50);
        return res.status(200).json({results:relevantHits(results),matchType:'semantic'});
    } catch (error) {
        console.error('Semantic search failed:', error.message);
        return res.status(503).json({error: 'Semantic search is unavailable. Try keyword search.'});
    }
};
