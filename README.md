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
│   ├── Shows.yml              # TV home rows, collections, BBC Earth, Netflix label
│   ├── Movies.yml             # movie home rows, collections, directors
│   └── <Collection Name>/
│       ├── poster.png
│       └── background.png
└── Overlays/
    ├── Shows.yml              # TV overlays, network logos
    ├── Movies.yml             # movie overlays, streaming logos
    ├── Test.yml               # TVTestBench overlays
    └── Networks/
        └── <Network>/
            └── Label/         # <Name>_White.png, _Black.png, _Color.png
```

## Usage

`config.yml` loads every file with a `- url:` line pointing at `https://raw.githubusercontent.com/tznRDP/KomStack/main/Kometa/<file>`:

| Library | metadata_files | collection_files | overlay_files |
| --- | --- | --- | --- |
| Movies | `Metadata/Movies.yml` | `Collections/Movies.yml` | `Overlays/Movies.yml` |
| TV Shows | `Metadata/Shows.yml` | `Collections/Shows.yml` | `Overlays/Shows.yml` |
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

## Home rows

The HOME section at the top of each collections file builds Netflix-style rows on Plex Home: Top 10 on Plexflix (from Tracearr), New Releases, Trending, Watch It Again and one genre row a day. They need Plex Pass, and Top 10 needs a `tracearr:` block in config.yml. `hub_priority` sets the order, lowest first.

## Network logos

Shows get a logo in the top-left corner from Plex's network field (`Overlays/Shows.yml`). Movies from Netflix, Apple TV+ and Amazon get one from their TMDb companies (`Overlays/Movies.yml`). Netflix and BBC Earth shows use labels set by their collections instead, so single shows can be added or left out.

Label a show or movie `Dark` in Plex to get the black logo, for light posters.

To add a network: upload `<Name>_White.png` and `<Name>_Black.png` (1000x1500, logo top left) to `Overlays/Networks/<Network>/Label/`, then add a pair of lines to the NETWORKS section.

## Adding a director

One line in the DIRECTORS section of `Collections/Movies.yml` with the name and the TMDb person id from `themoviedb.org/person/<id>`. The collection appears once you have 3 of their films.

## Credits

Artwork is custom-made or sourced from community sites such as [MediUX](https://mediux.pro), [ThePosterDB](https://theposterdb.com) and [Fanart.tv](https://fanart.tv). All credit to the original creators.
