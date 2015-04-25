# Wikisum

This project defines an HTTP server that accepts requests for Wikipedia pages
by ID (e.g., <http://localhost:5000/page/16815>), and returns HTML tables
summarizing the identified pages.  When run in *test mode* (via the `-t` flag),
the server returns only canned data.
