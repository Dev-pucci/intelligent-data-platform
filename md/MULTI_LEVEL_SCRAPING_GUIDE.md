# Multi-Level Scraping Guide

## Overview

The SPA Scraper now supports sophisticated multi-level scraping, allowing you to:
1. Scrape listing pages (search results, product lists, etc.)
2. Automatically visit detail pages for each item
3. Extract additional data from detail pages
4. Merge listing and detail data intelligently

---

## Key Improvements

### 1. **Automatic URL Field Detection**
No need to hardcode field names! The scraper automatically detects URL fields using:
- **Common field names**: `url`, `listing_url`, `product_url`, `video_url`, `article_url`, `link`, `href`, `detail_url`, `page_url`, `item_url`
- **Smart pattern matching**: Any field containing `url` or `link` in the name

### 2. **Flexible Configuration**
You can override auto-detection by specifying the URL field:

```yaml
detail_parser:
  url_field: "video_url"  # Explicitly specify which field contains the detail URL
  # ... rest of config
```

### 3. **Rate Limiting**
Built-in rate limiting for detail pages prevents overwhelming servers:

```yaml
detail_parser:
  rate_limit:
    delay: 2  # Seconds between detail page requests (default: 2)
  max_pages: 10  # Limit number of detail pages to scrape (default: all)
```

### 4. **Error Handling**
- Graceful failure: If one detail page fails, others continue
- Original data preserved: Items without detail data are kept
- Comprehensive logging: Track success/error counts

### 5. **Field Conflict Prevention**
Use prefixes to avoid field name conflicts:

```yaml
detail_parser:
  field_prefix: "detail_"  # Prefix all detail fields with "detail_"
  # Example: "description" becomes "detail_description"
```

### 6. **Relative URL Support**
Automatically converts relative URLs to absolute:

```yaml
detail_parser:
  base_url: "https://example.com"
  # /product/123 becomes https://example.com/product/123
```

---

## Configuration Examples

### Example 1: YouTube Videos (Complex)

```yaml
name: "YouTube Search"
type: spa
seed_url: "https://www.youtube.com/results?search_query=python"

# Main listing parser
parser_type: css
parser_config:
  container: "ytd-video-renderer"
  fields:
    title: "yt-formatted-string#video-title ::text"
    channel: "ytd-channel-name a ::text"
    video_url: "a#video-title ::attr(href)"
    views: "span.ytd-video-meta-block:nth-of-type(1) ::text"
    upload_date: "span.ytd-video-meta-block:nth-of-type(2) ::text"
    thumbnail: "img#img ::attr(src)"

# Detail page parser
detail_parser:
  url_field: "video_url"  # Explicitly specify (or auto-detect)
  base_url: "https://www.youtube.com"  # Convert relative URLs
  wait_for: "div#primary"
  scroll: true
  rate_limit:
    delay: 3  # 3 seconds between detail page scrapes
  max_pages: 5  # Only scrape first 5 videos
  field_prefix: "detail_"  # Prefix detail fields

  parser_type: css
  parser_config:
    container: "div#primary"
    fields:
      description: "yt-formatted-string#description ::text"
      likes: "yt-formatted-string#text[aria-label*='like'] ::attr(aria-label)"
      channel_subscribers: "yt-formatted-string#owner-sub-count ::text"
      category: "a.yt-chip-cloud-chip-renderer ::text"
      publish_date: "div#info-strings yt-formatted-string ::text"
      full_stats: "ytd-video-primary-info-renderer ::text"
```

**Result Structure:**
```json
{
  "title": "Python Tutorial for Beginners",
  "channel": "TechWithTim",
  "video_url": "https://www.youtube.com/watch?v=abc123",
  "views": "1.2M views",
  "upload_date": "2 months ago",
  "thumbnail": "https://i.ytimg.com/vi/abc123/hqdefault.jpg",
  "detail_description": "Full Python course for beginners...",
  "detail_likes": "45K likes",
  "detail_channel_subscribers": "1.5M subscribers",
  "detail_category": "Education",
  "detail_publish_date": "Oct 15, 2025"
}
```

---

### Example 2: E-Commerce (Jumia)

```yaml
name: "Jumia Products"
type: spa
seed_url: "https://www.jumia.co.ke/catalog/?q=phones"

parser_type: css
parser_config:
  container: "article.prd"
  fields:
    product_name: "h3.name ::text"
    product_url: "a.core ::attr(href)"
    price: "div.prc ::text"
    rating: "div.stars ::text"

detail_parser:
  # Auto-detect URL field (will find "product_url")
  base_url: "https://www.jumia.co.ke"
  wait_for: "div.-paxs"
  scroll: true
  rate_limit:
    delay: 2
  max_pages: 20  # Scrape up to 20 product details

  parser_type: css
  parser_config:
    container: "div.row.-pas"
    fields:
      full_description: "div.-pvs ::text"
      specifications: "ul.key-feat li ::text"
      seller_name: "a.-df ::text"
      seller_score: "div.stars ::text"
      warranty: "div.-df:contains('Warranty') ::text"
      stock_status: "p.-fs14 ::text"
```

---

### Example 3: Classifieds (Jiji)

```yaml
name: "Jiji Listings"
type: spa
seed_url: "https://jiji.co.ke/search?query=cars"

parser_type: css
parser_config:
  container: "div[data-testid='advert-list-item']"
  fields:
    title: "h2 ::text"
    listing_url: "a ::attr(href)"  # Auto-detected
    price: "p.price ::text"
    location: "p.location ::text"

detail_parser:
  base_url: "https://jiji.co.ke"
  wait_for: "div[data-testid='advert-details']"
  rate_limit:
    delay: 3  # Slower for classifieds
  max_pages: 30

  parser_type: css
  parser_config:
    container: "div.advert-content"
    fields:
      description: "div.description ::text"
      seller_name: "a.seller-link ::text"
      seller_verified: "span.verified-badge ::text"
      year: "div[data-testid='year'] ::text"
      mileage: "div[data-testid='mileage'] ::text"
      fuel_type: "div[data-testid='fuel-type'] ::text"
      transmission: "div[data-testid='transmission'] ::text"
      phone_number: "a.phone ::attr(href)"
```

---

## How It Works

### Flow Diagram

```
1. Scrape Listing Page
   ├─> Extract items (title, price, URL, etc.)
   └─> Get list of detail URLs

2. For Each Detail URL:
   ├─> Navigate to detail page
   ├─> Wait for content to load
   ├─> Extract detail data
   ├─> Merge with listing data
   └─> Apply rate limiting

3. Return Combined Data
   └─> Each item contains both listing + detail fields
```

### Code Flow

```python
# 1. Initial scraping (listing page)
items = scraper.scrape(url)
# Items: [
#   {"title": "Item 1", "url": "/item/1", "price": "$10"},
#   {"title": "Item 2", "url": "/item/2", "price": "$20"}
# ]

# 2. Auto-detect URL field
url_field = "url"  # Auto-detected or configured

# 3. Scrape detail pages
for item in items:
    detail_url = item[url_field]
    detail_data = scrape_detail_page(detail_url)
    item.update(detail_data)

# Final items: [
#   {
#     "title": "Item 1",
#     "url": "/item/1",
#     "price": "$10",
#     "description": "Full description...",
#     "specs": "Full specs...",
#     "reviews": 4.5
#   }
# ]
```

---

## Advanced Features

### 1. Conditional Detail Scraping

Only scrape details for specific items:

```yaml
detail_parser:
  # Only scrape if item has certain conditions
  condition_field: "price"
  condition_min: 1000  # Only scrape items with price > $1000
```

### 2. Multiple Detail Levels

Chain multiple levels of scraping:

```yaml
# Level 1: Listing
parser_config:
  container: ".item"
  fields:
    category_url: "a.category ::attr(href)"

# Level 2: Category detail
detail_parser:
  url_field: "category_url"
  parser_config:
    container: ".product"
    fields:
      product_url: "a ::attr(href)"

# Level 3: Product detail
# (Would require nested detail_parser support - future feature)
```

### 3. Parallel Detail Scraping (Future)

```yaml
detail_parser:
  parallel: true
  max_workers: 5  # Scrape 5 detail pages concurrently
```

---

## Performance Tips

### 1. Limit Detail Pages
Don't scrape all detail pages if you don't need to:

```yaml
detail_parser:
  max_pages: 10  # Only first 10 items
```

### 2. Adjust Rate Limiting
Balance speed vs. server politeness:

```yaml
detail_parser:
  rate_limit:
    delay: 1  # Fast: 1 second (use for tolerant sites)
    delay: 5  # Slow: 5 seconds (use for strict sites like Amazon)
```

### 3. Filter Before Detail Scraping
Extract only what you need from listing:

```yaml
parser_config:
  fields:
    product_url: "a ::attr(href)"
    # Only extract URL on listing page, get everything else from detail
```

---

## Error Handling

The scraper handles common issues:

### 1. Missing URLs
Items without URLs are skipped gracefully:
```
[WARNING] Item 5/20 has no URL in field 'product_url', skipping
```

### 2. Failed Detail Pages
Original listing data is preserved:
```
[ERROR] Error scraping detail page: Connection timeout
[INFO] Detail page scraping completed: 18 successful, 2 errors
```

### 3. Invalid Data
Parser returns empty dict if no data extracted:
```
[WARNING] No data extracted from detail page: https://example.com/item/123
```

---

## Monitoring & Logging

The scraper provides detailed progress tracking:

```
[INFO] Starting detail page scraping for 20 items using URL field: 'product_url'
[INFO] Scraping detail page 1/20: https://example.com/product/1
[INFO] Successfully scraped 8 fields from detail page
[INFO] Scraping detail page 2/20: https://example.com/product/2
...
[INFO] Detail page scraping completed: 18 successful, 2 errors
```

---

## Migration Guide

### Before (Hardcoded)
```python
for item in items:
    detail_url = item.get('video_url')  # Hardcoded field name
    if detail_url:
        detail_data = scrape(detail_url)
        item.update(detail_data)
```

### After (Auto-Detected)
Just add to your YAML config:

```yaml
detail_parser:
  wait_for: "div.content"
  parser_type: css
  parser_config:
    container: "div.main"
    fields:
      description: "div.desc ::text"
```

No code changes needed!

---

## Best Practices

### 1. Start Small
Test with `max_pages: 5` first:

```yaml
detail_parser:
  max_pages: 5  # Test with 5 items
  rate_limit:
    delay: 3  # Be polite during testing
```

### 2. Monitor Performance
Check logs for success rate:
```
[INFO] Detail page scraping completed: 95 successful, 5 errors
```
Aim for >90% success rate.

### 3. Use Appropriate Delays
- **E-commerce (Jumia, Kilimall):** 2-3 seconds
- **Classifieds (Jiji):** 3-4 seconds
- **Video platforms (YouTube):** 3-5 seconds
- **Strict sites (Amazon):** 5-8 seconds

### 4. Handle Relative URLs
Always set `base_url` if site uses relative URLs:

```yaml
detail_parser:
  base_url: "https://example.com"
```

### 5. Avoid Field Conflicts
Use prefixes for detail fields:

```yaml
detail_parser:
  field_prefix: "detail_"
```

---

## Troubleshooting

### Issue: "Could not determine URL field"
**Solution:** Explicitly set `url_field`:

```yaml
detail_parser:
  url_field: "your_url_field_name"
```

### Issue: "Relative URL found but no base_url configured"
**Solution:** Add `base_url`:

```yaml
detail_parser:
  base_url: "https://example.com"
```

### Issue: Too many errors
**Solution:** Increase delays and check selectors:

```yaml
detail_parser:
  rate_limit:
    delay: 5  # Slower
  wait_for: "correct.selector"  # Verify selector works
```

---

## Summary

The improved multi-level scraping system provides:

✅ **Automatic URL detection** - No hardcoding
✅ **Flexible configuration** - Override any default
✅ **Built-in rate limiting** - Respect servers
✅ **Error resilience** - Continue on failures
✅ **Field prefixing** - Avoid conflicts
✅ **Relative URL handling** - Auto-conversion
✅ **Progress tracking** - Monitor performance
✅ **Production-ready** - Used in Jumia, Jiji, YouTube configs

**Ready for complex, multi-level data extraction at scale!** 🚀

---

*Last Updated: October 26, 2025*
*Intelligent Data Acquisition Platform v1.0*
