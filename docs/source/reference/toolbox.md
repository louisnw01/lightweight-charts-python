# `ToolBox`

`````{py:class} ToolBox

The Toolbox allows for trendlines, ray lines and horizontal lines to be drawn and edited directly on the chart.

It can be used within any Chart object, and is enabled by setting the `toolbox` parameter to `True` upon Chart declaration.

The following hotkeys can also be used when the Toolbox is enabled:

| Key Cmd            | Action  |
|---                 |---        |
| `alt T`             |  Trendline |
| `alt H`           |  Horizontal Line |
| `alt R`             |  Ray Line  |
| `⌘ Z` or `ctrl Z`  |  Undo |

Right-clicking on a drawing will open a context menu, allowing for color selection, style selection and deletion.
___



````{py:method} save_drawings_under(widget: Widget)

Saves drawings under a specific `topbar` text widget. For example:

```python
chart.toolbox.save_drawings_under(chart.topbar['symbol'])
```

````
___



```{py:method} load_drawings(tag: str)

Loads and displays drawings stored under the tag given.
```
___



```{py:method} import_drawings(file_path: str)

Imports the drawings stored at the JSON file given in `file_path`.

```
___



```{py:method} export_drawings(file_path: str)

Exports all currently saved drawings to the JSON file given in `file_path`.

```

`````



