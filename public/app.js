const conteneur = document.getElementById('lois');
const template = document.getElementById('carte-loi');

async function chargerLois() {
  const res = await fetch('/api/lois');
  const lois = await res.json();
  conteneur.innerHTML = '';
  for (const loi of lois) {
    conteneur.appendChild(renduLoi(loi));
  }
}

function renduLoi(loi) {
  const carte = template.content.cloneNode(true);
  carte.querySelector('.titre').textContent = loi.titre;
  carte.querySelector('.expose').textContent = loi.expose;
  const liste = carte.querySelector('.points');
  for (const point of loi.points_cles) {
    const li = document.createElement('li');
    li.textContent = point;
    liste.appendChild(li);
  }

  for (const bouton of carte.querySelectorAll('.vote')) {
    bouton.addEventListener('click', async () => {
      const choix = bouton.dataset.choix;
      await fetch(`/api/lois/${loi.id}/vote`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ choix })
      });
      await rafraichirResultats(carte, loi.id);
    });
  }

  carte.querySelector('.resume-ia').addEventListener('click', async () => {
    const bloc = carte.querySelector('.ia');
    bloc.hidden = false;
    bloc.textContent = 'L’IA réfléchit…';
    const res = await fetch(`/api/lois/${loi.id}/resume-ia`);
    const data = await res.json();
    bloc.textContent = data.resume;
  });

  afficherResultats(carte, loi.votes);
  return carte;
}

async function rafraichirResultats(carte, id) {
  const res = await fetch('/api/lois');
  const lois = await res.json();
  const loi = lois.find((l) => l.id === id);
  if (loi) afficherResultats(carte, loi.votes);
}

function afficherResultats(carte, votes) {
  const total = votes.pour + votes.contre + votes.abstention;
  const part = total === 0 ? 0 : Math.round((votes.pour / total) * 100);
  carte.querySelector('.remplissage').style.width = `${part}%`;
  carte.querySelector('.detail').textContent =
    `${total} vote(s) — 👍 ${votes.pour} pour (${part} %) · 👎 ${votes.contre} contre · 🤍 ${votes.abstention} abstention`;
}

chargerLois();
