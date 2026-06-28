# LexiFlash

LexiFlash is a Rust-first desktop vocabulary learning application built with Dioxus. It helps you turn articles and local documents into reviewable vocabulary decks, stores everything locally in SQLite, and schedules review sessions with FSRS.

The project’s core value proposition is simple:

- read real content instead of curated word lists
- extract vocabulary in context with a Rust-native NLP pipeline
- review due cards in a lightweight desktop app without a cloud dependency

Primary use cases:

- learners who want to build vocabulary from articles and study materials
- developers experimenting with a Rust desktop + NLP architecture
- contributors who want to work on a Dioxus desktop app backed by local SQLite storage

![LexiFlash preview](assets/preview.png)

## Overview

LexiFlash is the active successor to the old Python CLI branch.

- Current app: native desktop UI in `lexiflash_app/`
- Current NLP engine: Rust-native pipeline in `lexiflash_nlp/`
- Legacy branch: frozen at `v3.2.0`

If you need the historical Python CLI source, use the `v3.2.0` tag. Current development happens in the Rust desktop stack only.

## Features

### Core Features

- Desktop app built with Dioxus Desktop
- Vocabulary extraction from article URLs
- Vocabulary extraction from local `.txt`, `.docx`, `.pptx`, and `.pdf` files
- Rust-native NLP pipeline using `nlprule` and `wordnet-db`
- Local SQLite persistence for decks, vocabulary entries, and review state
- FSRS-based review scheduling with `Again`, `Hard`, `Good`, and `Easy` ratings
- Context-aware vocabulary entries with deduplication and first-occurrence retention

### Supplementary Features

- BBC- and VnExpress-aware scraping selectors, with generic article fallbacks
- Local file picker in the desktop UI
- Portable release packaging:
  - Windows: `LexiFlash-windows.zip`
  - Linux: `LexiFlash.AppImage`
- Smoke binaries for parser, scraper, NLP, and persistence verification
- Shared `known_words.txt` file for filtering already-known vocabulary

### Example Use Cases

- Read a BBC article, extract candidate words, and save them as a deck in SQLite
- Import lecture notes in `.docx` or slide decks in `.pptx` and build study cards from them
- Review all due cards from every deck in a single desktop review session
- Validate the NLP or persistence layer from the command line without launching the full UI

## Prerequisites

### Supported Runtime Modes

- End users:
  - Windows release artifact: `LexiFlash-windows.zip`
  - Linux release artifact: `LexiFlash.AppImage`
- Developers and contributors:
  - build from source using Cargo

### Software Requirements

- Rust toolchain: stable Rust with Cargo
- Git: required to clone the repository
- SQLite: bundled through `rusqlite`, no separate system SQLite setup required for app builds
- Python 3.12 or compatible Python 3.x: optional but recommended for downloading NLTK corpora locally with the same method used in CI

### Desktop Runtime Dependencies

- Windows:
  - Microsoft Edge WebView2 runtime available on the target machine
- Linux:
  - WebKitGTK desktop runtime/development packages required by Dioxus Desktop
  - GTK 3 development packages
  - `pkg-config`
  - a C/C++ build toolchain

Example packages:

- Debian/Ubuntu:

  ```bash
  sudo apt update
  sudo apt install -y build-essential pkg-config libgtk-3-dev libwebkit2gtk-4.1-dev
  ```

- Arch Linux:

  ```bash
  sudo pacman -S --needed base-devel pkgconf gtk3 webkit2gtk-4.1
  ```

### NLP Data Requirements

The Rust NLP crate expects:

- NLTK `wordnet.zip`
- NLTK English stopwords corpus file

It looks for them in this order:

- `WORDNET_ZIP_PATH` and `STOPWORDS_ENGLISH_PATH`
- `NLTK_DATA` for stopwords
- standard local/system `nltk_data` directories

The English `nlprule` tokenizer binary is downloaded automatically during the first `lexiflash_nlp` build by `build.rs`.

### Hardware Expectations

LexiFlash does not enforce a hard minimum hardware requirement in code, but the practical baseline is:

- 64-bit desktop or laptop system
- x86_64 architecture for the current release artifacts
- no dedicated GPU required
- enough disk space for:
  - Rust toolchains and build artifacts during development
  - local SQLite data
  - cached/extracted NLP data under the user cache directory

## Installation

### Option A: Install A Release Build

#### Windows

1. Download `LexiFlash-windows.zip` from the latest release.
2. Extract the archive to any directory.
3. Run `Launch-LexiFlash.bat`.

Verification:

- the extracted directory must contain:
  - `LexiFlash.exe`
  - `Launch-LexiFlash.bat`
  - `nlp-data/`

#### Linux

1. Download `LexiFlash.AppImage` from the latest release.
2. Make it executable:

   ```bash
   chmod +x LexiFlash.AppImage
   ```

3. Run it:

   ```bash
   ./LexiFlash.AppImage
   ```

Verification:

- the application window opens and shows the Dashboard

### Option B: Build From Source

#### 1. Clone The Repository

```bash
git clone https://github.com/QinZinn/LexiFlash.git
cd LexiFlash
```

#### 2. Install Rust

If you do not already have Rust:

```bash
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
source "$HOME/.cargo/env"
rustc --version
cargo --version
```

#### 3. Install Platform Dependencies

On Linux, install the packages shown in the prerequisites section above.

#### 4. Download NLTK Data

This is the same approach used by the Windows CI workflow:

```bash
python -m pip install --upgrade pip nltk
python -c "import nltk; nltk.download('wordnet', download_dir='$HOME/nltk_data'); nltk.download('stopwords', download_dir='$HOME/nltk_data')"
```

Verification:

```bash
test -f "$HOME/nltk_data/corpora/wordnet.zip"
test -f "$HOME/nltk_data/corpora/stopwords/english"
```

#### 5. Check Both Rust Crates

There is currently no root Cargo workspace manifest, so run checks per crate:

```bash
cargo check --manifest-path lexiflash_nlp/Cargo.toml
cargo check --manifest-path lexiflash_app/Cargo.toml
```

Verification:

- both commands exit successfully

#### 6. Run A Smoke Test

NLP smoke test:

```bash
cargo run --manifest-path lexiflash_app/Cargo.toml --bin nlp_smoke
```

Persistence smoke test using the sample article:

```bash
cargo run --manifest-path lexiflash_app/Cargo.toml --bin persist_deck_smoke -- file lexiflash_app/examples/sample_article.txt
```

Verification:

- `nlp_smoke` prints extracted `VocabularyEntry` values
- `persist_deck_smoke` prints a `DB_PATH`, `SAVED_DECK_ID`, and deck statistics

#### 7. Launch The Desktop App

```bash
cargo run --manifest-path lexiflash_app/Cargo.toml --bin lexiflash_app
```

Successful setup is confirmed when:

- the LexiFlash window opens
- the Dashboard renders without a blank screen
- the Create Deck screen can be opened from the top navigation

## Usage

### Launch The App

```bash
cargo run --manifest-path lexiflash_app/Cargo.toml --bin lexiflash_app
```

### Common User Workflows

#### 1. Create A Deck From A URL

1. Open `Create Deck`
2. Select `From URL`
3. Paste an article URL
4. Click `Extract from URL`
5. Review the preview
6. Let the app save the resulting deck to SQLite

Good candidates:

- BBC article pages
- VnExpress article pages
- other article-like pages with paragraph-based HTML structure

#### 2. Create A Deck From A Local File

Supported formats:

- `.txt`
- `.docx`
- `.pptx`
- `.pdf`

Workflow:

1. Open `Create Deck`
2. Select `From File`
3. Choose a supported document
4. Click `Extract from file`
5. Review the preview and save result

#### 3. Review Due Cards

1. Open the Dashboard
2. Click `Start session`
3. Flip the current card
4. Rate recall with:
   - `Again`
   - `Hard`
   - `Good`
   - `Easy`

The app updates `review_state` in SQLite using FSRS scheduling logic.

### Command-Line Workflows

#### Parse A Sample File And Run NLP

```bash
cargo run --manifest-path lexiflash_app/Cargo.toml --bin file_parse_smoke
```

Or pass an explicit file:

```bash
cargo run --manifest-path lexiflash_app/Cargo.toml --bin file_parse_smoke -- path/to/document.pdf
```

#### Scrape A Live Article

```bash
cargo run --manifest-path lexiflash_app/Cargo.toml --bin scrape_smoke
```

#### Run The NLP Pipeline Directly

```bash
cargo run --manifest-path lexiflash_app/Cargo.toml --bin nlp_smoke
```

#### Save A Deck Through The Persistence Smoke Binary

```bash
cargo run --manifest-path lexiflash_app/Cargo.toml --bin persist_deck_smoke -- file lexiflash_app/examples/sample_article.txt
```

### Rust API Example

`lexiflash_nlp` can also be used directly from Rust:

```rust
use lexiflash_nlp::LexiFlashNlp;

fn main() -> anyhow::Result<()> {
    let nlp = LexiFlashNlp::new()?;
    let sentences = vec![
        "Researchers are analyzing multilingual datasets for robust tagging.".to_string(),
        "A clever parser should ignore malformed tokens gracefully.".to_string(),
    ];

    let entries = nlp.process_article(&sentences);
    println!("{entries:#?}");
    Ok(())
}
```

### Configuration

#### Environment Variables

- `WORDNET_ZIP_PATH`
  - explicit path to NLTK `wordnet.zip`
- `STOPWORDS_ENGLISH_PATH`
  - explicit path to the NLTK English stopwords file
- `NLTK_DATA`
  - additional search root for NLTK corpora lookup
- `XDG_CACHE_HOME`
  - affects where extracted WordNet data is cached on Linux and other XDG-based environments

#### Known Words

LexiFlash reads `known_words.txt` from the repository root when building/running from source. Add one lowercase word per line to exclude already-known lemmas from extracted deck results.

#### Local Data Locations

The app stores data locally through the OS data directory via the `dirs` crate.

Examples:

- Linux:
  - `~/.local/share/lexiflash/lexiflash.db`
- Windows:
  - `%LOCALAPPDATA%\lexiflash\lexiflash.db`

No cloud synchronization is implemented in the current release.

## Technical Architecture

### High-Level Architecture

LexiFlash is split into two standalone Rust crates:

- `lexiflash_app`
  - Dioxus desktop UI
  - URL scraping and file parsing
  - SQLite persistence
  - FSRS scheduling
- `lexiflash_nlp`
  - tokenization, POS tagging, lemmatization, WordNet gating, stopword filtering, known-word filtering, and context extraction

### Key Technical Implementations

- UI renderer:
  - Dioxus Desktop `0.7.9`
- Desktop runtime:
  - WebView-based desktop rendering
- Persistence:
  - SQLite via `rusqlite` with bundled SQLite
- Review scheduler:
  - `fsrs`
- NLP:
  - `nlprule` for POS tagging and lemmatization
  - `wordnet-db` for WordNet lexname checks
- File parsing:
  - `office_oxide` for `.docx` and `.pptx`
  - `pdf_oxide` for `.pdf`
- HTTP scraping:
  - `reqwest` + `scraper`

### Database Schema

The local database centers on three tables:

- `decks`
  - deck metadata and source information
- `vocabulary_entries`
  - extracted lemma, context, original token, and WordNet POS
- `review_state`
  - per-card FSRS scheduling data such as `due_at`, `stability`, `difficulty`, `reps`, `lapses`, and `state`

### Repository Structure

```text
LexiFlash/
├── .github/workflows/
│   └── build-windows.yml        # Windows release packaging workflow
├── assets/
│   └── preview.png              # README and documentation preview asset
├── docs/adr/
│   └── 001-nlp-engine-rust-migration.md
├── known_words.txt              # Optional known-word filter input
├── lexiflash_app/
│   ├── examples/
│   │   └── sample_article.txt
│   ├── src/
│   │   ├── bin/                 # Smoke binaries
│   │   ├── components/          # Dashboard, Create Deck, Review Session
│   │   ├── article_content.rs
│   │   ├── db.rs
│   │   ├── file_parser.rs
│   │   ├── fsrs_scheduler.rs
│   │   ├── main.rs
│   │   ├── styles.rs
│   │   ├── text_utils.rs
│   │   └── url_scraper.rs
│   └── Cargo.toml
├── lexiflash_nlp/
│   ├── src/
│   │   ├── bin/
│   │   └── lib.rs
│   ├── tests/
│   │   └── compare_with_python.py
│   ├── build.rs                 # Downloads nlprule binaries at build time
│   └── Cargo.toml
├── LICENSE
└── README.md
```

### Design And Migration Notes

- The Python CLI branch is frozen at `v3.2.0`
- The Rust NLP migration decision is documented in [ADR 001](docs/adr/001-nlp-engine-rust-migration.md)
- The current desktop app is the production direction for LexiFlash

## Contributing

### Development Workflow

1. Fork the repository
2. Create a focused feature branch
3. Make changes in the relevant crate
4. Run formatting, checks, and any relevant smoke tests
5. Open a pull request with a clear scope and test summary

Recommended local checks:

```bash
cargo fmt --manifest-path lexiflash_nlp/Cargo.toml
cargo fmt --manifest-path lexiflash_app/Cargo.toml

cargo check --manifest-path lexiflash_nlp/Cargo.toml
cargo check --manifest-path lexiflash_app/Cargo.toml
```

If you touch functionality, also run the closest smoke binary or test that proves the change.

### Pull Request Guidelines

- Keep PRs focused and reviewable
- Explain user-visible impact
- List commands you ran locally
- Include screenshots or short recordings for UI changes
- Mention schema or packaging changes explicitly
- Avoid mixing unrelated refactors with bug fixes or feature work

### Coding Standards

- Use idiomatic Rust
- Prefer small, well-scoped modules
- Preserve existing naming and architectural boundaries unless a change is intentional and documented
- Keep user-facing error messages actionable
- Update README or ADRs when behavior, setup, or architecture changes materially

### Code Of Conduct

This repository does not currently ship a dedicated `CODE_OF_CONDUCT.md`.

Until one is added, contributors are expected to:

- communicate respectfully
- assume good intent
- keep review feedback specific and professional
- avoid harassment, discrimination, or abusive behavior

For platform-level expectations, follow the standard GitHub community conduct norms when participating in issues and pull requests.

## Troubleshooting

### `could not find wordnet.zip`

Cause:

- NLTK WordNet data is missing

Resolution:

```bash
python -m pip install --upgrade pip nltk
python -c "import nltk; nltk.download('wordnet', download_dir='$HOME/nltk_data')"
```

Or set:

```bash
export WORDNET_ZIP_PATH="$HOME/nltk_data/corpora/wordnet.zip"
```

### `could not find NLTK stopwords corpus file`

Cause:

- NLTK stopwords data is missing or not discoverable

Resolution:

```bash
python -c "import nltk; nltk.download('stopwords', download_dir='$HOME/nltk_data')"
export STOPWORDS_ENGLISH_PATH="$HOME/nltk_data/corpora/stopwords/english"
```

### Linux Build Fails With WebKitGTK Or GTK Linker Errors

Cause:

- missing native desktop dependencies required by Dioxus Desktop

Resolution:

- install the Linux packages listed in the prerequisites section
- confirm `pkg-config` is available
- rerun:

  ```bash
  cargo check --manifest-path lexiflash_app/Cargo.toml
  ```

### Windows App Does Not Start Correctly

Cause:

- WebView2 runtime may be missing on the target system

Resolution:

- install Microsoft Edge WebView2 runtime
- if using the release zip, make sure you launch the app through `Launch-LexiFlash.bat`

### First Build Is Slow

Cause:

- `lexiflash_nlp/build.rs` downloads `nlprule` binaries during the initial build

Resolution:

- allow the first build to complete with network access
- subsequent incremental builds should be much faster

### Extracted Vocabulary Looks Different From The Old Python CLI

Cause:

- the Rust app uses the new Rust-native NLP engine
- the legacy Python CLI and the new Rust pipeline are not expected to be output-identical

Resolution:

- compare behavior against the current Rust app, not the frozen Python CLI
- review [ADR 001](docs/adr/001-nlp-engine-rust-migration.md) for the accepted behavior drift

### Database Appears Empty

Cause:

- the Dashboard reflects real SQLite state and does not use mock data anymore

Resolution:

- create a deck from URL or file first
- verify the database path printed by:

  ```bash
  cargo run --manifest-path lexiflash_app/Cargo.toml --bin persist_deck_smoke -- file lexiflash_app/examples/sample_article.txt
  ```

## License

LexiFlash is distributed under the MIT License. See [LICENSE](LICENSE).

## Credits

- LexiFlash desktop app and repository: [QinZinn/LexiFlash](https://github.com/QinZinn/LexiFlash)
- UI framework: [Dioxus](https://dioxuslabs.com/)
- NLP stack:
  - `nlprule`
  - `wordnet-db`
- Review scheduling:
  - `fsrs`

## Maintainers And Contact

- Maintainer: [QinZinn](https://github.com/QinZinn)
- Issue tracker: [GitHub Issues](https://github.com/QinZinn/LexiFlash/issues)
- Pull requests: [GitHub Pull Requests](https://github.com/QinZinn/LexiFlash/pulls)

## Documentation Verification Notes

This README has been updated against the current repository state:

- crate names and paths match the codebase
- supported file formats match the parser implementation
- current release artifact names match the published release packaging
- usage examples are based on the existing smoke binaries and desktop entry points

The Markdown uses standard headings, lists, fenced code blocks, relative links, and image syntax so it renders cleanly on major Git hosting platforms that support GitHub-flavored Markdown.
