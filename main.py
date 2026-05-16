#!/usr/bin/env python3
import asyncio
import aiohttp
import curses
import json
import os
import warnings
import random
import webbrowser
import textwrap
from datetime import datetime

warnings.filterwarnings("ignore", category=DeprecationWarning)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SUB_FILE = os.path.join(BASE_DIR, "subreddits.txt")
SEEN_FILE = os.path.join(BASE_DIR, "seen.json")

# Load seen posts
if os.path.exists(SEEN_FILE):
    with open(SEEN_FILE, "r") as f:
        SEEN = set(json.load(f))
else:
    SEEN = set()

NEW_POSTS = set()
SUB_COLOURS = {}

def save_seen():
    with open(SEEN_FILE, "w") as f:
        json.dump(list(SEEN), f)

def load_subreddits():
    with open(SUB_FILE) as f:
        return [line.strip() for line in f if line.strip()]

async def fetch_subreddit(session, sub):
    url = f"https://www.reddit.com/r/{sub}/new.json?limit=20"
    headers = {"User-Agent": "TerminalTickerCurses/MouseWrap/1.0"}
    try:
        async with session.get(url, headers=headers, timeout=10) as r:
            data = await r.json()
    except Exception:
        return []

    posts = []
    for item in data.get("data", {}).get("children", []):
        post = item["data"]
        post_id = post["id"]

        if post_id not in SEEN:
            SEEN.add(post_id)
            NEW_POSTS.add(post_id)

            posts.append({
                "id": post_id,
                "sub": post.get("subreddit", "unknown"),
                "title": post.get("title", "").replace("\n", " "),
                "url": "https://reddit.com" + post.get("permalink", ""),
                "time": datetime.utcfromtimestamp(
                    post.get("created_utc", 0)
                ).strftime("%Y-%m-%d %H:%M UTC"),
            })
    return posts

async def poll_subreddits(subs, posts, interval=20):
    async with aiohttp.ClientSession() as session:
        while True:
            new_posts = []
            for sub in subs:
                new_posts.extend(await fetch_subreddit(session, sub))

            if new_posts:
                posts[0:0] = new_posts
                save_seen()

            await asyncio.sleep(interval)

def init_colors():
    curses.start_color()
    curses.use_default_colors()

    neon = [
        curses.COLOR_CYAN,
        curses.COLOR_MAGENTA,
        curses.COLOR_YELLOW,
        curses.COLOR_GREEN,
        curses.COLOR_RED,
        curses.COLOR_BLUE,
    ]

    for i, colour in enumerate(neon, start=1):
        curses.init_pair(i, colour, -1)

    curses.init_pair(20, curses.COLOR_CYAN, -1)
    curses.init_pair(21, curses.COLOR_WHITE, -1)
    curses.init_pair(30, curses.COLOR_MAGENTA, -1)

def get_sub_colour(sub):
    if sub not in SUB_COLOURS:
        SUB_COLOURS[sub] = random.randint(1, 6)
    return SUB_COLOURS[sub]

def build_row_map(posts, offset, width, height):
    """
    Maps screen row -> post index, even with wrapped lines.
    """
    row_map = {}
    row = 1
    idx = offset

    while row < height and idx < len(posts):
        p = posts[idx]
        line = f"r/{p['sub']} | {p['time']} | {p['title']}"
        wrapped = textwrap.wrap(line, width=width)

        for _ in wrapped:
            if row >= height:
                break
            row_map[row] = idx
            row += 1

        idx += 1

    return row_map

def draw_screen(stdscr, posts, offset, selected):
    stdscr.erase()
    h, w = stdscr.getmaxyx()

    header = "Reddit Live Ticker (q=quit, ↑/↓ scroll, Enter=open, mouse=click)"
    stdscr.addnstr(0, 0, header, w - 1,
                   curses.color_pair(30) | curses.A_BOLD)

    row = 1
    idx = offset

    while row < h and idx < len(posts):
        p = posts[idx]

        # Fade-out by age
        if idx < 10:
            colour = curses.color_pair(3) | curses.A_BOLD
        elif idx < 30:
            colour = curses.color_pair(get_sub_colour(p["sub"])) | curses.A_BOLD
        elif idx < 80:
            colour = curses.color_pair(20)
        else:
            colour = curses.color_pair(21)

        line = f"r/{p['sub']} | {p['time']} | {p['title']}"
        wrapped = textwrap.wrap(line, width=w - 1)

        for wrap_line in wrapped:
            if row >= h:
                break

            if idx == selected:
                stdscr.addnstr(row, 0, wrap_line, w - 1,
                               colour | curses.A_REVERSE)
            else:
                stdscr.addnstr(row, 0, wrap_line, w - 1, colour)

            row += 1

        idx += 1

    stdscr.refresh()

async def ui_loop(stdscr, posts):
    curses.curs_set(0)
    stdscr.nodelay(True)
    init_colors()

    curses.mousemask(curses.ALL_MOUSE_EVENTS | curses.REPORT_MOUSE_POSITION)

    offset = 0
    selected = 0

    while True:
        h, w = stdscr.getmaxyx()

        # Keep selection in bounds
        if posts:
            selected = max(0, min(selected, len(posts) - 1))
        else:
            selected = 0

        # Adjust offset so selected stays visible
        visible_rows = h - 2
        if selected < offset:
            offset = selected
        elif selected >= offset + visible_rows:
            offset = selected - visible_rows + 1

        draw_screen(stdscr, posts, offset, selected)

        # Build row map for mouse clicks
        row_map = build_row_map(posts, offset, w - 1, h)

        try:
            key = stdscr.getch()
        except curses.error:
            key = -1

        if key == ord("q"):
            break

        elif key == curses.KEY_UP:
            selected = max(0, selected - 1)

        elif key == curses.KEY_DOWN:
            selected = min(len(posts) - 1, selected + 1)

        elif key == 10:  # Enter
            if posts:
                webbrowser.open(posts[selected]["url"])

        elif key == curses.KEY_MOUSE:
            try:
                _, mx, my, _, bstate = curses.getmouse()
            except curses.error:
                continue

            # Ignore header
            if my <= 0:
                continue

            if my in row_map:
                selected = row_map[my]

                # Click or double-click opens link
                if bstate & curses.BUTTON1_CLICKED or bstate & curses.BUTTON1_DOUBLE_CLICKED:
                    webbrowser.open(posts[selected]["url"])

        await asyncio.sleep(0.1)

def main_curses(stdscr):
    subs = load_subreddits()
    posts = []

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    poll_task = loop.create_task(poll_subreddits(subs, posts))
    ui_task = loop.create_task(ui_loop(stdscr, posts))

    try:
        loop.run_until_complete(asyncio.gather(poll_task, ui_task))
    except KeyboardInterrupt:
        pass
    finally:
        save_seen()
        for task in (poll_task, ui_task):
            task.cancel()
        loop.stop()
        loop.close()

if __name__ == "__main__":
    curses.wrapper(main_curses)
