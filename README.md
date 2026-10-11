# pyMLM (python Music Library Manager)
pyMLM is a small python music library management script. If you rip CDs, you mind find it a bit of a hassle to rename every folder. Technically you could use Picard or MP3 Tag, but it gets really difficult, if you want to conditionally rename folders, e.g. to differentiate between rips and downloads. This script lets you rename your album directories and indexes all folders to a chosen markdown file, and can even index all songs to a csv.

Example:
```md
# Music Library Index

## Darkthrone
- [1992] - A Blaze In The Northern Sky (Studio) [FLAC] [DIGITAL]
- [2012] - Sempiternal Past The Darkthrone Demos [FLAC] [CD]
- [2022] - Astral Fortress [FLAC] [CD]
```

Generated indexes are written to `index/album_index.md` by default. Use `--output` to choose a different output file, for example `--output index/music_library.csv` for a CSV index.