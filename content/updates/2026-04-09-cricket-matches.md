---
title: "Cricket matches page added"
date: 2026-04-09
tags:
  - release
  - feature
  - api
summary: A new cricket match section is now part of the site. Cricket matches can be filtered by certain conditions and then a detailed summary of the match can be viewed.
---

The site now has a page for cricket match data. The data comes from the excellent cricsheet database, which has ball by ball data for a large number of matches. Currently around 22,000 matches are included over all formats, with matches regularly added.

## How it works

The data is stored as JSON documents in cosmosdb. A minimal .NET API is used to query the database and return data. Currently there are two endpoints `/browse` and `/matches/{id}`. Browse is used when searching for documents, with a query generated from user inputs, the resulting documents are displayed back to the user as a summary. The summary can be clicked through to provide the detailed scorecard for the match.

## Future developments

Further manipulation of the match data is possible, as ball by ball data is available this will allow charts such as Manhattans to be implemented. An automated process to pull data in from cricsheet, and LLM integration to provide natural language searchinfga and data summarisation would be valuable additions.
