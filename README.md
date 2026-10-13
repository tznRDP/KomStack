# KomStack

Artwork, overlays and metadata files for a [Kometa](https://kometa.wiki/) setup, served via raw GitHub URLs.

## Structure

```
Kometa/
├── templates.yml              # shared art templates
├── Metadata/
│   ├── Shows.yml              # all shows, keyed by TVDB id
│   ├── Movies.yml             # all movies, keyed by TMDB id
│   ├── Shows/
│   │   └── <Show (Year)>/
│   │       ├── poster.png
│   │       ├── Season01.png
│   │       ├── Season01_background.png
│   │       ├── S01E01.png
│   │       └── ...
│   └── Movies/
│       └── <Movie (Year)>/
│           ├── poster.png
│           └── background.png
├── Collections/
│   ├── Shows.yml              # TV collections, network labels, network collections
│   ├── Movies.yml             # movie collections
│   ├── Studios.yml            # studio collections, both libraries
│   └── <Collection Name>/
│       ├── poster.png
│       └── background.png
└── Overlays/
    ├── Shows.yml              # TV overlays
    ├── Movies.yml             # movie overlays
    ├── Test.yml               # TVTestBench overlays
    └── Networks/
        └── <Network>/
            └── Label/         # <Name>_White.png, _Black.png, _Color.png
```

## Usage

`config.yml` loads every file with a `- url:` line pointing at `https://raw.githubusercontent.com/tznRDP/KomStack/main/Kometa/<file>`:

| Library | metadata_files | collection_files | overlay_files |
| --- | --- | --- | --- |
| Movies | `Metadata/Movies.yml` | `Collections/Movies.yml`, `Collections/Studios.yml` | `Overlays/Movies.yml` |
| TV Shows | `Metadata/Shows.yml` | `Collections/Shows.yml`, `Collections/Studios.yml` | `Overlays/Shows.yml` |
| TVTestBench | | | `Overlays/Test.yml` |

`Metadata/Shows.yml` pulls in `templates.yml` via `external_templates`. A show whose art is hosted here can call a template with its folder name:

```yaml
322191:  # The Terror (2018)
  template: {name: Seasons3, folder: "The Terror (2018)"}
```

The template builds every image URL from the folder name, URL-encoding it automatically. The number in the template name is the season count.

| Template | Sets |
| --- | --- |
| `Seasons1`–`Seasons5` | Season posters and backgrounds |
| `Art` | Show poster and background |
| `Art1`–`Art5` | Show art plus season art |

## File naming

Follows Kometa's asset-directory convention. Case-sensitive.

| File | Image |
| --- | --- |
| `poster.png` | Show, movie or collection poster |
| `background.png` | Show, movie or collection background |
| `Season##.png` | Season poster, zero-padded (`Season01.png`) |
| `Season##_background.png` | Season background |
| `S##E##.png` | Episode poster (`S01E01.png`) |
| `S##E##_background.png` | Episode background |

Files ending in `_alt` (or a colour, in collection folders) are unused alternates.

## Adding a show

1. Upload images to `Kometa/Metadata/Shows/<Show (Year)>/`.
2. Add an entry to `Metadata/Shows.yml`, keyed by TVDB id. One entry per show: if it already has one (a MediUX set, say), add the new art to that entry.
3. More than five seasons: copy the `Seasons5` block in `templates.yml` to `Seasons6` and add a season.

## Credits

Artwork is custom-made or sourced from community sites such as [MediUX](https://mediux.pro), [ThePosterDB](https://theposterdb.com) and [Fanart.tv](https://fanart.tv). All credit to the original creators.
