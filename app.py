from flask import Flask, request, jsonify, render_template_string
import os
import requests as req

app = Flask(__name__)

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "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")

HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
  <title>Ask Anything</title>
  <link href="https://fonts.googleapis.com/css2?family=DM+Serif+Display:ital@0;1&family=DM+Mono:wght@400;500&display=swap" rel="stylesheet"/>
  <style>
    *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
    :root {
      --bg: #0e0e0e; --surface: #161616; --border: #2a2a2a;
      --accent: #c8ff00; --text: #f0f0f0; --muted: #666; --radius: 12px;
    }
    body {
      background: var(--bg); color: var(--text);
      font-family: 'DM Mono', monospace; min-height: 100vh;
      display: flex; flex-direction: column; align-items: center;
      padding: 60px 20px 40px;
    }
    header { text-align: center; margin-bottom: 48px; }
    header h1 {
      font-family: 'DM Serif Display', serif;
      font-size: clamp(2.2rem, 6vw, 4rem); font-style: italic;
      letter-spacing: -0.02em; line-height: 1; color: var(--text);
    }
    header h1 span { color: var(--accent); }
    header p { margin-top: 10px; color: var(--muted); font-size: 0.78rem; letter-spacing: 0.08em; text-transform: uppercase; }
    .card { width: 100%; max-width: 680px; background: var(--surface); border: 1px solid var(--border); border-radius: var(--radius); padding: 28px; }
    textarea {
      width: 100%; background: var(--bg); border: 1px solid var(--border);
      border-radius: 8px; color: var(--text); font-family: 'DM Mono', monospace;
      font-size: 0.9rem; padding: 14px 16px; resize: vertical; min-height: 100px;
      outline: none; transition: border-color 0.2s; line-height: 1.6;
    }
    textarea:focus { border-color: var(--accent); }
    textarea::placeholder { color: var(--muted); }
    .row { display: flex; align-items: center; justify-content: space-between; margin-top: 14px; gap: 12px; }
    .model-select {
      background: var(--bg); border: 1px solid var(--border); border-radius: 8px;
      color: var(--muted); font-family: 'DM Mono', monospace; font-size: 0.78rem;
      padding: 8px 12px; outline: none; cursor: pointer;
    }
    button {
      background: var(--accent); color: #000; border: none; border-radius: 8px;
      font-family: 'DM Mono', monospace; font-size: 0.82rem; font-weight: 500;
      letter-spacing: 0.05em; padding: 10px 24px; cursor: pointer;
      transition: opacity 0.15s, transform 0.1s; text-transform: uppercase;
    }
    button:hover { opacity: 0.85; } button:active { transform: scale(0.97); } button:disabled { opacity: 0.4; cursor: not-allowed; }
    .answer-box { margin-top: 24px; display: none; }
    .answer-box.visible { display: block; }
    .answer-label { font-size: 0.7rem; text-transform: uppercase; letter-spacing: 0.12em; color: var(--accent); margin-bottom: 10px; }
    .answer-text {
      background: var(--bg); border: 1px solid var(--border); border-radius: 8px;
      padding: 16px; font-size: 0.88rem; line-height: 1.75; white-space: pre-wrap;
      color: var(--text); min-height: 60px;
    }
    .error { color: #ff6b6b; }
    .spinner { display: inline-block; width: 14px; height: 14px; border: 2px solid #000; border-top-color: transparent; border-radius: 50%; animation: spin 0.6s linear infinite; vertical-align: middle; margin-right: 6px; }
    @keyframes spin { to { transform: rotate(360deg); } }
    footer { margin-top: 36px; color: var(--muted); font-size: 0.7rem; letter-spacing: 0.08em; text-transform: uppercase; }
  </style>
</head>
<body>
  <header>
    <h1>Ask <span>anything.</span></h1>
    <p>Natural language Q&amp;A · Powered by Groq</p>
  </header>
  <div class="card">
    <textarea id="question" placeholder="What would you like to know?"></textarea>
    <div class="row">
      <select class="model-select" id="model">
        <option value="llama-3.3-70b-versatile">llama-3.3-70b</option>
        <option value="llama-3.1-8b-instant">llama-3.1-8b (faster)</option>
        <option value="mixtral-8x7b-32768">mixtral-8x7b</option>
        <option value="gemma2-9b-it">gemma2-9b</option>
      </select>
      <button id="askBtn" onclick="ask()">Ask →</button>
    </div>
    <div class="answer-box" id="answerBox">
      <div class="answer-label">Answer</div>
      <div class="answer-text" id="answerText"></div>
    </div>
  </div>
  <footer>Flask · Groq · No data stored</footer>
  <script>
    async function ask() {
      const question = document.getElementById('question').value.trim();
      const model = document.getElementById('model').value;
      const btn = document.getElementById('askBtn');
      const box = document.getElementById('answerBox');
      const text = document.getElementById('answerText');
      if (!question) return;
      btn.disabled = true;
      btn.innerHTML = '<span class="spinner"></span>Thinking';
      box.classList.add('visible');
      text.className = 'answer-text';
      text.textContent = '';
      try {
        const res = await fetch('/ask', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ question, model })
        });
        const data = await res.json();
        if (data.error) { text.classList.add('error'); text.textContent = 'Error: ' + data.error; }
        else { text.textContent = data.answer; }
      } catch (e) {
        text.classList.add('error');
        text.textContent = 'Network error. Is the server running?';
      }
      btn.disabled = false;
      btn.textContent = 'Ask →';
    }
    document.getElementById('question').addEventListener('keydown', e => {
      if (e.key === 'Enter' && (e.metaKey || e.ctrlKey)) ask();
    });
  </script>
</body>
</html>
"""

@app.route("/")
def index():
    return render_template_string(HTML)

@app.route("/ask", methods=["POST"])
def ask():
    data = request.get_json()
    question = (data.get("question") or "").strip()
    model = data.get("model", "llama-3.3-70b-versatile")

    if not question:
        return jsonify({"error": "No question provided"}), 400

    try:
        response = req.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {GROQ_API_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "model": model,
                "messages": [
                    {"role": "system", "content": "You are a helpful assistant. Answer questions clearly and concisely."},
                    {"role": "user", "content": question}
                ],
                "max_tokens": 1024,
                "temperature": 0.7,
            },
            timeout=30,
        )

        if response.status_code != 200:
            try:
                err = response.json().get("error", {})
                msg = err.get("message", response.text)
            except Exception:
                msg = response.text
            return jsonify({"error": f"[{response.status_code}] {msg}"}), response.status_code

        answer = response.json()["choices"][0]["message"]["content"].strip()
        return jsonify({"answer": answer})

    except req.exceptions.Timeout:
        return jsonify({"error": "Request timed out. Try again."}), 504
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True, port=5000)