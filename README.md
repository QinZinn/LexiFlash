# News-to-Anki CLI 🚀

A professional Python-based CLI tool designed to streamline language learning by automating the extraction of target vocabulary from news articles and generating ready-to-use Anki flashcards (.apkg).

![Anki Demo](assets/preview.png)

## 🌟 Key Features

- **Smart Scraping**: Built-in support for popular news outlets like **VnExpress (English)** and **BBC News**, with a robust generic fallback for other domains.
- **Advanced NLP**: Implements **Triple-Pass Lemmatization** (Verb, Noun, Adjective) to reduce redundancy and extract only the most meaningful base forms of words.
- **Offline Dictionary Enrichment**: Automatically fetches definitions and parts of speech using the **WordNet** database (via NLTK), ensuring fast and private lookups.
- **Modern Workflow**: Managed by `uv` for lightning-fast dependency management and consistent environments.
- **Customizable Blacklist**: Easily skip words you already know by adding them to `known_words.txt`.

## 🛠️ Installation

This project uses [uv](https://github.com/astral-sh/uv) for dependency management.

1. **Clone the repository**:
   ```bash
   git clone https://github.com/your-username/NewsToAnki.git
   cd NewsToAnki/Backend
   ```

2. **Sync dependencies**:
   ```bash
   uv sync
   ```

## 🚀 Usage

Run the tool from the `Backend/` directory using `uv run`.

### Basic Command
```bash
uv run main.py --url "https://e.vnexpress.net/news/news/education/vietnam-wins-four-gold-medals-at-international-chemistry-olympiad-4775486.html"
```

### Custom Output
```bash
uv run main.py --url "https://www.bbc.com/news/articles/c0jje79z7jno" --output "bbc_vocab.apkg"
```

### Arguments
- `--url`: (Required) The URL of the news article to process.
- `--output`: (Optional) The name of the output `.apkg` file (default: `English_News_Vocab.apkg`).

## 🧪 Testing

The project includes unit tests for the core processing logic. To run them:

```bash
uv run test_processor.py
```

## 📂 Project Structure

```text
NewsToAnki/
├── Backend/
│   ├── main.py              # CLI Entry Point
│   ├── test_processor.py    # Unit Tests
│   ├── known_words.txt      # Vocabulary Blacklist
│   ├── pyproject.toml       # uv Configuration
│   ├── uv.lock              # Lockfile
│   └── src/                 # Core Package
│       ├── __init__.py
│       ├── scraper.py       # News Scraping Logic
│       ├── processor.py     # NLP & Lemmatization
│       ├── dictionary_lookup.py # WordNet Integration
│       └── anki_generator.py    # .apkg Generation
├── assets/                  # Documentation Assets
└── README.md                # Project Documentation
```

## 📄 License
MIT License. See [LICENSE](LICENSE) for details.
