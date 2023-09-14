:orphan:

# `Typing`

These classes serve as placeholders for type requirements.


```{py:class} NUM(Literal[float, int])
```

```{py:class} FLOAT(Literal['left', 'right', 'top', 'bottom'])
```

```{py:class} TIME(Union[datetime, pd.Timestamp, str])
```

```{py:class} COLOR(str)
Throughout the library, colors should be given as either rgb (`rgb(100, 100, 100)`), rgba(`rgba(100, 100, 100, 0.7)`), hex(`#32a852`) or a html literal(`blue`, `red` etc).
```

```{py:class} LINE_STYLE(Literal['solid', 'dotted', 'dashed', 'large_dashed', 'sparse_dotted'])
```

```{py:class} MARKER_POSITION(Literal['above', 'below', 'inside'])
```

```{py:class} MARKER_SHAPE(Literal['arrow_up', 'arrow_down', 'circle', 'square'])
```

```{py:class} CROSSHAIR_MODE(Literal['normal', 'magnet'])
```

```{py:class} PRICE_SCALE_MODE(Literal['normal', 'logarithmic', 'percentage', 'index100'])
```

```{py:class} ALIGN(Literal['left', 'right'])
```








