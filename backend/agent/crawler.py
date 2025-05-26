# import os
# import psutil
# from crawl4ai import (
#     AsyncWebCrawler,
#     BrowserConfig,
#     CrawlerRunConfig,
#     CacheMode,
#     MemoryAdaptiveDispatcher
# )
# from typing import List, Dict

# async def crawl_parallel(urls: List[str], max_concurrent: int = 10) -> Dict[str, str]:
#     print("\n=== Parallel Crawling with craw4ai ===")

#     peak_memory = 0
#     process = psutil.Process(os.getpid())

#     def log_memory(prefix: str = ""):
#         nonlocal peak_memory
#         current_mem = process.memory_info().rss
#         if current_mem > peak_memory:
#             peak_memory = current_mem
#         print(f"{prefix} Current Memory: {current_mem // (1024 * 1024)} MB, Peak: {peak_memory // (1024 * 1024)} MB")

#     browser_config = BrowserConfig(
#         headless=True,
#         verbose=False,
#         extra_args=["--disable-gpu", "--disable-dev-shm-usage", "--no-sandbox"],
#     )
#     crawl_config = CrawlerRunConfig(cache_mode=CacheMode.BYPASS, stream=False)
#     dispatcher = MemoryAdaptiveDispatcher(
#         memory_threshold_percent=70.0,
#         check_interval=1.0,
#         max_session_permit=max_concurrent
#     )

#     url_to_text = {}

#     async with AsyncWebCrawler(config=browser_config) as crawler:
#         log_memory("Before crawl: ")

#         results = await crawler.arun_many(
#             urls=urls,
#             config=crawl_config,
#             dispatcher=dispatcher
#         )
        

#         for result in results:
#             if result.success:
#                 print(result)
#                 url_to_text[result.url] = result
#             else:
#                 print(f"Error crawling {result.url}: {result.error_message}")

#         log_memory("After crawl: ")
#         print(f"\nSuccessfully crawled {len(url_to_text)} of {len(urls)} URLs.")
#         print(f"Peak memory usage (MB): {peak_memory // (1024 * 1024)}")

#     return url_to_text

import sys
import re
import asyncio
from typing import List, Dict, Any
from urllib.parse import urlparse, urldefrag
from xml.etree import ElementTree
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, CacheMode, MemoryAdaptiveDispatcher
import argparse
import requests
import re
from datetime import datetime, timedelta


def filter_recent_article_sitemaps(sitemaps: List[str], days: int = 1) -> List[str]:
    today = datetime.utcnow()
    cutoff = today - timedelta(days=days)

    pattern = re.compile(r'article-(\d{4})-(\d{2})-(\d{2})\.xml')

    recent = []
    for url in sitemaps:
        match = pattern.search(url)
        if match:
            year, month, day = map(int, match.groups())
            sitemap_date = datetime(year, month, day)
            if sitemap_date >= cutoff:
                recent.append(url)

    return recent

def smart_chunk_markdown(markdown: str, max_len: int = 10000) -> List[str]:
    """Hierarchically splits markdown by #, ##, ### headers, then by characters, to ensure all chunks < max_len."""
    def split_by_header(md, header_pattern):
        indices = [m.start() for m in re.finditer(header_pattern, md, re.MULTILINE)]
        indices.append(len(md))
        return [md[indices[i]:indices[i+1]].strip() for i in range(len(indices)-1) if md[indices[i]:indices[i+1]].strip()]

    chunks = []

    for h1 in split_by_header(markdown, r'^# .+$'):
        if len(h1) > max_len:
            for h2 in split_by_header(h1, r'^## .+$'):
                if len(h2) > max_len:
                    for h3 in split_by_header(h2, r'^### .+$'):
                        if len(h3) > max_len:
                            for i in range(0, len(h3), max_len):
                                chunks.append(h3[i:i+max_len].strip())
                        else:
                            chunks.append(h3)
                else:
                    chunks.append(h2)
        else:
            chunks.append(h1)

    final_chunks = []

    for c in chunks:
        if len(c) > max_len:
            final_chunks.extend([c[i:i+max_len].strip() for i in range(0, len(c), max_len)])
        else:
            final_chunks.append(c)

    return [c for c in final_chunks if c]

def is_sitemap(url: str) -> bool:
    return url.endswith('sitemap.xml') or 'sitemap' in urlparse(url).path

def is_txt(url: str) -> bool:
    return url.endswith('.txt')

async def crawl_recursive_internal_links(start_urls, max_depth=3, max_concurrent=10) -> List[Dict[str,Any]]:
    """Recursive crawl using logic from 5-crawl_recursive_internal_links.py. Returns list of dicts with url and markdown."""
    browser_config = BrowserConfig(headless=True, verbose=False)
    run_config = CrawlerRunConfig(cache_mode=CacheMode.BYPASS, stream=False)
    dispatcher = MemoryAdaptiveDispatcher(
        memory_threshold_percent=70.0,
        check_interval=1.0,
        max_session_permit=max_concurrent
    )

    visited = set()

    def normalize_url(url):
        return urldefrag(url)[0]

    current_urls = set([normalize_url(u) for u in start_urls])
    results_all = []

    async with AsyncWebCrawler(config=browser_config) as crawler:
        for depth in range(max_depth):
            urls_to_crawl = [normalize_url(url) for url in current_urls if normalize_url(url) not in visited]
            if not urls_to_crawl:
                break

            results = await crawler.arun_many(urls=urls_to_crawl, config=run_config, dispatcher=dispatcher)
            next_level_urls = set()

            for result in results:
                norm_url = normalize_url(result.url)
                visited.add(norm_url)

                if result.success and result.markdown:
                    results_all.append({'url': result.url, 'markdown': result.markdown})
                    for link in result.links.get("internal", []):
                        next_url = normalize_url(link["href"])
                        if next_url not in visited:
                            next_level_urls.add(next_url)

            current_urls = next_level_urls

    return results_all

async def crawl_markdown_file(url: str) -> List[Dict[str,Any]]:
    """Crawl a .txt or markdown file using logic from 4-crawl_and_chunk_markdown.py."""
    browser_config = BrowserConfig(headless=True)
    crawl_config = CrawlerRunConfig()

    async with AsyncWebCrawler(config=browser_config) as crawler:
        result = await crawler.arun(url=url, config=crawl_config)
        if result.success and result.markdown:
            return [{'url': url, 'markdown': result.markdown}]
        else:
            print(f"Failed to crawl {url}: {result.error_message}")
            return []


# def parse_sitemap(sitemap_url: str) -> List[str]:
#     resp = requests.get(sitemap_url)
#     urls = []

#     if resp.status_code == 200:
#         try:
#             tree = ElementTree.fromstring(resp.content)
#             urls = [loc.text for loc in tree.findall('.//{*}loc')][:1]  # Limit to first 50 URLs
#         except Exception as e:
#             print(f"Error parsing sitemap XML: {e}")
#     print(urls)
#     return urls

def parse_sitemap(sitemap_url: str) -> List[str]:
    resp = requests.get(sitemap_url)
    urls = []

    if resp.status_code == 200:
        try:
            tree = ElementTree.fromstring(resp.content)
            all_urls = [loc.text for loc in tree.findall('.//{*}loc')]
            # Filter out image URLs
            image_extensions = ('.jpg', '.jpeg', '.png', '.gif', '.svg', '.webp', '.bmp', '.tiff')
            urls = [url for url in all_urls if not any(ext in url.lower() for ext in image_extensions)][:25]
        except Exception as e:
            print(f"Error parsing sitemap XML: {e}")
    print(urls)
    return urls

# def parse_sitemap(sitemap_url: str, days: int = 1) -> List[str]:
#     """
#     Parses a CNN sitemap or sitemap index, returning only the article URLs from the last `days`.
#     """
#     urls = []
#     try:
#         resp = requests.get(sitemap_url)
#         if resp.status_code != 200:
#             print(f"Failed to fetch sitemap: {sitemap_url}")
#             return urls

#         tree = ElementTree.fromstring(resp.content)
#         loc_elements = tree.findall('.//{*}loc')
#         loc_urls = [loc.text for loc in loc_elements if loc is not None]

#         # Detect if this is a sitemap index (contains article sitemaps)
#         is_index = any('sitemap' in url and url.endswith('.xml') for url in loc_urls)

#         if is_index:
#             # Filter to recent article sitemaps
#             cutoff_date = datetime.utcnow() - timedelta(days=days)
#             article_sitemaps = []
#             for url in loc_urls:
#                 match = re.search(r'article-(\d{4})-(\d{2})-(\d{2})\.xml', url)
#                 if match:
#                     year, month, day = map(int, match.groups())
#                     sitemap_date = datetime(year, month, day)
#                     if sitemap_date >= cutoff_date:
#                         article_sitemaps.append(url)

#             # Recursively parse recent article sitemaps
#             for article_sitemap_url in article_sitemaps:
#                 urls.extend(parse_sitemap(article_sitemap_url, days=days))

#         else:
#             # This is a direct article sitemap, return all article URLs
#             urls = loc_urls

#     except Exception as e:
#         print(f"Error parsing sitemap XML from {sitemap_url}: {e}")

#     return urls

async def crawl_batch(urls: List[str], max_concurrent: int = 10) -> List[Dict[str,Any]]:
    """Batch crawl using logic from 3-crawl_sitemap_in_parallel.py."""
    browser_config = BrowserConfig(headless=True, verbose=False)
    crawl_config = CrawlerRunConfig(cache_mode=CacheMode.BYPASS, stream=False)
    dispatcher = MemoryAdaptiveDispatcher(
        memory_threshold_percent=70.0,
        check_interval=1.0,
        max_session_permit=max_concurrent
    )

    async with AsyncWebCrawler(config=browser_config) as crawler:
        results = await crawler.arun_many(urls=urls, config=crawl_config, dispatcher=dispatcher)
        return [{'url': r.url, 'markdown': r.markdown} for r in results if r.success and r.markdown]

def extract_section_info(chunk: str) -> Dict[str, Any]:
    """Extracts headers and stats from a chunk."""
    headers = re.findall(r'^(#+)\s+(.+)$', chunk, re.MULTILINE)
    header_str = '; '.join([f'{h[0]} {h[1]}' for h in headers]) if headers else ''

    return {
        "headers": header_str,
        "char_count": len(chunk),
        "word_count": len(chunk.split())
    }

def crawler(args):
    

    # Detect URL type
    url = args.url
    if is_txt(url):
        print(f"Detected .txt/markdown file: {url}")
        crawl_results = asyncio.run(crawl_markdown_file(url))
    elif is_sitemap(url):
        print(f"Detected sitemap: {url}")
        sitemap_urls = parse_sitemap(url)
        if not sitemap_urls:
            print("No URLs found in sitemap.")
            sys.exit(1)
        crawl_results = asyncio.run(crawl_batch(sitemap_urls, max_concurrent=args.max_concurrent))
    else:
        print(f"Detected regular URL: {url}")
        crawl_results = asyncio.run(crawl_recursive_internal_links([url], max_depth=args.max_depth, max_concurrent=args.max_concurrent))

    # Chunk and collect metadata
    collected_chunks = []
    collected_metadata = []
    chunk_idx = 0

    for doc in crawl_results:
        url = doc['url']
        md = doc['markdown']
        chunks = smart_chunk_markdown(md, max_len=args.chunk_size)
        for chunk in chunks:
            collected_chunks.append(chunk)
            meta = extract_section_info(chunk)
            meta["chunk_index"] = chunk_idx
            meta["source"] = url
            collected_metadata.append(meta)
            chunk_idx += 1

    if not collected_chunks:
        print("No documents found.")
        sys.exit(1)

    print(f"Collected {len(collected_chunks)} chunks from '{args.url}'")

    # Optional: return or print chunks (adapt as needed)
    # for i, chunk in enumerate(collected_chunks):
    #     print(f"\n--- Chunk {i} ---\n{chunk}\n")

    # You can now return or use `collected_chunks` and `collected_metadata` as needed
    return ','.join(collected_chunks)#, collected_metadata

# if __name__ == "__main__":
#     parser = argparse.ArgumentParser(description="Crawl and chunk documents without saving to database")
#     parser.add_argument("--url", help="URL to crawl (regular, .txt, or sitemap)")
#     parser.add_argument("--chunk-size", type=int, default=1000, help="Max chunk size (chars)")
#     parser.add_argument("--max-depth", type=int, default=3, help="Recursion depth for regular URLs")
#     parser.add_argument("--max-concurrent", type=int, default=10, help="Max parallel browser sessions")
#     args = parser.parse_args()
#     args.url = "https://www.cnn.com/sitemap/news.xml"
#     chunks, metadata = crawler(args)
    
#     # Print to console
#     print(chunks)
    
#     # Save to a text file
#     with open("chunks_output.txt", "w", encoding="utf-8") as f:
#         for chunk in chunks:
#             f.write(f"{chunk}\n")

