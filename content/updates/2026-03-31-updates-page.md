---
title: "Updates page added"
date: 2026-03-31
tags:
  - release
  - feature
  - markdown
summary: A new Updates section is now part of the site. Entries are written as Markdown files and appear automatically — no code changes required.
---

The site now has an Updates page. Each entry is a Markdown file stored in `content/updates/` with a small YAML frontmatter block at the top. Dropping a new file into that directory is all that is needed to publish a post.

## How it works

Posts carry a `title`, `date`, and optional `tags` and `summary` fields in their frontmatter. The feed displays them newest-first, and each entry links to a detail page that renders the full Markdown body.

## Finding things

The feed supports client-side search and tag filtering so entries can be found without leaving the page. Sort order can be flipped between newest-first and oldest-first.

## Writing a post

```markdown
---
title: My update
date: 2026-04-01
tags:
  - design
summary: One-line description for the feed.
---

Body content in standard Markdown goes here.
```

The filename (without `.md`) becomes the URL slug. Set `draft: true` to keep an entry off the public feed while still keeping the file in the repository.
