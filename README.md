# Novel-Scrapers

Supported Sites
- RoyalRoad
- SpaceBattles, SufficientVelocity, QuestionableQuesting (XenForo)
- FanFiction.net, FictionPress
- Archive Of Our Own
- Harry Potter Fanfic Archive
- Sink Into Your Eyes
- AdultFanfiction.org
- Worm, Ward


# Setup

```
uv venv novel_scrapers --python 3.11
uv pip install -e .
```

# Sample Usage

Downloading `Traveler` from Fanfiction.net
```
python -m novel_scrapers download --provider "fichub" --novel-name "Traveler" --novel-url "https://www.fanfiction.net/s/8466693/1/Traveler" --output-dir "/home/arelius/books/Traveler"
```

Credit:
- [RoyalRoad Support](https://github.com/sgprinc/RoyalRoadScraper)
- [Fanction.net and Rest is from Fichub.net](https://fichub.net/)

