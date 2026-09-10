# Reusable Arial on Linux

Use $XDG_DATA_HOME/fonts/nature-figure, falling back to ~/.local/share/fonts/nature-figure. This is persistent per-user storage, not /tmp, and requires no sudo. Check the current host first; installation on a Mac does not establish availability on a Linux server or inside a container.

Run scripts/ensure_arial.py with the rendering Python environment (requires matplotlib). Without --source it only discovers and registers installed Arial. It checks real family/style metadata, requiring distinct regular and bold faces rather than accepting a Fontconfig alias or nearest-weight fallback.

If Arial is absent and an identified local source is licensed for installation on this host, automatically use --source /absolute/authorized-font-directory. The helper installs only actual Arial TTF/OTF files under hash-based filenames, reuses existing copies, and refreshes fontconfig when available. No arbitrary download or transfer from another host is performed. Preserve the font provider's license outside the figure deliverable; do not bundle proprietary font binaries in the skill or output ZIP.

If there is no usable local source, identify an appropriate distribution-supported Microsoft core-font installer or licensed provider, inspect its origin and terms, and explain what is needed. Windows/macOS installation alone is not evidence of permission to copy that font to a server. Do not claim that automated download is implemented by this helper. A download adapter should only be added after a reusable permitted source and its verification method are established. Never silently use Liberation Sans or another alias as Arial.

In each actual Matplotlib rendering process, import and call ensure_arial(), or register the resolved files using font_manager.fontManager.addfont(path). Check status before selecting Arial. A successful registration in a separate shell command does not carry into a different process. Other renderers must be checked independently with their actual font resolver and exported result. For containers, mount the reusable directory into the container and register those mounted files; host font caches do not guarantee container availability. Figma font access remains separate from Linux plotting.

Verified sources, 2026-09-10:
- Fontconfig user configuration and XDG paths: https://fontconfig.pages.freedesktop.org/fontconfig/fontconfig-user.html
- Microsoft font redistribution FAQ (specifically Windows-supplied fonts, not a universal license for every Arial distribution): https://learn.microsoft.com/en-us/typography/fonts/font-faq
- Matplotlib addfont persistence: https://matplotlib.org/stable/api/font_manager_api.html
