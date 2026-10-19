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
│   ├── Shows.yml              # TV home rows and collections
│   ├── Movies.yml             # movie home rows, collections, directors
│   └── <Collection Name>/
│       ├── poster.png
│       └── background.png
└── Overlays/
    ├── Shows.yml              # TV overlays, network logos, episode badges
    ├── Movies.yml             # movie overlays
    ├── Test.yml               # TVTestBench overlays
    ├── Episodes/              # premiere and finale badges, 1920x1080
    └── Networks/
        ├── build.py           # makes Label/ and Tinted/ from Source/
        └── <Network>/
            ├── Source/        # the original logo, <Name>.svg or .png (+ _Color)
            ├── Label/         # <Name>_White.png, _Black.png, _Color.png, _ColorDark.png
            └── Tinted/        # <Name>_<show>.png, one show's logo in its own colour
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

## Adding a movie

1. Upload `poster.png` (and `background.png` if there is one) to `Kometa/Metadata/Movies/<Movie (Year)>/`.
2. Add an entry to `Metadata/Movies.yml`, keyed by TMDB id, with `url_poster` (and `url_background`) pointing at the file's raw URL. A space in the folder name becomes `%20`, as in Hope's entry: `.../Kometa/Metadata/Movies/Hope%20(2026)/poster.png`.

## Home rows

The HOME section at the top of each collections file builds Netflix-style rows on Plex Home: New Releases (by digital release date, or physical when there's no digital one), Trending, one genre row a day, Most Popular (from Tracearr) and Watch Again. Star Wars, Mission: Impossible and Harry Potter are Plex's own collections; Kometa only puts the posters on them. The rows need Plex Pass, and Most Popular needs a `tracearr:` block in config.yml.

`hub_priority` sets each row's place in Manage Recommendations, lowest first. Kometa only moves its own rows and always puts them above Plex's built-in ones (Recently Added, Seasonal), so the gaps in the numbering are where those would go. Row-only collections get a `ZZZ_` sort title, which puts them at the bottom of the Collections tab, since Plex can't hide a collection from it.

## Network logos

Shows get a logo in the top-left corner from Plex's network field (`Overlays/Shows.yml`). Movies don't get one. BBC Earth isn't a network in Plex, so its line lists the BBC Earth shows by TVDB id; add a new one's id there. Any network line can add or leave out single shows with `add_titles` and `skip_titles`.

Label a show `Dark` in Plex to get the black logo, for light posters, or `Color` for the colour logo. Color works on Crunchyroll, fubo, Hulu, Paramount+, Peacock, Prime Video, Rakuten TV and Viaplay; on other networks the show keeps its plain logo. Both labels together give the colour logo with black text on Prime Video and Peacock, and the colour logo on the rest.

A single show can have its logo in its own colour, usually its poster's title colour: a `Tinted/<Name>_<show>.png` in the network's folder and one line in the TINTED section. Most are one colour, like Peacemaker's yellow HBO Max logo. Some copy the title's look as well: an orange-to-yellow gradient for Why Didn't They Ask Evans?, brushed gold for Shōgun, bevelled copper for House of the Dragon, cracks for Full Circle, worn chalk for Grotesquerie and a green element tile for Breaking Bad. Crystal Lake's Peacock logo keeps its coloured dots.

The images are 1000x1500 with the logo's top-left corner at 43,43, sized like the network logos on MediUX posters: HBO is 108x45, hulu 99x33, prime video 172x53 and square logos 58x58. `Overlays/Networks/build.py` makes every one of them from the original in the network's `Source/` folder (an svg where there is one, otherwise a png bigger than the logo is drawn), so nothing is ever scaled up. A new network is a line in the `LOGOS` table and a new tint a line in `TINTS` (the effects are listed above it), then `python3 build.py` (needs Pillow, numpy and cairosvg) and the matching lines in `Overlays/Shows.yml`: a pair in NETWORKS plus one per colour version, or one in TINTED.

Kometa keeps its own copy of each overlay image and reuses it for up to 60 days, so after changing a logo or badge image, delete those copies on the server before the next run: `sudo rm /home/plxsrv/docker/appdata/kometa/config/overlays/*.png`.

## Episode badges

Title cards get a badge on premieres and finales: Series Premiere, Season Premiere, Mid-Season Finale, Season Finale and Series Finale. Bookends, a separate container, labels the episodes in Plex from TheTVDB or TMDb data, whichever the show's episode ordering in Plex uses, and the EPISODE OVERLAYS section of `Overlays/Shows.yml` puts the matching badge on each labelled episode. Specials and Beck get no labels.

## Adding a director

One line in the DIRECTORS section of `Collections/Movies.yml` with the name and the TMDb person id from `themoviedb.org/person/<id>`. The collection appears once you have 3 of their films.

## Credits

Artwork is custom-made or sourced from community sites such as [MediUX](https://mediux.pro), [ThePosterDB](https://theposterdb.com) and [Fanart.tv](https://fanart.tv). All credit to the original creators.
