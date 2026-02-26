Storage & Saving

localStorage is still the working cache (fast, instant)
Save File button (green, always visible) exports JSON to your machine — that's your real database
Ctrl+S keyboard shortcut triggers Save File
A pulsing "Unsaved changes" indicator appears in the header whenever you've made edits without saving
Browser warns you if you try to close with unsaved changes
A 5-minute reminder toast if you forget to save

Import — JSON (sync between machines)

4 merge strategies: Skip duplicates, Update if newer (uses lastModified timestamp), Always overwrite, or Replace entire library
Shows an Added / Updated / Skipped summary after every import
Drag & drop supported

Import — CSV (from spreadsheet)

Paste in data from Excel or Google Sheets
Additive only — never overwrites existing records
If your CSV has an id column, deduplication works; otherwise new IDs are generated
Column format shown right in the UI

Multi-machine workflow

Edit on Machine A → Ctrl+S → saves cantus-library-2026-02-25.json
Copy that file to Machine B (USB, email, Drive, etc.)
Import on Machine B → choose "Update if newer"
+++++++++++++++++++++++++++++
📱 Phone (under 600px) — Android & iOS

Clean swipeable card list — one piece per row, tap to open
Floating gold + button to add pieces
Bottom navigation bar with Save, Import, Search, and status
All modals slide up as bottom sheets (native mobile feel)
Detail view slides up from bottom
Notch/safe area support for iPhone X and newer
Header decluttered — just logo and add button

📟 Tablet (600–1023px) — iPad, Android tablet

Card grid layout — 2–3 columns depending on width
Each card shows title, composer, voicing, season, publisher, year, last performed, copies, and notes preview
Floating + button for adding
Detail panel slides in from the right side (not a bottom sheet)
Modals are centered, not bottom sheets

🖥️ Desktop (1024px+)

Full table view with all columns visible
View toggle button lets you switch between table and card grid
Full header with all buttons
Side-panel detail view
Keyboard shortcuts (Ctrl+S, Ctrl+K, Escape)

Installing on phone:

Android Chrome: Menu → "Add to Home Screen"
iOS Safari: Share button → "Add to Home Screen"
