# recommender/templates.py
HTML_TEMPLATE = """
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width,initial-scale=1" />
  <title>Show Recommender</title>
  <style>
    body { font-family: system-ui, -apple-system, "Segoe UI", Roboto, Arial; margin: 2rem; color:#111; }
    textarea { width: 100%; height: 140px; font-size: 14px; padding: 8px; }
    input[type="submit"], button { padding: 8px 12px; font-size: 14px; }
    .card { border: 1px solid #ddd; padding: 12px; border-radius: 8px; margin-top: 1rem; background:#fff; }
    .error { color: #900; margin-top: 1rem; }
    .rec { margin-bottom: 0.75rem; }
    .spinner { display:inline-block; width:16px; height:16px; border:2px solid #ccc; border-top-color:#333; border-radius:50%; animation:spin 1s linear infinite; vertical-align: middle; margin-right:6px;}
    @keyframes spin { to { transform: rotate(360deg); } }
    footer { margin-top: 2rem; color:#666; font-size: 13px; }
  </style>
</head>
<body>
  <h1>AI Show Recommender</h1>
  <p>Enter shows you enjoy, one per line, then press Recommend to get suggestions with brief reasons.</p>

  <form id="likesForm" class="card" onsubmit="return onSubmit(event)">
    <label for="likes">Shows you like (one per line):</label><br/>
    <textarea id="likes" name="likes" placeholder="Breaking Bad&#10;The Wire&#10;Fleabag">{{ sample }}</textarea>
    <div style="margin-top:0.75rem;">
      <input type="submit" value="Recommend" />
      <button type="button" onclick="clearResults()">Clear</button>
      <span id="status" style="margin-left:1rem;"></span>
    </div>
  </form>

  <div id="results" style="margin-top:1rem;"></div>
  <div id="error" class="error" role="alert" aria-live="polite"></div>

  <footer>
    <small>Note: This demo calls an Ollama server configured by OLLAMA_URL. Configure environment variables before running.</small>
  </footer>

  <script>
    function setStatus(text, busy=false) {
      const s = document.getElementById('status');
      if (!text) { s.innerHTML = ''; return; }
      if (busy) {
        s.innerHTML = '<span class="spinner" aria-hidden="true"></span>' + text;
      } else {
        s.textContent = text;
      }
    }

    function clearResults() {
      document.getElementById('results').innerHTML = '';
      document.getElementById('error').textContent = '';
      setStatus('');
    }

    async function onSubmit(evt) {
      evt.preventDefault();
      clearResults();
      const textarea = document.getElementById('likes');
      const raw = textarea.value.trim();
      if (!raw) {
        document.getElementById('error').textContent = 'Please enter at least one show.';
        return false;
      }
      const likes = raw.split('\\n').map(s => s.trim()).filter(Boolean);
      setStatus('Requesting recommendations...', true);
      document.getElementById('error').textContent = '';
      try {
        const resp = await fetch('/recommend', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ likes })
        });
        setStatus('');
        if (!resp.ok) {
          const err = await resp.json().catch(() => ({}));
          document.getElementById('error').textContent = err.error || 'Server error';
          return false;
        }
        const data = await resp.json();
        renderResults(data.recommendations || []);
      } catch (e) {
        setStatus('');
        document.getElementById('error').textContent = 'Network error: ' + (e && e.message ? e.message : String(e));
        console.error(e);
      }
      return false;
    }

    function renderResults(items) {
      const container = document.getElementById('results');
      container.innerHTML = '';
      if (!items.length) {
        container.innerHTML = '<div class="card">No recommendations found.</div>';
        return;
      }
      const card = document.createElement('div');
      card.className = 'card';
      const title = document.createElement('h2');
      title.textContent = 'Recommendations';
      card.appendChild(title);
      items.forEach((it, idx) => {
        const p = document.createElement('div');
        p.className = 'rec';
        const strong = document.createElement('strong');
        strong.textContent = (idx + 1) + '. ' + it.title;
        p.appendChild(strong);
        const br = document.createElement('div');
        br.textContent = it.reason || '';
        br.style.marginLeft = '8px';
        p.appendChild(br);
        card.appendChild(p);
      });
      container.appendChild(card);
    }
  </script>
</body>
</html>
"""
