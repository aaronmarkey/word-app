# To-Do

## Word Details Screen
- [x] Every non-UI word on the details page is clickable.
- [x] Sidebar
  - [x] Buttons go to the relevant word information. "Definitions",
        "Thesaurus", etc.
  - [x] Vertical scrolling.
  - [x] Subclass Button to style properly based on section type.
- [ ] Sections
  - [x] Collapsible sections
  - [x] Section keybindings - Numbers, 1 through 9, by order of section, number
        always same for section.
  - [ ] Sections are disabled, collapsed, and moved to the bottom of the
        screen if section is empty.
  - [ ] WordDetail providers.
### Keybindings
- [x] Section keybindings - Numbers, 1 through 9, by order of section,
      number always same for section.


## Quick Search Modal
- [x] Modal interface
  - [x] CSS
  - [x] Design
  - [x] Initialize with runtime dependencies
  - [x] Real search providers
  - [x] Clean up code in DatamuseSearchProvider and DatamuseClient classes
  - [x] Add (?) hover for help tooltip.
  - [x] Result caching on search palette
- [x] Faker Provider


## Misc
- [ ] General project clean up.
  - [ ] Reorg code to better directory structure.
  - [x] Ruff config: check import order.
  - [ ] Document things.
  - [x] i18n
- [x] Rethink session/cmd-line conf differences.
- [x] Replace theme variables with "interace-color" and "hover-color"
- [x] Defaults in UserConf class.
- [x] Dep injection
  - [x] Word Detail Providers
  - [x] Suggestion Providers
