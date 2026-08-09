# Photo page navigation: filmstrip as the single nav control

**Date:** 2026-08-09
**Status:** Approved, ready for implementation
**Affects:** `templates/photo-page-template.html`, `src/kgdotcom/generators/photos.py`, `tests/test_photos.py`

## Problem

Individual photo pages carry two separate navigation affordances in the right column:

1. A text row of `Previous` / `Next` links.
2. A strip of 60px thumbnails.

They are redundant and visually unrelated. The strip is always three thumbnails —
`[prev][current][next]`, or `[current][next][next-next]` on the first photo — but the
current photo is rendered **unlinked and unmarked**. With no indication of which
thumbnail represents the current page, the strip reads as three arbitrary images
rather than a position indicator, and the text links duplicate its outer two entries
without being tied to them.

## Decision

Make the thumbnail strip the single navigation control. Delete the separate
`Previous`/`Next` text row.

The strip shows only entries that exist: `[current][next]` on the first photo,
`[prev][current][next]` in the middle, `[prev][current]` on the last. A short strip
is meaningful — it tells you that you are at the start or end of the gallery. The
`next-next` padding is removed.

### Rejected alternatives

- **Move navigation beneath the photo.** Puts nav where the eye already is, but is a
  larger restructuring than the problem warrants.
- **Keep both, align them.** Smallest change, but leaves two nav affordances for one
  job — the redundancy was the actual complaint.
- **Always three slots, blank the missing one.** Keeps the current photo centred, but
  an empty box reads as broken rather than as "end of gallery".

## Markup

Inside `.rcol`, the existing prev/next `<section>` and thumbnail `<section>` collapse
into a single `<nav>`:

```html
<nav class="filmstrip" aria-label="Gallery navigation">
  <h3>{{gallery.name}}</h3>
  <ul>
    {% if previous_image %}
    <li><a href="{{previous_image.image_page}}">
      <img class="navthumb" src="{{previous_image.thumb_filename}}"
           alt="{{previous_image.title}}"><span>&lsaquo; prev</span>
    </a></li>{% endif %}
    <li class="current" aria-current="page">
      <img class="navthumb" src="{{photo.thumb_filename}}" alt=""><span>current</span>
    </li>
    {% if next_image %}
    <li><a href="{{next_image.image_page}}">
      <img class="navthumb" src="{{next_image.thumb_filename}}"
           alt="{{next_image.title}}"><span>next &rsaquo;</span>
    </a></li>{% endif %}
  </ul>
</nav>
```

The current entry stays unlinked, because it is the page the reader is already on,
but is marked so its role is legible. Accessibility:

- `aria-current="page"` on the current `<li>`.
- Thumbnail `alt` carries the **destination photo's title**, so the link's purpose is
  clear to a screen reader.
- The current thumbnail is decorative (`alt=""`); the visible `current` label and
  `aria-current` already convey its role.

## CSS

In the template's inline `<style>`:

- `.filmstrip ul` — `display: flex`, `list-style: none`, `padding-left: 0`,
  `gap: 0.5em`.
- `.filmstrip li` — `display: flex; flex-direction: column; align-items: center`, so
  each label sits directly under its own thumbnail.
- `.navthumb` — 60px → **72px** square, keeping `object-fit: cover`. The larger size
  gives the labels something to sit under and keeps the targets comfortable.
- `.filmstrip .current img` — `outline: 2px solid #AA0000` with a small
  `outline-offset`. Deliberately `outline` and not `border`: an outline is drawn
  outside the box and does not change layout, so the marked thumbnail stays exactly
  the same size as its neighbours.
- `.filmstrip span` — small (`font-size: .8em`), muted, `text-align: center`.

Deletions:

- The `.right { float: right; }` rule, whose only consumer was the prev/next row.
- The `wrap`, `first`, and `last` classes on the old links. These have **no CSS
  definition anywhere in the project** and are already dead.

## Generator

`next-next` becomes unused once the template stops rendering it:

- `src/kgdotcom/generators/photos.py` — rename `get_prev_next_nextnext` to
  `get_prev_next`, drop `next_next_el` from the loop and the return tuple, and update
  its docstring.
- `create_image_page` — unpack two values instead of three, and delete the
  `pagevalues["next_next_image"] = next_next_image` assignment along with the
  `if not previous:` guard that wraps it.
- `tests/test_photos.py:115` — update the import and the call. The test already
  discards the third value as `_`, so its assertions are unaffected.

## Responsive behaviour

None required. The strip is at most three 72px thumbnails plus gaps (~230px), so it
fits the 300px sidebar in two-column mode and never needs to wrap. When the container
query stacks the layout, the strip sits at the top of the full-width sidebar,
left-aligned.

## Verification

- Regenerate photo pages and confirm on a middle photo, the **first** photo of a
  gallery, and the **last** photo that the strip renders 3 / 2 / 2 entries
  respectively, with the current entry marked and unlinked.
- Confirm prev/next hrefs still follow the gallery's newest-first display order.
- Re-run the horizontal-overflow sweep (photo pages, 320–1500px): expect `0px`
  overflow and the sidebar flush with the top of the photo.
- `make test` passes.

## Out of scope

- Keyboard navigation (arrow keys between photos).
- Any change to gallery index pages.
- The photo page's Sharing / Captured / Metadata / Rights sections, which keep their
  current order and styling.
