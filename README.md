# Auction Site Scraper

A robust web scraper designed to extract auction data from various auction websites. The scraper uses a self-healing selector system to adapt to different site structures and handle dynamic content.

## Features

- Automatic selector detection and validation
- Support for dynamic content loading
- Self-healing selector system
- Configurable per-site settings
- Robust error handling and logging
- Data format adaptation
- Pagination support
- Navigation extraction

## Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd auction-scraper
```

2. Create a virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Install Playwright browsers:
```bash
playwright install
```

## Usage

Run the scraper with a URL:
```bash
python3 launch.py example.com
```

The scraper will:
1. Load the page and wait for dynamic content
2. Extract auction items, navigation, and pagination
3. Save the data to `output/scrape_*.json`
4. Log operations to `logs/`

## Configuration

Site-specific configurations can be added in `config/sites/<domain>.yaml`. Example:

```yaml
enable_dynamic: true
wait_for_dynamic: true
dynamic_wait_time: 2
scroll: true
scroll_step: 500
scroll_delay: 0.1
custom_selectors:
  auction_items:
    - .lot-item
    - .auction-item
    - [data-lot-id]
```

## Project Structure

```
.
├── config/
│   └── sites/
├── logs/
├── output/
├── scraper/
│   ├── core.py
│   ├── extractor.py
│   ├── selector_manager.py
│   ├── selector_validator.py
│   ├── selector_generator.py
│   ├── selector_repair.py
│   └── schema_adapters.py
├── utils/
│   └── logger.py
├── launch.py
├── requirements.txt
└── README.md
```

## Error Handling

Errors are logged to:
- Console output
- `logs/<component>_<date>.log`
- `history/errors.json`

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

MIT License 