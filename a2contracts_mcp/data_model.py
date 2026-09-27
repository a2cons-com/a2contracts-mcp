"""The one-page map of how things relate in A2 Contracts, for an AI
client: the `a2contracts://data-model` resource and the
`describe_data_model` tool. A copy of the app's backend/mcp_server/
data_model.py (minus the remote endpoint's OAuth scopes) -- keep the two
in step (the app repo's CLAUDE.md: MCP + docs current with every change)."""

DATA_MODEL = """\
A2 CONTRACTS -- HOW THINGS RELATE (for an AI client)

Ids: every tool takes a project by its `id` from list_projects (the
company-scoped project number, not a database id). Everything below
belongs to one project and one company; you see only what the signed-in
user (this server's device token) can see.

PROJECT
  name, project number, client (the customer), address, status. The hub
  every other record hangs off.

ESTIMATE = the PROPOSAL (get_estimate)
  divisions (a section, e.g. csi_code "09" Finishes) -> line items
  (title, qty, unit, unit_cost, cost_type material|labor|subcontractor|
  equipment|other, is_allowance). Markups (overhead, fee, contingency)
  are applied on top by the app and reported in `totals`.
  proposal_finalized_at == null  -> a DRAFT: divisions and line items can
  be added/changed (estimate:draft). Once finalized it is the contract
  basis and is LOCKED: new scope goes through a CHANGE ORDER.
  change orders: each has its own line items; editable while status is
  "pending"; approving/reopening one is a person's act in the app.

SCHEDULE (get_schedule)
  one schedule task per line item, kept in sync automatically, plus
  standalone milestones/phases (permit issued, inspections, walkthrough
  -- create_milestones). Each task: start_date, end_date or
  duration_days, status not_started|in_progress|done, is_milestone,
  ignored (a line item that needs no schedule row: allowances, fees).
  dependencies link tasks: task waits on depends_on, type FS (finish-to-
  start, the usual), SS, FF, SF, with lag_days. Cycles are refused. The
  app draws the Gantt and the critical path from these.
  started_at / completed_at record when a task actually started and
  finished (stamped by the app from status; read-only). A long-lead item
  (windows, cabinets, equipment) is lead_time_days on the task that needs
  it: order-by = start_date - lead_time_days; ordered_on once ordered. The
  Gantt shows it as a shadow bar and the critical path as a hidden
  "Procure" step in front of the task.

PLANS (list_plan_sheets)
  collection (a permit set: "Plans" by default, or e.g. original house
  plans) -> folder (one level, usually by discipline: Architectural,
  Electrical...) -> sheet (A-101 "Proposed ground level floor plan").
  A sheet has versions (number + date); the current one is what you
  render. Sheets have a scale (real length per drawing length; 48 means
  1/4" = 1'-0"); measurements need it. get_sheet_info gives size in PDF
  points (origin top-left) -- every markup coordinate is in those.
  markups live on a sheet, on a layer (project-wide, named, colored):
  pen, line, arrow, rect, ellipse, cloud, polygon, text, measurements
  (length, area, count), markers (a numbered pin with title/notes/
  status), stamps (symbols from list_symbols). A markup is PRIVATE to
  its author until a person publishes it; you can only create private
  ones (plans:annotate) -- draw on a layer named for suggestions and say
  so.

PHOTOS (read via api_get)
  /api/project-photos/?project= -- every photo/video: taken_at, caption,
  is_favorite, kind photo|video, width/height, ai_caption + ai_tags (what
  the owner's local AI indexer saw), markup_counts. Search like the app's
  search box: /api/project-photos/search/?project=&q=words -> {ids}.
  Albums: /api/photo-albums/?project= (hand-picked, or smart: all /
  favorites / a date range / words). Photos can carry markups too -- the
  same plan-markup rows with `photo` instead of `sheet`, coordinates in
  the photo's pixels (/api/plan-markups/?photo=<id>); no measuring on
  photos.

3D MODELS (read via api_get): /api/project-models/?project= -- IFC
  models and site scans, grouped by day and into albums
  (/api/project-model-albums/?project=).

REPORTS (read via api_get)
  Daily / weekly / monthly site reports a person publishes:
  /api/daily-reports/?project=&kind=daily|weekly|monthly lists them,
  /api/daily-reports/<id>/ is one frozen report: its note, photos,
  permit and inspection changes, plan pages with new versions or
  published annotations, 3D models, and a `schedule` section (summary;
  done / in_progress / coming_up; weekly/monthly add long_lead, monthly
  the projected finish). A weekly is built from that week's dailies, a
  monthly from its weeklies. Drafts and publishing are people's acts in
  the app.

DOCUMENTS AND FILES (read via api_get): /api/project-documents/?project=
  (contracts, permits, insurance -- categorized) and the free folders of
  files: /api/project-file-folders/?project=,
  /api/project-files/?project= (name, size, type, folder).

PERMITS AND INSPECTIONS (read via api_get /api/permits/?project=,
  /api/inspections/?project=): a master permit and sub-permits per
  trade, each with inspections (type, date, result). Synced from the
  city's portal; read-only here.

MONEY (read-only for AI clients, by design)
  bid packages -> bids from subcontractors -> a subcontract (the award)
  with payment terms; subcontractor payments and lien releases;
  payment applications (pay apps) to the client, deposits and payments
  received; QuickBooks transactions and budgets. You may read what the
  person can read (api_get) and must never try to change any of it;
  finalizing, approving, submitting, locking and paying are human acts
  in the app, and the API refuses those writes to an AI token.

TYPICAL FLOWS
  - Takeoff on a plan: list_plan_sheets -> get_sheet_info -> render_sheet
    (whole sheet at ~40 dpi, then crops at 100-150 dpi) -> create_markups
    (counts/lengths/areas) on a suggestions layer -> tell the person to
    review and publish; optionally create_line_items on the draft
    estimate from what you measured.
  - Schedule a project: get_estimate + get_schedule -> propose durations
    per line item and an FS chain per trade -> update_schedule_tasks +
    set_dependencies -> the person reviews the Gantt.
  - Long-lead check: get_schedule -> for tasks needing ordered materials,
    set lead_time_days (update_schedule_tasks) -> the weekly report's
    Long lead list and the Gantt show what to order when.
  - "What happened this week": api_get /api/daily-reports/?project=&kind=
    weekly, then the report by id -- its note and schedule section.
  - Anything financial: read, summarize, recommend; never write.
"""
