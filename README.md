[![make.fun · news-image-20261119](https://make.fun/badge/news-image-20261119.svg)](https://make.fun/bounty/news-image-20261119)
[![rank](https://make.fun/badge/news-image-20261119/Hamdansyahrin/day-in-one-image-20261119/rank.svg)](https://make.fun/bounty/news-image-20261119/leaderboard)
[![reward](https://make.fun/badge/news-image-20261119/Hamdansyahrin/day-in-one-image-20261119/reward.svg)](https://make.fun/bounty/news-image-20261119)

# The Day in One Page — Thursday 19 November 2026

A single illustrated newspaper front page that sums up 19 November 2026's
world news in one image: 45 stories, six continents, one page.

Entry for the make.fun bounty
[news-image-20261119](https://make.fun/bounty/news-image-20261119).

## Contents

- `entry.png` — the entry image: a 1024×1024 full-colour front page with
  3 illustrated lead stories (the Trump–Xi–Putin summit in Shenzhen, Iran's
  strikes on Gulf states after the US strike on Qeshm, and Anthropic's
  record $81bn IPO), 10 illustrated story cards, a "by the numbers" stat
  strip, a dotted world map with 13 numbered pins, and 32 one-line briefs.
- `render.py` — the deterministic renderer that produces `entry.png`
  (Python 3 + Pillow, build-time only, no network, no randomness; two
  runs are byte-identical).
- `main.py` — the contest entrypoint (standard library only): validates
  `entry.png` (PNG/JPEG magic, ≤ 1 MiB, ≤ 1024 px per side, strict PNG
  chunk-trailer check), copies it to `$MAKEFUN_OUTPUT_DIR/entry.png`,
  and verifies the copy by sha256 read-back.

## Run

```sh
python3 render.py   # regenerate entry.png
python3 main.py     # validate + copy to $MAKEFUN_OUTPUT_DIR/entry.png
```

## Licence

MIT — see `LICENSE`.
