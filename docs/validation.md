# Validation and provenance

This is the published portfolio repository. The preparation checks below describe
the original review package; publication does not imply a new database run.

## Sources and preserved evidence

- Aaron's ADS 507 Module 3 submission, dated January 26, 2026, supplied the
  business framing and relationship discussion. Its original PDF is excluded.
- Aaron's Module 4 notebook supplied the five SQL statements, six saved result
  tables (including table/view discovery), and the rating chart. Its matching
  submitted PDF is dated February 2, 2026. Original coursework stays outside
  this package and has not been edited.
- SQL text is preserved unchanged in both the prepared notebook and SQL file.
  Original result payloads are preserved, apart from removing warning streams,
  execution counters, and metadata. The chart's pixel-data chunks are retained;
  auxiliary PNG metadata was removed.

## Changes made for this review copy

- Replaced the original connection cell with environment variables and a
  private `getpass` fallback. No password is present in example settings.
- Replaced direct pandas/DBAPI calls with SQLAlchemy connections using PyMySQL.
  Removed unused NumPy imports and used context managers to close connections.
- Added readable headings, result provenance, query limitations, setup
  instructions, schema notes, and Oracle attribution.
- Cleared notebook execution counts and metadata. Excluded all original PDFs,
  course worksheets, database dumps, local account details, and runtime warnings.

## Checks performed during preparation

- Parsed notebook JSON; checked format 4.5 fields, unique cell IDs, allowed
  metadata and outputs; compiled each Python cell and the validation script.
- Compared all five queries byte-for-byte after trimming outer whitespace with
  their original coursework strings, and matched the standalone SQL file to the
  notebook. Checked that each is a single SELECT with no mutating SQL keywords.
- Reviewed query table/column references against the local Oracle Sakila schema.
  This is a static consistency check, not a MySQL parser or execution check.
- Compared all retained table payloads with the original saved outputs and
  checked the 1,000 / 958 / 42 film-count arithmetic against those outputs.
- Checked PNG integrity, removed auxiliary metadata, and visually reviewed the
  retained chart. Its embedded notebook image matches the standalone asset.
- Scanned every staged file for the original credential value and common
  token/private-key patterns, private filesystem paths, and email addresses.
  Reviewed remaining content for unrelated personal data.
- Verified relative documentation links, the package file list, and unchanged
  original source hashes. Checked ZIP contents and file hashes against this folder.

Run the repeatable offline checks from the repository root:

```sh
python3 scripts/validate_package.py
```

The original-credential comparison and original-source comparisons are separate
preparation checks. The public validator does not include credentials, private
source paths, or copies of original coursework. It ignores local Git metadata,
virtual environments, Python/notebook caches, `.DS_Store`, and private `.env` /
`*.local.env` configuration when checking the distributable file list. None of
those ignored artifacts is present in the prepared package or ZIP.

## What remains unverified

No notebook cells, SQL statements, or installation commands were executed during
preparation. No database was connected to or changed. The updated connection
code and dependency ranges still need a fresh local environment and MySQL run.
Saved results document the historical run, not successful execution of this copy.
There is no formal JSON-schema or MySQL-parser validation in the standard-library
checker, and pattern-based secret scans cannot guarantee detection of every
possible secret. A later run must be reviewed before sharing new outputs.

Aaron can review project wording and decide whether to add a license for his work. The original password remains in the untouched local
coursework; if it is still in use, rotate it separately. Oracle's sample schema
and records retain their own attribution and licensing. No database data is
redistributed in this package.
