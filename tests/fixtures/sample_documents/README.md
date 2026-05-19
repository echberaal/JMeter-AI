# Sample Documents for Testing

## Files

### `sample.txt`
A realistic e-commerce login + product search + logout test scenario in plain text with markdown headings. Contains:
- 3 transactions (Login, Search, Logout)
- Multiple HTTP steps with methods, URLs, headers, and bodies
- Variables (CSV-sourced credentials, extracted product_id)
- Authentication via form login
- Think times specified

### `sample.pdf`
**Not included in the repository.** To test the PDF loader, generate a PDF from `sample.txt` using any tool (e.g., `pandoc sample.txt -o sample.pdf`). The unit tests for the PDF loader use a dynamically-generated fixture.

## Adding New Fixtures

When adding new fixture documents:
1. Keep them realistic but concise (under 50 lines preferred).
2. Include a variety of HTTP methods and data formats.
3. Add a description to this README.
