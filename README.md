# KomStack

Artwork, overlays and metadata files for a [Kometa](https://kometa.wiki/) setup, served via raw GitHub URLs.

## Structure

```
Kometa/
├── templates.yml              # shared art templates
├── Metadata/
│   ├── Shows.yml              # all shows, keyed by TVDB id
│   └── Shows/
│       └── <Show (Year)>/
│           ├── Season01.png
│           ├── Season01_background.png
│           └── ...
└── Overlays/
    └── Networks/
        └── <Network>/         # network overlay assets
```

## Usage

Kometa's `config.yml` loads `Shows.yml` remotely:

```yaml
libraries:
  TV Shows:
    metadata_files:
      - url: https://raw.githubusercontent.com/tznRDP/KomStack/main/Kometa/Metadata/Shows.yml
```

`Shows.yml` pulls in `templates.yml` via `external_templates`. Each show is keyed by its TVDB id and calls a template with its folder name:

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
| `poster.png` | Show poster |
| `background.png` | Show background |
| `Season##.png` | Season poster, zero-padded (`Season01.png`) |
| `Season##_background.png` | Season background |

## Adding a show

1. Upload images to `Kometa/Metadata/Shows/<Show (Year)>/`.
2. Add a two-line entry to `Shows.yml`: TVDB id, template, folder.
3. More than five seasons: copy the `Seasons5` block in `templates.yml` to `Seasons6` and add a season.

## Credits

Artwork is custom-made or sourced from community sites such as [MediUX](https://mediux.pro), [ThePosterDB](https://theposterdb.com) and [Fanart.tv](https://fanart.tv). All credit to the original creators.
