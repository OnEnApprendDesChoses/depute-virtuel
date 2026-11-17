const conteneur = document.getElementById('lois');
const template = document.getElementById('carte-loi');
let apiDisponible = true;

function votesLocaux(id) {
  try {
    return JSON.parse(localStorage.getItem(`votes-${id}`)) || { pour: 0, contre: 0, abstention: 0 };
  } catch (e) {
    return { pour: 0, contre: 0, abstention: 0 };
  }
}

function sauverVotesLocaux(id, votes) {
  localStorage.setItem(`votes-${id}`, JSON.stringify(votes));
}

function resumeLocal(loi) {
  return (
    `En deux mots : « ${loi.titre} ». ${loi.expose} ` +
    `Les points à retenir : ${loi.points_cles.join(' ; ')}.`
  );
}

async function chargerLois() {
  try {
    const res = await fetch('/api/lois');
    if (!res.ok) throw new Error('API indisponible');
    const lois = await res.json();
    conteneur.innerHTML = '';
    for (const loi of lois) {
      conteneur.appendChild(renduLoi(loi));
    }
  } catch (e) {
    apiDisponible = false;
    const res = await fetch('data/lois.json');
    const lois = await res.json();
    conteneur.innerHTML = '';
    for (const loi of lois) {
      conteneur.appendChild(renduLoi({ ...loi, votes: votesLocaux(loi.id) }));
    }
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
      if (apiDisponible) {
        try {
          await fetch(`/api/lois/${loi.id}/vote`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ choix })
          });
          await rafraichirResultats(carte, loi.id);
          return;
        } catch (e) {
          apiDisponible = false;
        }
      }
      const votes = votesLocaux(loi.id);
      votes[choix] += 1;
      sauverVotesLocaux(loi.id, votes);
      afficherResultats(carte, votes);
    });
  }

  carte.querySelector('.resume-ia').addEventListener('click', async () => {
    const bloc = carte.querySelector('.ia');
    bloc.hidden = false;
    bloc.textContent = 'L’IA réfléchit…';
    if (apiDisponible) {
      try {
        const res = await fetch(`/api/lois/${loi.id}/resume-ia`);
        if (res.ok) {
          const data = await res.json();
          bloc.textContent = data.resume;
          return;
        }
      } catch (e) {
        apiDisponible = false;
      }
    }
    bloc.textContent = resumeLocal(loi);
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
