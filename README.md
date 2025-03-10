# sdoc

## Introduction

`sdoc` is a Python library for creating quick HTML reports from data science scripts. It provides a simple API to add various HTML elements such as headers, paragraphs, images, lists, markdown, and matplotlib plots to a document and save it as an HTML file.

## Installation

To install `sdoc`, you can use pip:

```bash
pip install sdoc
```

## Usage Examples

### Creating a Simple Report

```python
import sdoc

doc = sdoc.Document()
doc.h1('My Report')
doc.markdown('## Section 2\nLorem ipsum dolor sit amet, consectetur adipiscing elit.')
doc.paragraph('This is a paragraph.')
doc.image('image.png', 'An image')
doc.list(['Item 1', 'Item 2', 'Item 3'])
doc.save('report.html')
```

### Adding a Matplotlib Plot

```python
import sdoc
import matplotlib.pyplot as plt

doc = sdoc.Document()
doc.h1('My Report')
plt.plot([0, 1], [0, 1])
doc.mplplot(plt)
doc.save('report_with_plot.html')
```

## API Reference

### Document Class

- `Document(title='My Report', destination=None, autosave=False)`
- `h1(text)`
- `h2(text)`
- `h3(text)`
- `h4(text)`
- `h5(text)`
- `h6(text)`
- `paragraph(text)`
- `image(src, alt='')`
- `list(items, ordered=False)`
- `markdown(text)`
- `mplplot(plot)`
- `save(destination=None)`

### Block Classes

- `H1(text)`
- `H2(text)`
- `H3(text)`
- `H4(text)`
- `H5(text)`
- `H6(text)`
- `Paragraph(text)`
- `Image(src, alt='')`
- `List(items, ordered=False)`
- `Markdown(text)`
- `MplPlot(plot)`

## License

This project is licensed under the MIT License.