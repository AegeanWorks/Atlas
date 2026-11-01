# Manual-vs-live pipeline report

Manual = hand analysis by the AI from viewing the figures. Live = Muse Spark 1.3 on the same figures, same day.

## mito-frame-manual
- manual: E=8 R=8 cards=24 Q=23 overall=93.8
- live:   E=7 R=7 cards=21 Q=21 overall=100.0
- live scores: {'flashcards': 100, 'podcast': 100, 'infographic': 100, 'model3d': 100}
- manual issues: ['1 overlapping boxes hurt readability']
- live issues: ['none']

## methionine-cycle-manual
- manual: E=23 R=16 cards=62 Q=62 overall=93.8
- live:   E=24 R=20 cards=68 Q=68 overall=93.8
- live scores: {'flashcards': 100, 'podcast': 100, 'infographic': 75, 'model3d': 100}
- manual issues: ['14 overlapping boxes hurt readability']
- live issues: ['7 overlapping boxes hurt readability']

## petechial-rash-manual
- manual: E=16 R=14 cards=46 Q=46 overall=93.8
- live:   E=15 R=11 cards=41 Q=41 overall=93.8
- live scores: {'flashcards': 100, 'podcast': 100, 'infographic': 75, 'model3d': 100}
- manual issues: ['4 overlapping boxes hurt readability']
- live issues: ['1 overlapping boxes hurt readability']

## richest-babylon-book (whole-book live run, chunked)
E=245 R=225 across ~18 chunks merged by normalized name
quality overall=76.7 (flashcards 100, podcast 80, infographic 50: text-only, nothing to draw)
Turkish concepts preserved (Antik Babil, Milli zenginlik, Bireysel zenginlik ...)
timed Muse Spark key, env-only, never stored

## 0.17.0 re-score (dedup + trim-scope + capped pathways)
book: overall 83.3 (flashcards 100, podcast 100 with trim scope, infographic 50: 245 grid boxes overlap; honest)
video model: quality 91.7 pre-dedup; deck dedupes repeats, warning shown when zero boxes ground


## live methionine_cycle_live: overall=93.8 {'flashcards': 100, 'podcast': 100, 'infographic': 75, 'model3d': 100}
deck=68 questions=68

## live petechial_rash_live: overall=93.8 {'flashcards': 100, 'podcast': 100, 'infographic': 75, 'model3d': 100}
deck=41 questions=41

## live video retry (grounding retry on): 32/32 entities grounded, no warning, quality 91.7
first pass boxless as before; explicit retry grounds all 4 frames; merge preserves boxes (0.16.0 fix verified live)
