# el_website_static
No.JS custom blog

I want to keep my website as simple as possible so that it is easy to maintain. That means no JS libraries. Hosted on Cloudflare Pages, which builds and deploys on every push to `main`.

Simple Python script contained in one file to build the website using Jinja from HTML files and markdown for the blog posts.

## Build locally

```
pip install -r requirements.txt
python main.py
```

The site is written to `build/`. To preview it with Pages routing (clean URLs, `404.html`): `npx wrangler pages dev build`.
