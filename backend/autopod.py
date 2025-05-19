import asyncio
from crawler import crawler
from summarizer import summarize_contents
import argparse
from voice import text_2_audio
from dotenv import load_dotenv


def main():
    parser = argparse.ArgumentParser(description="Crawl and chunk documents without saving to database")
    parser.add_argument("--url", help="URL to crawl (regular, .txt, or sitemap)")
    parser.add_argument("--chunk-size", type=int, default=1000, help="Max chunk size (chars)")
    parser.add_argument("--max-depth", type=int, default=3, help="Recursion depth for regular URLs")
    parser.add_argument("--max-concurrent", type=int, default=10, help="Max parallel browser sessions")
    args = parser.parse_args()
    args.url = "https://www.nytimes.com/sitemaps/new/news.xml.gz"

    print(f"Crawling {args.url}...")
    url_to_text = crawler(args)
    print(url_to_text)

    print("\n=== Generating Summaries ===")
    summaries = summarize_contents(url_to_text)

    # for url, summary in summaries.items():
    print(f"\n--- Summary for  ---\n{summaries}\n")
    text_2_audio(summaries)



if __name__ == "__main__":
    load_dotenv()
    main()