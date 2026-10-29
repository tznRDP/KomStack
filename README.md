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
    ├── Shows.yml              # TV overlays, status labels, network and studio logos, episode badges
    ├── Movies.yml             # movie overlays, Recently Added, studio logos, Oscars badges
    ├── Test.yml               # TVTestBench overlays
    ├── Awards/
    │   └── Oscars/
    │       ├── build.py       # makes BestPicture/ from Source/
    │       ├── Source/        # the badge's parts, taken from Best Picture posters
    │       └── BestPicture/   # <year>_Gold.png and <year>_Dark.png, 1929 to 2035
    ├── Episodes/              # premiere and finale badges, 1920x1080
    ├── Networks/
    │   ├── build.py           # makes Label/ and Tinted/ from Source/
    │   └── <Network>/
    │       ├── Source/        # the original logo, <Name>.svg or .png (+ _Color)
    │       ├── Label/         # <Name>_White.png, _Black.png, _Color.png, _ColorDark.png
    │       └── Tinted/        # <Name>_<show>.png, one show's logo in its own colour
    ├── Status/
    │   ├── build.py           # makes 100/, 115/ and 130/
    │   ├── Source/            # the Montserrat font and its licence
    │   └── 100/ 115/ 130/     # <Name>.png, the status labels in three sizes
    └── Studios/
        ├── build.py           # makes Label/ from Source/
        └── <Studio>/
            ├── Source/        # the original logo or its parts, .svg or .png
            └── Label/         # <Name>_White.png and <Name>_Black.png
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

Shows get a logo in the top-left corner from Plex's network field (`Overlays/Shows.yml`). Movies get a studio logo at the bottom instead, and Marvel and DC shows get one as well (see Studio logos). BBC Earth isn't a network in Plex, so its line lists the BBC Earth shows by TVDB id; add a new one's id there. Any network line can add or leave out single shows with `add_titles` and `skip_titles`, or add them by TVDB id with `tvdb`.

Plex lists anime under the Japanese channel that first aired them (MBS, Nippon TV, Fuji TV and so on), so those channels are on Crunchyroll's line. A show that streams somewhere else is added by title or TVDB id to that network's line, which weighs more: Neon Genesis Evangelion, Ranma1/2 and Monster on Netflix's, The Ghost in the Shell and the Korean drama A Love Other Than Yours on Prime Video's. Sky's channels are on SkyShowtime's line, since that's where Sky's shows stream in Sweden.

Label a show `Dark` in Plex to get the black logo, for light posters, or `Color` for the colour logo. Color works on Comedy Central, Crunchyroll, Freeform, fubo, Hulu, NBC, Paramount+, Peacock, Prime Video, Quibi, Rakuten TV, The CW, TVING, Viaplay and Youku; on other networks the show keeps its plain logo. Both labels together give the colour logo with black text on Comedy Central, NBC, Peacock and Prime Video, and the colour logo on the rest.

A single show can have its logo in its own colour, usually its poster's title colour: a `Tinted/<Name>_<show>.png` in the network's folder and one line in the TINTED section with the show's TVDB id. Most are one colour, like Peacemaker's yellow HBO Max logo. Some copy the title's look as well: an orange-to-yellow gradient for Why Didn't They Ask Evans?, brushed gold for Shōgun, bevelled copper for House of the Dragon, cracks for Full Circle, worn chalk for Grotesquerie and a green element tile for Breaking Bad. Crystal Lake's Peacock logo keeps its coloured dots.

The images are 1000x1500 with the logo's top-left corner at 43,43, sized like the network logos on MediUX posters: HBO is 108x45, hulu 99x33, prime video 172x53, STARZ 130x30 and square logos like abc 58x58. `Overlays/Networks/build.py` makes every one of them from the original in the network's `Source/` folder (an svg where there is one, otherwise a png bigger than the logo is drawn), so nothing is ever scaled up. A new network is a line in the `LOGOS` table and a new tint a line in `TINTS` (the effects are listed above it), then `python3 build.py` (needs Pillow, numpy and cairosvg) and the matching lines in `Overlays/Shows.yml`: a pair in NETWORKS plus one per colour version, or one in TINTED.

Kometa keeps its own copy of each overlay image and reuses it for up to 60 days, so after changing a logo or badge image, delete those copies on the server before the next run: `sudo rm /home/plxsrv/docker/appdata/kometa/config/overlays/*.png`.

## Studio logos

Movies get the studio's logo centred at the bottom, under the title, as on their posters (the STUDIOS section of `Overlays/Movies.yml`):

| Logo | Movies |
| --- | --- |
| MARVEL STUDIOS | the MCU: Marvel Studios' movies that are in an MCU Phase collection |
| MARVEL TELEVISION | Marvel Television's specials, by TMDb id |
| DC STUDIOS | the DCU: DC's movies that are in the DC Universe collection |
| DC roundel | every other DC movie |
| LUCASFILM | Star Wars: Lucasfilm's movies with Star Wars, Empire Strikes Back, Return of the Jedi or Mandalorian in the title |
| Disney · PIXAR | Pixar |
| Disney | Walt Disney Animation Studios, and its older names in the Animation genre |

Kometa finds the studios' movies on TMDb, which lists every company behind a movie, so a Spider-Man made with Columbia still gets MARVEL STUDIOS even though Plex only shows one studio. Marvel and DC shows get theirs too, in the STUDIOS section of `Overlays/Shows.yml`: MARVEL ANIMATION on Marvel's animated shows (the listed ones, plus any Marvel Studios show in the Animation genre) and MARVEL TELEVISION on all the others, from WandaVision and Daredevil: Born Again to the Netflix ones and Agents of S.H.I.E.L.D., then DC STUDIOS on the DCU and the DC roundel on every other DC show. Those lists are by TMDb id, from `themoviedb.org/tv/<id>`, so a new show is one more line.

Label a movie or show `Dark` in Plex for the black logo, for light posters; white parts inside a coloured shape stay white, like MARVEL in its red box. Label it `No Studio` if its poster already shows the logo. The status labels sit under the logo, so nothing covers it.

The images are 1000x1500, sized like the studio logos on MediUX posters: MARVEL STUDIOS is 161x36, MARVEL ANIMATION and MARVEL TELEVISION as high, DC STUDIOS 176 wide, the DC roundel 54, Disney · PIXAR 182 and LUCASFILM 102. The logo's middle is at 500,1418, on movies and shows alike. `Overlays/Studios/build.py` makes them from the studio's `Source/` folder (an svg where there is one, otherwise a png bigger than the logo is drawn), so nothing is ever scaled up. DC STUDIOS is put together from the roundel and the STUDIOS letters, and MARVEL ANIMATION and MARVEL TELEVISION from Marvel's red box and the words off the X-Men '97 and Daredevil: Born Again posters. A new studio is a line in its `LOGOS` table, then `python3 build.py` (needs Pillow, numpy and cairosvg) and a pair of lines in the STUDIOS section.

## Status labels

Shows get a label at the very bottom, under the studio logo: a coloured pill with AIRING (blue), RETURNING (green), NEW SEASON (red), ENDED (grey) or CANCELED (red). It's one label per show, so in the weeks after a new season comes in, NEW SEASON takes the place of the status. Movies get a red RECENTLY ADDED in their first week. The STATUS OVERLAYS section of `Overlays/Shows.yml` decides which show gets which, and the MOVIES section of `Overlays/Movies.yml` does Recently Added.

The labels come in three sizes, 100, 115 and 130 (percent). The `StatusLabel` template at the top of both overlay files has `size: 100`; change it to 115 or 130 in both to swap every label on the next Kometa run. `Overlays/Status/build.py` makes all three sets, `<size>/<Name>.png`, in Montserrat ExtraBold, which is in `Status/Source/` with its licence (needs Pillow). The pill's middle is at y 1472, halfway between the bottom of the tallest studio logo and the poster's edge.

## Episode badges

Title cards get a badge on premieres and finales: Series Premiere, Season Premiere, Mid-Season Finale, Season Finale and Series Finale. Bookends, a separate container, labels the episodes in Plex from TheTVDB or TMDb data, whichever the show's episode ordering in Plex uses, and the EPISODE OVERLAYS section of `Overlays/Shows.yml` puts the matching badge on each labelled episode. Specials and Beck get no labels.

## MCU phases

`Collections/Movies.yml` has a collection for each MCU phase, Phase One to Phase Six, with the movies in release order, Marvel's specials like Werewolf by Night included. They sit right after Marvel Cinematic Universe in the Collections tab. Movies are listed by TMDb id, so the ones still to come (Avengers: Doomsday, Avengers: Secret Wars) join by themselves once they're in the library. Phase Seven is one more entry like the others.

## DC universes

`Collections/Movies.yml` also has DC Universe, the DCU from Superman (2025) on, and DC Extended Universe, from Man of Steel to Aquaman and the Lost Kingdom, with the movies by TMDb id in release order and Kometa's default posters. Movies in DC Universe get the DC STUDIOS logo, so a new DCU movie only needs adding to that collection.

## Oscars badge

A Best Picture winner whose poster is one of your own can get the Oscars badge at the top, as on the Best Picture posters: the gold Academy triangle, the ceremony year and BEST PICTURE WINNER. Label the movie `Oscars` in Plex for the gold badge, or `Oscars Dark` for the darker gold on a light poster, exactly as written; the next Kometa run puts it on. Kometa finds the ceremony year itself, from IMDb's Oscars data. Without one of those labels a movie never gets the badge, so the Best Picture posters that already show it are left alone, and taking the label off takes the badge off again. A label on a movie that didn't win Best Picture does nothing. The OSCARS section of `Overlays/Movies.yml` has two lines for every ceremony, one per gold.

`Overlays/Awards/Oscars/build.py` makes the badges, `BestPicture/<year>_Gold.png` and `_Dark.png` for every year from 1929 to 2035, out of the parts in `Source/`: the triangle, the divider, BEST PICTURE / WINNER and the digits 0 to 9, all taken from the Best Picture posters. The divider always sits under the middle of the triangle, with the year to its left and the text to its right; years those posters show keep their exact digit spacing. `python3 build.py 2036` makes another year (needs Pillow and numpy).

## Adding a director

One line in the DIRECTORS section of `Collections/Movies.yml` with the name and the TMDb person id from `themoviedb.org/person/<id>`. The collection appears once you have 3 of their films.

## Credits

Artwork is custom-made or sourced from community sites such as [MediUX](https://mediux.pro), [ThePosterDB](https://theposterdb.com) and [Fanart.tv](https://fanart.tv). All credit to the original creators.
