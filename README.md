# reddit-terminal-tickerI can absolutely give you a **download‑ready README.md**, Anthony — but I need to stay within my boundaries, so instead of generating an actual file attachment, I’ll give you a **perfectly formatted Markdown document** that you can save directly as `README.md` on your machine.

Here it is, clean and ready to drop into your repo.

---

```markdown
# 📰 Reddit Terminal Ticker
*A colourful, mouse‑driven, real‑time Reddit feed for your terminal.*

A fast, neon‑styled, curses‑powered Reddit ticker that streams posts from **r/all** (or any subreddits you choose), complete with:

- 🖱️ **Mouse support** — click to select, click again to open
- 🎨 **Neon colour‑coding per subreddit**
- 🧵 **Wrapped titles** (no truncation)
- 📉 **Fade‑out effect** for older posts
- 🌐 **Clickable links** (Enter or mouse)
- ⚡ **Async live updates**
- 🖥️ **Terminal‑safe UI** (no flicker, no overflow)

Built for people who want a *live wire* Reddit feed right in their terminal.

---

## ✨ Features

- **Live updates** from any subreddit (default: `r/all`)
- **Mouse‑click navigation**
- Click a post → select it
- Click again or double‑click → open in browser
- **Keyboard navigation**
- ↑ / ↓ to move
- Enter to open
- q to quit
- **Wrapped titles** so long posts display cleanly
- **Neon colour‑coding** per subreddit
- **Fade‑out** for older posts
- **Terminal‑safe rendering**
- **Async polling** for smooth updates

---

## 📦 Requirements

- Python 3.9+
- `aiohttp`
- A terminal that supports mouse events (most modern terminals do)

Install dependencies:

```bash
pip install aiohttp
```

---

## 🚀 Usage

Clone the repo:

```bash
git clone https://github.com/kurobeats/reddit-terminal-ticker
cd reddit-terminal-ticker
```

Create a `subreddits.txt` file:

```
40kLore
linux
Perth
SipsTea
```

Run the ticker:

```bash
python3 main.py
```

---

## 🖱️ Mouse Controls

- **Left‑click** a post → select it
- **Left‑click again** → open it
- **Double‑click** → open immediately

---

## ⌨️ Keyboard Controls

- **↑ / ↓** — move selection
- **Enter** — open selected post
- **q** — quit

---

## 🧠 How It Works

The ticker:

1. Polls Reddit’s JSON API asynchronously
2. Inserts new posts at the top
3. Wraps long titles across multiple lines
4. Maps screen rows → post indices for mouse clicks
5. Applies neon colours per subreddit
6. Fades older posts to dimmer colours
7. Opens links via your system browser

---

## 📁 File Structure

```
.
├── main.py # main program
├── subreddits.txt # list of subs to poll
└── README.md # this file
```
