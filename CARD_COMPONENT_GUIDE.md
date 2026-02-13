# Reusable Card Component Guide

This guide explains how to use the shared card component across Django templates in the NAA project. It is written for front-end developers and template editors.

- Component file: accounts/templates/accounts/partials/card.html
- Example partials using the card:
  - Committee workspace: accounts/templates/accounts/partials/committee/teammates_table.html, accounts/templates/accounts/partials/committee/committee_announcements.html
  - CPD tracker: accounts/templates/accounts/partials/cpd/activity_table.html
  - Resources library: accounts/templates/accounts/partials/resources/library_table.html

## 1. Component Overview
- Provides a consistent, responsive, accessible container for content blocks such as lists, tables, announcements, forms, and media.
- Centralizes spacing, typography, and hover/visual effects; eliminates duplicated card markup across pages.
- Encourages modular design via parameters and slot-style body partials, making complex sections maintainable and testable.

## 2. Supported Inputs / Parameters
Pass parameters using the Django include “with” syntax.

- Content
  - title: Main heading inside the card body
  - subtitle: Secondary text under the title
  - text: General body copy (accepts plain text, filters like truncatewords)

- Media
  - image_url: Displays an image at top of card body
  - image_alt: Accessible alt text for the image

- Badges and Links
  - badge_html: Injects a badge or icon snippet at the top of the body
  - link_url: If provided, title becomes a link to this URL

- Primary Action
  - action_url: URL the primary button links to
  - action_text: Button label (defaults to “Open”)
  - action_icon_class: Optional icon class (e.g., “bi bi-download”)
  - action_class: Button class (defaults to “btn btn-primary w-100 btn-rounded”)
  - action_download: True to mark link as a download

- Metadata
  - meta_left_text: Left-side small meta text (e.g., author)
  - meta_right_text: Right-side small meta text (e.g., date)
  - meta_left_icon_class: Optional icon for left meta
  - meta_right_icon_class: Optional icon for right meta

- Styling and behavior
  - body_class: Classes for the card body (e.g., “p-4” or “p-4 d-flex flex-column”)
  - card_class: Classes for the card container (defaults to “border-0 shadow-sm”)
  - style: Inline style string (use sparingly)
  - hover: When truthy, adds a hover-card effect class

- Header
  - header_title: Simple text header; rendered inside card-header
  - header_html: Rich header content (e.g., with icons)
  - header_class: Classes for card-header (e.g., “bg-white fw-bold”)

- Body Partial
  - body_partial: A template path to include inside the card body
  - Important: body_partial templates should not contain their own “card-body” wrapper; the component provides it

- Additional (optional)
  - header/footer slots: footer_html, footer_class
  - wrapper_class: Wrap card in an outer div with this class
  - actions_html: Advanced custom action area (prefer action_url setup for simple buttons)
  - body_html: Inject raw HTML directly into the body (use sparingly; prefer body_partial)

## 3. Usage Patterns
- Simple content card
  - Use title, text, body_class, card_class for standard content
- Linked title and primary action
  - Use link_url to wrap title in a link; use action_* for the call-to-action
- Image, badge, and download
  - Use image_url/image_alt, badge_html, action_download for file cards
- Forms/tables via body_partial
  - Use header_title/header_html and body_partial to slot complex content (forms, tables, tabbed sections)

## 4. Best Practices
- Do not include a “card-body” wrapper inside body_partial templates; the component provides it.
- Keep inline styles minimal; prefer utility classes and shared styles in naa.css.
- Use header_title for simple section headers or header_html for icons and richer content.
- Preserve semantic and accessible HTML:
  - Use image_alt for images and proper heading levels in body partials.
  - Keep interactive elements focusable and keyboard-friendly.
- Use responsive grid utilities (container, row, col-*) and spacing helpers consistently for layout.

## 5. Examples

### A. Simple Content Card

```django
{% include 'accounts/partials/card.html' with 
  card_class='border-0 shadow-sm h-100'
  body_class='p-4'
  title='Welcome to NAA'
  subtitle='Getting Started'
  text='Explore the latest announcements and resources.' %}
```

### B. Linked Title + Primary Action

```django
{% url 'announcement' post.pk as ann_url %}
{% include 'accounts/partials/card.html' with 
  card_class='shadow-sm h-100'
  body_class='p-4'
  link_url=ann_url
  title=post.title
  text=post.summary|default:post.content|truncatewords:20
  action_url=ann_url
  action_text='Read more →'
  action_icon_class='bi bi-arrow-right'
  action_class='btn btn-link text-primary p-0' %}
```

### C. Image, Badge, and Download

```django
{% include 'accounts/partials/card.html' with
  card_class='border-0 shadow-sm h-100'
  body_class='p-4 d-flex flex-column'
  image_url=item.image.url
  image_alt=item.title
  badge_html='<span class="badge bg-info-subtle text-info"><i class="bi bi-file-earmark-pdf me-1"></i> PDF</span>'
  title=item.title
  text=item.description|striptags|truncatewords:12
  action_url=item.file.url
  action_text='Download'
  action_icon_class='bi bi-download'
  action_class='btn btn-primary w-100 mt-auto btn-rounded'
  action_download=True %}
```

### D. Body Partial for Tables/Forms

```django
{% include 'accounts/partials/card.html' with
  card_class='border-0 shadow-sm'
  header_title='Activity History'
  header_class='bg-white py-3'
  body_class='p-0'
  body_partial='accounts/partials/cpd/activity_table.html' %}
```

Note: The referenced partial (activity_table.html) contains only table markup—no card-body wrapper.

## 6. Notes / Warnings
- When not to use the card component
  - Complex views that control multiple nested cards or dynamic wrappers beyond a single card body.
  - Situations where the content must dictate custom container semantics that conflict with card semantics.
- Extending for new use cases
  - Prefer adding new slot partials (body_partial) for unique views (forms, list groups, tabs).
  - If a repeated pattern emerges, add a clearly named parameter to the component and update this guide.
  - Avoid passing long HTML strings; use action_* or body_partial instead to keep templates lint-friendly and readable.
