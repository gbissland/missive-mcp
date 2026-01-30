# Changelog

All notable changes to the Missive MCP Server.

## [1.2.0] - 2026-01-30

### Added
- **`calculate_team_metrics` tool**: Custom analytics for any team inbox
  - Calculates messages received/sent, first reply times
  - Breakdown by email channel (which address received/sent)
  - Configurable via `INTERNAL_DOMAINS` and `TRACKED_CHANNELS` env vars
  - Works regardless of Missive plan tier (uses conversation/message endpoints)
  - Supports historical data analysis with date range filtering
  - Rate-limit aware with built-in delays

## [1.1.0] - 2026-01-30

### Fixed
- **Analytics API format**: Fixed `create_analytics_report` to use correct Missive API format:
  - Changed wrapper from `{"analytics_reports": ...}` to `{"reports": ...}`
  - Changed date parameters from `start_date`/`end_date` strings to `start`/`end` Unix timestamps
  - Added `time_zone` parameter (defaults to `Pacific/Auckland`)
  - Renamed `mailbox_ids` to `account_ids` per API spec
  - Renamed `labels` to `shared_labels` per API spec

- **Analytics response parsing**: Fixed `get_analytics_report` to properly parse the `selected_period.global.totals` response structure from Missive API

### Changed
- **Analytics output formatting**: Improved `get_analytics_report` output with:
  - Clear sections for Messages, Response Times, and Distribution
  - Human-readable duration formatting (e.g., "4h 12m" instead of seconds)
  - First reply time distribution grouped into meaningful buckets
  - Period-over-period comparison with percentage changes
  - Better visual formatting with section dividers

### Notes
- Analytics filtering (by team, user, account, or label) requires Missive Business plan
- Org-wide analytics work on Productive plan

## [1.0.0] - 2026-01-30

### Added
- Initial fork from jordanlaubaugh9/missive-mcp
- Full suite of Missive API tools:
  - Conversation management (list, filter, details, messages, comments)
  - Task management (create, update)
  - Message operations (details, search, create)
  - Analytics reports (create, retrieve)
  - Drafts management (create, list, delete)
  - Posts/integration actions
  - Contacts management (CRUD, contact books, groups)
  - Organizations, Teams, and Shared Labels listing
