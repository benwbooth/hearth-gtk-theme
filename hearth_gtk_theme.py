#!/usr/bin/env python3
"""Hearth: a GTK 2/3/4 theme in the colours and shapes of hearth (Ben's
macOS-26-style shell, ~/src/hearth) and his Qt apps' Mac menus.

    hearth_gtk_theme.py --adw-gtk3 DIR --libadwaita-css FILE --adwaita-gtk2 DIR --out DIR

writes DIR/Hearth (light) and DIR/Hearth-dark:

- gtk-3.0: adw-gtk3's stylesheet (libadwaita's look for GTK 3), then hearth's
  palette as GTK named colours (a later @define-color wins), then hearth's
  own rules (rules()).
- gtk-4.0: libadwaita's own stylesheet (so plain GTK 4 apps and libadwaita
  apps look alike), the palette and the same rules.
- gtk-4.0/libadwaita-user.css: palette for both modes (@media
  prefers-color-scheme) and the rules, for ~/.config/gtk-4.0/gtk.css: the
  only way into libadwaita apps, which never load a GTK theme.
- gtk-2.0: Adwaita's GTK 2 theme (gnome-themes-extra, the adwaita engine)
  with hearth's gtk-color-scheme and flat accent menu rows.

The accent everywhere is @accent_bg_color, so a theme that @imports one of
these and redefines it recolours the lot (hearth-color-scheme does that for
accents other than the system blue).

The palette is shell/Theme.qml's; the menus are
shared/app-menus/MacMenuStyle.qml's (radius 14, padding 5, rows 27, a 9 px
accent selection, grey shortcuts, the glass tint arbor blurs behind).
"""
import argparse
import os
import shutil

# --- palette ---------------------------------------------------------------

PALETTE = {
    "dark": dict(
        accent="#0a84ff",
        window="#202326", window_fg="#fcfcfc", view="#1a1c1f", view_fg="#fcfcfc",
        alt="#292c30", raised="#31363b", border="#3f444a", dim="#a1a9b1",
        headerbar="#202326", headerbar_backdrop="#202326",
        sidebar="#292c30", sidebar_backdrop="#25282b",
        card="rgba(255, 255, 255, 0.05)", dialog="#292c30", popover="#26282b",
        thumbnail="#31363b",
        shade="rgba(0, 0, 0, 0.36)", separator="rgba(255, 255, 255, 0.10)",
        hover="rgba(255, 255, 255, 0.08)", pressed="rgba(255, 255, 255, 0.14)",
        selected="rgba(255, 255, 255, 0.16)",
        button="rgba(255, 255, 255, 0.10)", button_hover="rgba(255, 255, 255, 0.15)",
        button_active="rgba(255, 255, 255, 0.22)",
        button_ring="rgba(255, 255, 255, 0.06)", button_shadow="rgba(0, 0, 0, 0.0)",
        field="rgba(255, 255, 255, 0.06)", field_border="rgba(255, 255, 255, 0.12)",
        destructive="#ff453a", success="#30d158", warning="#ff9f0a",
        scrollbar="rgba(255, 255, 255, 0.38)", scrollbar_hover="rgba(255, 255, 255, 0.55)",
        tip="rgba(41, 42, 46, 0.96)",
        # MacMenuStyle.qml
        menu_fg="#f5f5f7", menu_glass="rgba(38, 40, 43, 0.74)", menu_solid="#26282b",
        menu_sheen="rgba(255, 255, 255, 0.06)", menu_dim="rgba(255, 255, 255, 0.55)",
        menu_dim_hover="rgba(255, 255, 255, 0.85)", menu_disabled="rgba(255, 255, 255, 0.28)",
        menu_sep="rgba(255, 255, 255, 0.13)", menu_edge="rgba(0, 0, 0, 0.28)",
        menu_rim="rgba(255, 255, 255, 0.05)", menu_shadow="rgba(0, 0, 0, 0.32)",
        # GTK 2's gtk-color-scheme
        gtk2=dict(fg_color="#fcfcfc", bg_color="#202326", base_color="#1a1c1f", text_color="#fcfcfc",
                  insensitive_fg_color="#6e747a", insensitive_bg_color="#202326", menu_color="#2b2d30",
                  window_color="#202326", tooltip_fg_color="#fcfcfc", tooltip_bg_color="#31363b",
                  column_header_color="#a1a9b1", hover_column_header_color="#fcfcfc"),
    ),
    "light": dict(
        accent="#007aff",
        window="#eff0f1", window_fg="#232629", view="#ffffff", view_fg="#232629",
        alt="#fcfcfc", raised="#ffffff", border="#c9ced3", dim="#6e7882",
        headerbar="#eff0f1", headerbar_backdrop="#f4f5f6",
        sidebar="#e5e7e9", sidebar_backdrop="#eceef0",
        card="#ffffff", dialog="#f6f7f8", popover="#f9f9fa",
        thumbnail="#ffffff",
        shade="rgba(0, 0, 0, 0.08)", separator="rgba(0, 0, 0, 0.10)",
        hover="rgba(0, 0, 0, 0.07)", pressed="rgba(0, 0, 0, 0.12)",
        selected="rgba(0, 0, 0, 0.10)",
        button="#ffffff", button_hover="#f7f7f8", button_active="#e9eaec",
        button_ring="rgba(0, 0, 0, 0.10)", button_shadow="rgba(0, 0, 0, 0.10)",
        field="#ffffff", field_border="rgba(0, 0, 0, 0.14)",
        destructive="#ff3b30", success="#34c759", warning="#ff9500",
        scrollbar="rgba(0, 0, 0, 0.38)", scrollbar_hover="rgba(0, 0, 0, 0.55)",
        tip="rgba(250, 250, 251, 0.97)",
        menu_fg="#1d1d1f", menu_glass="rgba(249, 249, 250, 0.74)", menu_solid="#f9f9fa",
        menu_sheen="rgba(255, 255, 255, 0.20)", menu_dim="rgba(0, 0, 0, 0.5)",
        menu_dim_hover="rgba(255, 255, 255, 0.85)", menu_disabled="rgba(0, 0, 0, 0.26)",
        menu_sep="rgba(0, 0, 0, 0.11)", menu_edge="rgba(0, 0, 0, 0.09)",
        menu_rim="rgba(255, 255, 255, 0.40)", menu_shadow="rgba(0, 0, 0, 0.2)",
        gtk2=dict(fg_color="#232629", bg_color="#eff0f1", base_color="#ffffff", text_color="#232629",
                  insensitive_fg_color="#a0a5aa", insensitive_bg_color="#eff0f1", menu_color="#f9f9fa",
                  window_color="#eff0f1", tooltip_fg_color="#232629", tooltip_bg_color="#fcfcfc",
                  column_header_color="#6e7882", hover_column_header_color="#232629"),
    ),
}

# The font hearth and the Mac menus use (Inter: SF Pro's nearest open relative).
FONT = 'Inter, "Inter Variable", "SF Pro", "SF Pro Text", "Noto Sans", sans-serif'
# 13 pt at hearth's 1.125 px/pt, Inter's 4% smaller (MacMenuStyle.fontSize).
MENU_FONT_PX = "14.1px"


def named_colors(mode, accent=None):
    """GTK named colours (the names libadwaita and adw-gtk3 use, and GTK's
    own theme_* ones) plus hearth_* ones the rules use."""
    p = PALETTE[mode]
    a = accent or p["accent"]
    c = {
        "accent_bg_color": a,
        "accent_fg_color": "#ffffff",
        "accent_color": "@accent_bg_color",
        "destructive_bg_color": p["destructive"], "destructive_fg_color": "#ffffff",
        "destructive_color": p["destructive"],
        "success_bg_color": p["success"], "success_fg_color": "#ffffff", "success_color": p["success"],
        "warning_bg_color": p["warning"], "warning_fg_color": "rgba(0, 0, 0, 0.8)", "warning_color": p["warning"],
        "error_bg_color": p["destructive"], "error_fg_color": "#ffffff", "error_color": p["destructive"],
        "window_bg_color": p["window"], "window_fg_color": p["window_fg"],
        "view_bg_color": p["view"], "view_fg_color": p["view_fg"],
        "headerbar_bg_color": p["headerbar"], "headerbar_fg_color": p["window_fg"],
        "headerbar_border_color": p["window_fg"], "headerbar_backdrop_color": p["headerbar_backdrop"],
        "headerbar_shade_color": p["separator"], "headerbar_darker_shade_color": p["separator"],
        "sidebar_bg_color": p["sidebar"], "sidebar_fg_color": p["window_fg"],
        "sidebar_backdrop_color": p["sidebar_backdrop"], "sidebar_shade_color": p["separator"],
        "sidebar_border_color": p["separator"],
        "secondary_sidebar_bg_color": p["sidebar_backdrop"], "secondary_sidebar_fg_color": p["window_fg"],
        "secondary_sidebar_backdrop_color": p["sidebar_backdrop"],
        "secondary_sidebar_shade_color": p["separator"], "secondary_sidebar_border_color": p["separator"],
        "card_bg_color": p["card"], "card_fg_color": p["view_fg"], "card_shade_color": p["separator"],
        "dialog_bg_color": p["dialog"], "dialog_fg_color": p["window_fg"],
        "popover_bg_color": p["popover"], "popover_fg_color": p["menu_fg"], "popover_shade_color": p["shade"],
        "thumbnail_bg_color": p["thumbnail"], "thumbnail_fg_color": p["view_fg"],
        "shade_color": p["shade"],
        "scrollbar_outline_color": "transparent",
        # GTK 3's own names (adw-gtk3 maps most to the above; some apps and
        # Chromium read these).
        "theme_fg_color": p["window_fg"], "theme_text_color": p["view_fg"],
        "theme_bg_color": p["window"], "theme_base_color": p["view"],
        "theme_selected_bg_color": "@accent_bg_color", "theme_selected_fg_color": "#ffffff",
        "theme_unfocused_selected_bg_color": "@accent_bg_color", "theme_unfocused_selected_fg_color": "#ffffff",
        "borders": p["border"], "unfocused_borders": p["border"],
        # hearth's own
        "hearth_dim": p["dim"],
        "hearth_border": p["border"],
        "hearth_separator": p["separator"],
        "hearth_hover": p["hover"], "hearth_pressed": p["pressed"], "hearth_selected": p["selected"],
        "hearth_button": p["button"], "hearth_button_hover": p["button_hover"],
        "hearth_button_active": p["button_active"],
        "hearth_button_ring": p["button_ring"], "hearth_button_shadow": p["button_shadow"],
        "hearth_field": p["field"], "hearth_field_border": p["field_border"],
        "hearth_scrollbar": p["scrollbar"], "hearth_scrollbar_hover": p["scrollbar_hover"],
        "hearth_tip": p["tip"],
        "hearth_menu_fg": p["menu_fg"], "hearth_menu_glass": p["menu_glass"],
        "hearth_menu_solid": p["menu_solid"], "hearth_menu_sheen": p["menu_sheen"],
        "hearth_menu_dim": p["menu_dim"], "hearth_menu_dim_hover": p["menu_dim_hover"],
        "hearth_menu_disabled": p["menu_disabled"], "hearth_menu_sep": p["menu_sep"],
        "hearth_menu_edge": p["menu_edge"], "hearth_menu_rim": p["menu_rim"],
        "hearth_menu_shadow": p["menu_shadow"],
    }
    return c


def colors_css(mode, accent=None, indent=""):
    return "".join(f"{indent}@define-color {k} {v};\n" for k, v in named_colors(mode, accent).items())


# libadwaita reads CSS variables (--window-bg-color...) that its stylesheet
# sets from the named colours; its style manager also sets the accent ones
# itself (from the portal, snapped to its nine accents), so user CSS sets
# them again from ours.
ADW_VARS = ["accent-bg-color", "accent-fg-color", "accent-color",
            "destructive-bg-color", "destructive-fg-color", "destructive-color",
            "success-bg-color", "success-color", "warning-bg-color", "warning-color",
            "error-bg-color", "error-color",
            "window-bg-color", "window-fg-color", "view-bg-color", "view-fg-color",
            "headerbar-bg-color", "headerbar-fg-color", "headerbar-backdrop-color",
            "headerbar-shade-color", "headerbar-darker-shade-color",
            "sidebar-bg-color", "sidebar-fg-color", "sidebar-backdrop-color",
            "sidebar-border-color", "sidebar-shade-color",
            "secondary-sidebar-bg-color", "secondary-sidebar-fg-color",
            "secondary-sidebar-backdrop-color", "secondary-sidebar-border-color",
            "secondary-sidebar-shade-color",
            "card-bg-color", "card-fg-color", "card-shade-color",
            "dialog-bg-color", "dialog-fg-color",
            "popover-bg-color", "popover-fg-color", "popover-shade-color",
            "thumbnail-bg-color", "thumbnail-fg-color", "shade-color",
            "scrollbar-outline-color"]


def adw_vars_css():
    body = " ".join(f"--{v}: @{v.replace('-', '_')};" for v in ADW_VARS)
    return f":root {{ {body} --window-radius: 14px; --document-font-family: {FONT}; }}\n"


# --- rules -------------------------------------------------------------------

def rules(gtk):
    """hearth's look in GTK CSS, the same for light and dark (colours are the
    named ones above). gtk: 3 or 4; most selectors are shared."""
    focus = ":focus" if gtk == 3 else ":focus-within"
    out = [f"""
/* ---- hearth (generated by hearth-gtk-theme) ---- */

/* Push buttons: macOS 26 capsules, flat fill, the default one in the accent. */
button {{
  border-radius: 100px; border: none; background-image: none; text-shadow: none; -gtk-icon-shadow: none;
  background-color: @hearth_button; color: inherit;
  box-shadow: 0 0 0 1px @hearth_button_ring, 0 1px 1.5px @hearth_button_shadow;
  font-weight: normal;
}}
button label, headerbar button, headerbar button label {{ font-weight: normal; }}
button:hover {{ background-color: @hearth_button_hover; }}
button:active, button:checked {{ background-color: @hearth_button_active; }}
button:disabled {{ box-shadow: none; }}
button.flat, button.image-button.flat, headerbar button, .titlebar button, toolbar button, .toolbar button,
button.circular.flat, popover button.flat, actionbar button {{
  background-color: transparent; box-shadow: none;
}}
button.flat:hover, headerbar button:hover, .titlebar button:hover, toolbar button:hover, .toolbar button:hover,
popover button.flat:hover, actionbar button:hover {{ background-color: @hearth_hover; }}
button.flat:active, button.flat:checked, headerbar button:active, headerbar button:checked,
.titlebar button:active, .titlebar button:checked, toolbar button:active, toolbar button:checked,
actionbar button:active, actionbar button:checked {{ background-color: @hearth_pressed; }}
button.suggested-action, button.default, button.default:hover {{
  background-color: @accent_bg_color; color: @accent_fg_color; box-shadow: none;
}}
button.suggested-action:hover {{ background-color: shade(@accent_bg_color, 1.08); }}
button.suggested-action:active, button.suggested-action:checked {{ background-color: shade(@accent_bg_color, 0.9); }}
button.destructive-action {{ background-color: @destructive_bg_color; color: @destructive_fg_color; box-shadow: none; }}
button.destructive-action:hover {{ background-color: shade(@destructive_bg_color, 1.08); }}
button.suggested-action:disabled, button.destructive-action:disabled {{ background-color: @hearth_button; color: @hearth_dim; }}
button.link, button.link:hover, button.link:active {{ background-color: transparent; box-shadow: none; color: @accent_bg_color; }}

/* Text fields: rounded, an accent focus ring outside them (macOS). */
entry, spinbutton:not(.vertical), searchbar entry {{
  border-radius: 8px; border: none; background-image: none;
  background-color: @hearth_field; color: @view_fg_color;
  box-shadow: inset 0 0 0 1px @hearth_field_border;
}}
entry{focus}, spinbutton:not(.vertical){focus} {{
  box-shadow: inset 0 0 0 1px @accent_bg_color, 0 0 0 3px alpha(@accent_bg_color, 0.45);
  outline: none;
}}
entry.search, searchentry, searchbar entry {{ border-radius: 100px; }}
spinbutton:not(.vertical) entry, spinbutton:not(.vertical) text, searchentry text, entry text {{
  box-shadow: none; background: none; outline: none;
}}
spinbutton:not(.vertical) button {{ background-color: transparent; box-shadow: none; border-radius: 6px; }}
spinbutton:not(.vertical) button:hover {{ background-color: @hearth_hover; }}
entry selection, text selection, label selection, textview text selection, entry > text > selection {{
  background-color: alpha(@accent_bg_color, 0.35); color: inherit;
}}

/* Check boxes, radios, switches, sliders. */
check {{ border-radius: 5px; }}
check:checked, check:indeterminate, radio:checked, radio:indeterminate {{
  background-color: @accent_bg_color; color: @accent_fg_color; box-shadow: none; background-image: none;
}}
switch:checked {{ background-color: @accent_bg_color; }}
switch slider, switch > slider {{ background-color: #ffffff; box-shadow: 0 1px 2px rgba(0, 0, 0, 0.3); }}
scale trough {{ min-height: 4px; min-width: 4px; border-radius: 100px; background-color: @hearth_selected; }}
scale highlight {{ background-color: @accent_bg_color; border-radius: 100px; }}
scale slider {{
  background-color: #ffffff; border: none; background-image: none;
  box-shadow: 0 0 0 0.5px rgba(0, 0, 0, 0.12), 0 1px 3px rgba(0, 0, 0, 0.3);
}}
progressbar progress {{ background-color: @accent_bg_color; border-radius: 100px; }}
progressbar trough {{ border-radius: 100px; }}

/* Slim scroll bars. */
scrollbar {{ background-color: transparent; border: none; box-shadow: none; }}
scrollbar slider {{ border-radius: 100px; background-color: @hearth_scrollbar; }}
scrollbar slider:hover, scrollbar slider:active {{ background-color: @hearth_scrollbar_hover; }}

/* Unified toolbars: the window colour, a hairline under them. */
headerbar, .titlebar:not(headerbar) {{
  background-image: none; background-color: @headerbar_bg_color;
  box-shadow: inset 0 -1px @hearth_separator; border: none;
}}
headerbar .title, .titlebar .title {{ font-weight: 600; }}

/* Lists and views: selection in the accent, rounded where GTK lets it be. */
.sidebar row:selected, .navigation-sidebar row:selected, placessidebar row:selected {{
  border-radius: 8px; background-color: @hearth_selected; color: inherit;
}}
.navigation-sidebar > row, placessidebar row {{ border-radius: 8px; }}

/* Tooltips. */
tooltip, tooltip.background {{
  border-radius: 8px; background-color: @hearth_tip; color: @hearth_menu_fg; box-shadow: none; border: none;
}}
"""]
    if gtk == 3:
        out.append(f"""
/* ---- menus (MacMenuStyle.qml): GTK 3 ---- */
/* GTK can't blur what's behind a menu; arbor does (popups {{ background-effect
   {{ blur true }} }}), so menus in GTK's popup windows get the translucent glass
   tint over that blur. Plain `menu` is solid: Chromium/Electron read their
   menu colour from `window.background menu` (not a popup window) and flatten
   a translucent one onto the window colour; arbor draws that colour
   see-through instead (hearth-color-scheme's arbor-popups.kdl). */
scrollbar slider {{ min-width: 6px; min-height: 6px; border: none; }}
scrollbar.overlay-indicator:not(.hovering) slider {{ min-width: 5px; min-height: 5px; }}

window.popup decoration, .csd.popup decoration {{
  border-radius: 14px;
  box-shadow: 0 9px 26px @hearth_menu_shadow, 0 0 0 1px @hearth_menu_edge;
}}
menu, .menu, .context-menu {{
  background-color: @hearth_menu_solid; color: @hearth_menu_fg; border-radius: 14px; border: none; padding: 5px;
  box-shadow: inset 0 0 0 1px @hearth_menu_rim;
  font-family: {FONT}; font-size: {MENU_FONT_PX}; letter-spacing: -0.09px;
}}
menu menuitem, .menu menuitem, .context-menu menuitem {{
  min-height: 27px; min-width: 193px; padding: 0 11px; border-radius: 9px; color: @hearth_menu_fg; text-shadow: none;
}}
menu menuitem:hover, .menu menuitem:hover, .context-menu menuitem:hover {{ background-color: @accent_bg_color; color: #ffffff; }}
menu menuitem:disabled, .menu menuitem:disabled {{ color: @hearth_menu_disabled; }}
menu menuitem accelerator {{ color: @hearth_menu_dim; letter-spacing: 0.6px; }}
menu menuitem:hover accelerator {{ color: @hearth_menu_dim_hover; }}
menu menuitem arrow {{ min-width: 12px; min-height: 12px; color: @hearth_menu_dim; }}
menu menuitem:hover arrow {{ color: #ffffff; }}
menu menuitem check, menu menuitem radio {{
  min-width: 14px; min-height: 14px; margin-right: 6px; background: none; border: none; box-shadow: none; color: inherit;
}}
menu separator, .menu separator {{ min-height: 1px; margin: 4px 11px; background-color: @hearth_menu_sep; }}
menu > arrow {{ background-color: @hearth_menu_solid; border: none; color: @hearth_menu_dim; }}
window.popup menu, window.popup .menu, window.popup .context-menu {{
  background-color: @hearth_menu_glass; background-image: linear-gradient(@hearth_menu_sheen, transparent 30%);
}}
window.popup menu > arrow {{ background-color: transparent; }}
menubar {{ padding: 0 4px; box-shadow: none; }}
menubar > menuitem {{ border-radius: 6px; padding: 3px 9px; margin: 2px 0; }}
menubar > menuitem:hover {{ background-color: @hearth_hover; box-shadow: none; color: inherit; }}

/* Popovers (GTK 3 draws them in the window: solid). */
popover, popover.background {{
  background-color: @popover_bg_color; color: @popover_fg_color; border-radius: 14px; padding: 5px;
  border: 1px solid @hearth_menu_edge; box-shadow: 0 9px 26px @hearth_menu_shadow;
}}
popover.menu modelbutton, popover modelbutton {{ min-height: 27px; padding: 0 11px; border-radius: 9px; color: @hearth_menu_fg; }}
popover.menu modelbutton:hover, popover modelbutton:hover {{ background-color: @accent_bg_color; color: #ffffff; }}
popover.menu separator, popover separator {{ margin: 4px 11px; background-color: @hearth_menu_sep; }}

/* Alerts. */
messagedialog.background, messagedialog .titlebar, messagedialog .dialog-vbox {{
  background-image: none; background-color: @dialog_bg_color; color: @dialog_fg_color; text-shadow: none;
}}
messagedialog.csd decoration {{ border-radius: 14px; box-shadow: 0 9px 26px @hearth_menu_shadow, 0 0 0 1px @hearth_menu_edge; }}
messagedialog .titlebar {{ border-top-left-radius: 14px; border-top-right-radius: 14px; box-shadow: none; }}
messagedialog.csd.background {{ border-bottom-left-radius: 14px; border-bottom-right-radius: 14px; }}
messagedialog .dialog-action-area button {{ border-radius: 100px; }}

/* Window corners. */
window.csd decoration, .csd decoration {{ border-radius: 12px; }}
""")
    else:
        out.append(f"""
/* ---- menus and popovers (MacMenuStyle.qml): GTK 4 ---- */
/* Popovers are their own surfaces: glass tint, arbor blurs behind it. */
popover > contents, popover.background > contents {{
  background-color: @hearth_menu_glass; background-image: linear-gradient(@hearth_menu_sheen, transparent 30%);
  color: @hearth_menu_fg; border-radius: 14px;
  box-shadow: 0 9px 26px @hearth_menu_shadow, 0 0 0 1px @hearth_menu_edge, inset 0 0 0 1px @hearth_menu_rim;
}}
popover > arrow, popover.background > arrow {{ background-color: @hearth_menu_glass; border-color: @hearth_menu_edge; }}
popover.menu > contents {{
  padding: 0; min-width: 202px; font-family: {FONT}; font-size: {MENU_FONT_PX}; letter-spacing: -0.09px;
}}
popover.menu > contents > stack > box, popover.menu > contents > scrolledwindow > viewport > stack > box {{ padding: 5px; }}
/* macOS menus have no arrow: GTK keeps its room, a gap under the button. */
popover.menu > arrow {{ background: none; border: none; box-shadow: none; }}
popover.menu accelerator {{ margin-left: 28px; }}
popover.menu label.title {{ font-weight: 600; padding: 4px 11px; }}
popover.menu modelbutton {{ min-height: 27px; min-width: 0; padding: 0 11px; border-radius: 9px; color: @hearth_menu_fg; }}
popover.menu modelbutton:hover, popover.menu modelbutton:selected {{ background-color: @accent_bg_color; color: #ffffff; }}
popover.menu modelbutton:disabled {{ color: @hearth_menu_disabled; }}
popover.menu modelbutton accelerator {{ color: @hearth_menu_dim; letter-spacing: 0.6px; }}
popover.menu modelbutton:hover accelerator, popover.menu modelbutton:selected accelerator {{ color: @hearth_menu_dim_hover; }}
popover.menu modelbutton arrow {{ color: @hearth_menu_dim; }}
popover.menu modelbutton:hover arrow, popover.menu modelbutton:selected arrow {{ color: #ffffff; }}
popover.menu modelbutton check, popover.menu modelbutton radio {{ background: none; box-shadow: none; color: inherit; }}
popover.menu separator {{ min-height: 1px; margin: 4px 11px; background-color: @hearth_menu_sep; }}
popover.menu box.inline-buttons button {{ border-radius: 9px; }}
menubar > item {{ border-radius: 6px; padding: 3px 9px; }}
menubar > item:selected {{ background-color: @hearth_hover; box-shadow: none; color: inherit; }}

/* Drop-down lists (GtkDropDown): their popovers are menus too. */
dropdown popover listview > row, combobox popover listview > row {{ min-height: 27px; border-radius: 9px; padding: 0 11px; }}
dropdown popover listview > row:selected, dropdown popover listview > row:hover {{ background-color: @accent_bg_color; color: #ffffff; }}
listview row:selected, list row:selected, columnview row:selected {{ background-color: alpha(@accent_bg_color, 0.35); }}

/* Alerts. */
window.dialog.message .dialog-action-area > button, .message-dialog .response-area > button {{ border-radius: 100px; }}
dialog-host > dialog.alert sheet, window.dialog.message, dialog.alert > sheet, window.alert {{ border-radius: 14px; }}

/* Window corners. */
window.csd, window.csd > decoration {{ border-radius: 14px; }}
""")
    return "".join(out)


# --- GTK 2 -------------------------------------------------------------------

GTK2_MENU = """
# hearth: menu rows highlighted in the accent itself, flat (Adwaita's
# engine shades it darker), as in hearth's and the apps' menus.
style "hearth-menu-item" {
  bg[PRELIGHT] = @selected_bg_color
  bg[SELECTED] = @selected_bg_color
  fg[PRELIGHT] = @selected_fg_color
  text[PRELIGHT] = @selected_fg_color
  engine "pixmap" {}
}
widget_class "*<GtkMenu>*<GtkMenuItem>*" style "hearth-menu-item"
# Taller rows and room around them (MacMenuStyle: 27 px rows, 5 px padding).
style "hearth-menu" {
  xthickness = 5
  ythickness = 5
}
style "hearth-menu-row" {
  xthickness = 6
  ythickness = 5
}
widget_class "*<GtkMenu>" style "hearth-menu"
style "hearth-menu-separator" {
  xthickness = 1
  ythickness = 1
}
widget_class "*<GtkMenu>.<GtkMenuItem>" style "hearth-menu-row"
widget_class "*<GtkMenu>.<GtkSeparatorMenuItem>" style "hearth-menu-separator"
"""


def gtk2_rc(src_rc, mode, accent):
    p = PALETTE[mode]
    scheme = dict(p["gtk2"])
    scheme.update(selected_fg_color="#ffffff", selected_bg_color=accent, link_color=accent,
                  visited_link_color="#a550a7")
    lines = []
    for line in open(src_rc).read().splitlines():
        if line.startswith("gtk-color-scheme"):
            continue
        lines.append(line)
    text = "\n".join(lines)
    colours = "".join(f'gtk-color-scheme = "{k}:{v}"\n' for k, v in scheme.items())
    marker = "# Set GTK settings"
    text = text.replace(marker, "# hearth's palette (shell/Theme.qml)\n" + colours + "\n" + marker, 1)
    return text + "\n" + GTK2_MENU


# --- output ------------------------------------------------------------------

def index_theme(name):
    return f"""[Desktop Entry]
Type=X-GNOME-Metatheme
Name={name}
Comment=hearth's macOS-26-style look for GTK 2, 3 and 4
Encoding=UTF-8

[X-GNOME-Metatheme]
GtkTheme={name}
MetacityTheme={name}
IconTheme={'breeze-dark' if name.endswith('-dark') else 'breeze'}
CursorTheme=Adwaita
ButtonLayout=close,minimize,maximize:
"""


def copytree(src, dst):
    """Copy a (read-only, Nix store) tree as writable files."""
    shutil.copytree(src, dst, copy_function=shutil.copyfile)
    for root, dirs, files in os.walk(dst):
        os.chmod(root, 0o755)
        for x in files:
            os.chmod(os.path.join(root, x), 0o644)


def read(path):
    with open(path) as f:
        return f.read()


def write(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        f.write(text)


def libadwaita_user_css():
    """For ~/.config/gtk-4.0/gtk.css: libadwaita apps never load a theme,
    only this; it follows light/dark live by media query."""
    return ("/* hearth's palette and look for libadwaita (and GTK 4) apps. */\n"
            "@media (prefers-color-scheme: light) {\n" + colors_css("light", indent="  ") + "}\n"
            "@media (prefers-color-scheme: dark) {\n" + colors_css("dark", indent="  ") + "}\n"
            + adw_vars_css() + rules(4))


def generate(adw_gtk3, libadwaita_css, adwaita_gtk2, out):
    adw4 = read(libadwaita_css)
    for name, mode in (("Hearth", "light"), ("Hearth-dark", "dark")):
        d = os.path.join(out, name)
        if os.path.isdir(d):
            shutil.rmtree(d)
        os.makedirs(d)
        write(os.path.join(d, "index.theme"), index_theme(name))
        accent = PALETTE[mode]["accent"]

        # GTK 3
        src3 = os.path.join(adw_gtk3, "adw-gtk3" + ("-dark" if mode == "dark" else ""), "gtk-3.0")
        copytree(os.path.join(src3, "assets"), os.path.join(d, "gtk-3.0", "assets"))
        css3 = lambda m: (read(os.path.join(adw_gtk3, "adw-gtk3" + ("-dark" if m == "dark" else ""), "gtk-3.0", "gtk.css"))
                          + "\n/* ---- hearth palette ---- */\n" + colors_css(m) + rules(3))
        write(os.path.join(d, "gtk-3.0", "gtk.css"), css3(mode))
        write(os.path.join(d, "gtk-3.0", "gtk-dark.css"), css3("dark"))

        # GTK 4
        css4 = lambda m: (adw4 + "\n/* ---- hearth palette ---- */\n" + colors_css(m) + rules(4))
        write(os.path.join(d, "gtk-4.0", "gtk.css"), css4(mode))
        write(os.path.join(d, "gtk-4.0", "gtk-dark.css"), css4("dark"))
        write(os.path.join(d, "gtk-4.0", "libadwaita-user.css"), libadwaita_user_css())

        # GTK 2
        src2 = os.path.join(adwaita_gtk2, "Adwaita" + ("-dark" if mode == "dark" else ""), "gtk-2.0")
        copytree(src2, os.path.join(d, "gtk-2.0"))
        write(os.path.join(d, "gtk-2.0", "gtkrc"), gtk2_rc(os.path.join(src2, "gtkrc"), mode, accent))


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--adw-gtk3", required=True, help="adw-gtk3's share/themes")
    ap.add_argument("--libadwaita-css", required=True, help="libadwaita's styles/gtk.css (from its GResource)")
    ap.add_argument("--adwaita-gtk2", required=True, help="gnome-themes-extra's share/themes")
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    generate(a.adw_gtk3, a.libadwaita_css, a.adwaita_gtk2, a.out)


if __name__ == "__main__":
    main()
