const http = require('http');
const fs = require('fs');
const path = require('path');

const PORT = process.env.PORT || 3000;
const PUBLIC_DIR = path.join(__dirname, 'public');
const LOIS = JSON.parse(fs.readFileSync(path.join(__dirname, 'data', 'lois.json'), 'utf8'));

const votes = {};
for (const loi of LOIS) {
  votes[loi.id] = { pour: 0, contre: 0, abstention: 0 };
}

const MIME = {
  '.html': 'text/html; charset=utf-8',
  '.css': 'text/css; charset=utf-8',
  '.js': 'text/javascript; charset=utf-8',
  '.json': 'application/json; charset=utf-8',
  '.svg': 'image/svg+xml',
  '.png': 'image/png',
  '.ico': 'image/x-icon'
};

function resumeIA(loi) {
  const total = loi.points_cles.length;
  return {
    titre: loi.titre,
    resume:
      `En deux mots : « ${loi.titre} ». ${loi.expose} ` +
      `Les points à retenir (${total}) : ${loi.points_cles.join(' ; ')}. ` +
      `En pratique, cette loi change le quotidien des citoyens sur ce sujet précis ; le débat porte surtout sur son coût et sa mise en œuvre.`,
    source: 'simulation'
  };
}

function sendJson(res, status, data) {
  const body = JSON.stringify(data);
  res.writeHead(status, { 'Content-Type': 'application/json; charset=utf-8' });
  res.end(body);
}

function readBody(req) {
  return new Promise((resolve, reject) => {
    let data = '';
    req.on('data', (chunk) => {
      data += chunk;
      if (data.length > 1e6) req.destroy();
    });
    req.on('end', () => {
      try {
        resolve(data ? JSON.parse(data) : {});
      } catch (err) {
        reject(err);
      }
    });
    req.on('error', reject);
  });
}

function loisAvecVotes() {
  return LOIS.map((loi) => ({ ...loi, votes: votes[loi.id] }));
}

function serveStatic(req, res, pathname) {
  const rel = pathname === '/' ? 'index.html' : pathname.replace(/^\/+/, '');
  const filePath = path.join(PUBLIC_DIR, path.normalize(rel));
  if (!filePath.startsWith(PUBLIC_DIR)) {
    res.writeHead(403);
    res.end('Interdit');
    return;
  }
  fs.readFile(filePath, (err, content) => {
    if (err) {
      res.writeHead(404, { 'Content-Type': 'text/plain; charset=utf-8' });
      res.end('Non trouvé');
      return;
    }
    res.writeHead(200, { 'Content-Type': MIME[path.extname(filePath)] || 'application/octet-stream' });
    res.end(content);
  });
}

const server = http.createServer(async (req, res) => {
  const url = new URL(req.url, `http://localhost:${PORT}`);
  const pathname = url.pathname;

  if (pathname === '/api/lois' && req.method === 'GET') {
    sendJson(res, 200, loisAvecVotes());
    return;
  }

  const voteMatch = pathname.match(/^\/api\/lois\/([\w-]+)\/vote$/);
  if (voteMatch && req.method === 'POST') {
    const loi = LOIS.find((l) => l.id === voteMatch[1]);
    if (!loi) {
      sendJson(res, 404, { erreur: 'Loi inconnue' });
      return;
    }
    try {
      const body = await readBody(req);
      const choix = body.choix;
      if (!['pour', 'contre', 'abstention'].includes(choix)) {
        sendJson(res, 400, { erreur: "Le choix doit être 'pour', 'contre' ou 'abstention'" });
        return;
      }
      votes[loi.id][choix] += 1;
      sendJson(res, 200, { ok: true, loi: loi.id, choix, votes: votes[loi.id] });
    } catch (err) {
      sendJson(res, 400, { erreur: 'Corps de requête JSON invalide' });
    }
    return;
  }

  const resumeMatch = pathname.match(/^\/api\/lois\/([\w-]+)\/resume-ia$/);
  if (resumeMatch && req.method === 'GET') {
    const loi = LOIS.find((l) => l.id === resumeMatch[1]);
    if (!loi) {
      sendJson(res, 404, { erreur: 'Loi inconnue' });
      return;
    }
    sendJson(res, 200, resumeIA(loi));
    return;
  }

  if (pathname.startsWith('/api/')) {
    sendJson(res, 404, { erreur: 'Endpoint inconnu' });
    return;
  }

  serveStatic(req, res, pathname);
});

server.listen(PORT, () => {
  console.log(`Député virtuel démarré sur http://localhost:${PORT}`);
});
