# utils/ai_assist.py

import os
import yaml
from dotenv import load_dotenv
from openai import OpenAI
from utils.logger import Logger

load_dotenv()

class AIAssistant:
    def __init__(self, config_path="config.yaml"):
        self.config = self._load_config(config_path)
        self.enabled = self.config.get("use_openai_fallback", False)
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.model = self.config.get("openai_model", "gpt-4")
        self.max_tokens = self.config.get("gpt_response_limit", 500)
        self.logger = Logger("global")

        if self.enabled and not self.api_key:
            raise ValueError("OpenAI fallback enabled but OPENAI_API_KEY not found.")

        self.client = OpenAI(api_key=self.api_key)

    def _load_config(self, path):
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                return yaml.safe_load(f)
        return {}

    def summarize_page(self, html, url):
        if not self.enabled:
            return "[OpenAI fallback disabled by config]"

        prompt = f"""
You are an expert AI web scraper. Analyze the following HTML content from {url}.
Return:
- What is the purpose of this page?
- What important data should be extracted?
- Recommend CSS selectors or data types for title, price, description, or main content.

HTML:
{html[:5000]}
"""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a precise and efficient web analysis assistant."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.4,
                max_tokens=self.max_tokens
            )
            return response.choices[0].message.content
        except Exception as e:
            self.logger.log_error("AI summary failed", str(e))
            return "[AI summary error]"

    def suggest_fix(self, error, html, url):
        if not self.enabled:
            return "[OpenAI fallback disabled by config]"

        prompt = f"""
You're debugging a failed web scrape from {url}. The error message was:
"{error}"

Here's the HTML snippet involved:
{html[:4000]}

Suggest a reason for the failure and a potential fix (e.g. wait condition, alt selector, new render step).
"""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You're an expert web scraping debugger."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.5,
                max_tokens=self.max_tokens
            )
            return response.choices[0].message.content
        except Exception as e:
            self.logger.log_error("AI suggestion failed", str(e))
            return "[AI suggestion error]"
