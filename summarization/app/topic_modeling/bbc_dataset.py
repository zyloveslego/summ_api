import os
from summarization.app.definitions import BBC_NEWS_PATH
from summarization.app.keywords.textrank.tokenizer import Tokenizer
import random


class BBCDataset:
    def __init__(self, bbc_dataset_path=BBC_NEWS_PATH):
        self.tokenizer = Tokenizer.factory("english")
        self.news = self._load_news(bbc_dataset_path)
        random.shuffle(self.news)

    def _load_category(self, category_path, label):
        news = []
        counter = 0
        for news_file_name in os.listdir(category_path):
            if counter > 50:
                break
            with open(os.path.join(category_path, news_file_name)) as f:
                try:
                    _news = f.read().replace("\n", " ")
                    tokens = self.tokenizer.tokenize_by_word(_news, apply_token_filters=True)
                    news.append(([unit.token for unit in tokens], label))
                    counter += 1
                except UnicodeDecodeError:
                    continue
        return news

    def _load_news(self, bbc_dataset_path):
        business_news = self._load_category(os.path.join(bbc_dataset_path, "business/"), "business")
        entertainment_news = self._load_category(os.path.join(bbc_dataset_path, "entertainment/"), "entertainment")
        politics_news = self._load_category(os.path.join(bbc_dataset_path, "politics/"), "politics")
        sport_news = self._load_category(os.path.join(bbc_dataset_path, "sport/"), "sport")
        tech_news = self._load_category(os.path.join(bbc_dataset_path, "tech/"), "tech")

        res = []
        res.extend(business_news)
        res.extend(entertainment_news)
        res.extend(politics_news)
        res.extend(sport_news)
        res.extend(tech_news)
        return res

    def __getitem__(self, item):
        news, label = self.news[item]
        return news, label
