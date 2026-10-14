const test = require('node:test');
const assert = require('node:assert/strict');
const {literalMatches, relevantHits} = require('../lib/xposts-ranking');
const handler = require('../api/xposts-search');
const posts = require('../xposts-embeddings.json').posts;

test('Leopold lookup returns mentions only, even when embeddings are offline', async () => {
    const savedToken = process.env.EMBED_TOKEN;
    const savedFetch = global.fetch;
    delete process.env.EMBED_TOKEN;
    global.fetch = () => {throw new Error('Embedding service must not be called');};
    try {
        const res = {setHeader(){},status(code){this.code=code;return this},json(data){this.data=data}};
        await handler({method:'GET',query:{q:'leopold'}},res);
        assert.equal(res.code,200);
        assert.equal(res.data.matchType,'literal');
        const expected = posts.filter(p => /(^|[^a-z0-9_])leopold($|[^a-z0-9_])/i.test(p.text)).map(p=>p.id);
        assert(expected.length > 0);
        assert.deepEqual(res.data.results.map(p=>p.id).sort(), expected.sort());
    } finally {
        global.fetch = savedFetch;
        if (savedToken === undefined) delete process.env.EMBED_TOKEN;
        else process.env.EMBED_TOKEN = savedToken;
    }
});
test('literal matching respects Latin boundaries and Chinese adjacency', () => {
    assert.equal(literalMatches('leopold',[{text:'Leopoldine'}]),null);
    assert.equal(literalMatches('leopold',[{text:'Leopold的基金'}]).length,1);
    assert.deepEqual(literalMatches('"missing phrase"',posts),[]);
});
test('semantic search excludes weak neighbors instead of filling 50 results', () => {
    assert.deepEqual(relevantHits([{id:'a',score:.8},{id:'b',score:.7},{id:'c',score:.3}]).map(p=>p.id),['a','b']);
    assert.deepEqual(relevantHits([{score:.3}]),[]);
});
test('AI is a parent topic and literal results are not capped at fifty', async () => {
    const res={setHeader(){},status(code){this.code=code;return this},json(data){this.data=data}};
    await handler({method:'GET',query:{q:'AI',topic:'AI'}},res);
    const {filterPosts}=require('../lib/xposts-ranking');
    const expected=filterPosts(literalMatches('AI',posts),{topic:'AI'}).map(p=>p.id);
    assert.equal(res.code,200);
    assert(expected.length>50);
    assert.deepEqual(res.data.results.map(p=>p.id).sort(),expected.sort());
    assert(filterPosts(posts,{topic:'AI'}).length>7);
});
test('topic, specific tag and language scopes intersect before ranking', () => {
    const {filterPosts}=require('../lib/xposts-ranking');
    const sample=[
        {id:'a',topics:['AI'],tags:['Local LLM'],languages:['Chinese']},
        {id:'b',topics:['AI'],tags:['AI Agents'],languages:['English']},
        {id:'c',topics:['Business & Finance'],tags:[],languages:['Chinese']},
    ];
    assert.deepEqual(filterPosts(sample,{topic:'AI'}).map(p=>p.id),['a','b']);
    assert.deepEqual(filterPosts(sample,{topic:'AI',tag:'local llm',language:'Chinese'}).map(p=>p.id),['a']);
    assert.deepEqual(filterPosts(sample,{topic:'AI',language:'English'}).map(p=>p.id),['b']);
});
