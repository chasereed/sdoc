'''
sdoc.py
Tool for making HTML reports in a script

Example:
doc = sdoc.Document()
doc.h1('My Report')
doc.markdown("""    
    ## Section 2

    Lorem ipsum dolor sit amet, consectetur adipiscing elit.
""")
'''

import textwrap
import jinja2
import argparse


def register_block(name, block_cls):
    """Register a block type with Document class and create global function"""
    def add_method(doc, *args, **kwargs):
        return doc.add_block(block_cls(*args, **kwargs))
    
    def global_method(*args, **kwargs):
        return get_current_document().add_block(block_cls(*args, **kwargs))
    
    # Add method to Document class
    setattr(Document, name, add_method)
    
    # Add global function
    return global_method


class Block:
    def __init__(self):
        raise NotImplementedError('Block is an abstract class')
    
    def get_template(self):
        raise NotImplementedError('Block is an abstract class') 
    
    def get_context(self):
        return self.__dict__
        
    def render(self):
        template_str = textwrap.dedent(self.get_template())
        template = jinja2.Template(template_str)
        context = self.get_context()
        return template.render(context)
    
    def pre_add_hook(self, parent):
        pass


class Document(Block):
    THEMES = {
        'default': '''
            body { font-family: system-ui, -apple-system, sans-serif; line-height: 1.5; max-width: 1200px; margin: 0 auto; padding: 2rem; }
            .code { background: #f6f8fa; padding: 1rem; border-radius: 6px; font-family: monospace; }
            .blockquote { border-left: 4px solid #ddd; margin: 0; padding-left: 1rem; color: #666; }
            .row { display: flex; gap: 1rem; margin: 1rem 0; }
            .col { flex: 1; }
            .card { border: 1px solid #ddd; border-radius: 6px; padding: 1rem; margin: 1rem 0; }
            .divider { border: 0; border-top: 1px solid #ddd; margin: 2rem 0; }
            .pandas-table { width: 100%; overflow-x: auto; }
            .pandas-table table { width: 100%; border-collapse: collapse; }
            .pandas-table th, .pandas-table td { border: 1px solid #ddd; padding: 0.5rem; }
            .table { width: 100%; border-collapse: collapse; margin-bottom: 1rem; color: #212529; }
            .table th, .table td { padding: 0.75rem; vertical-align: top; border-top: 1px solid #dee2e6; }
            .table thead th { vertical-align: bottom; border-bottom: 2px solid #dee2e6; }
            .table tbody + tbody { border-top: 2px solid #dee2e6; }
            .table-bordered { border: 1px solid #dee2e6; }
            .table-bordered th, .table-bordered td { border: 1px solid #dee2e6; }
            .table-bordered thead th, .table-bordered thead td { border-bottom-width: 2px; }
            .table-striped tbody tr:nth-of-type(odd) { background-color: rgba(0, 0, 0, 0.05); }
            .table-hover tbody tr:hover { color: #212529; background-color: rgba(0, 0, 0, 0.075); }
            .alert { padding: 1rem; margin: 1rem 0; border-radius: 6px; }
            .alert-info { background-color: #e3f2fd; color: #0c5460; border: 1px solid #bee5eb; }
            .alert-warning { background-color: #fff3cd; color: #856404; border: 1px solid #ffeeba; }
            .alert-error { background-color: #f8d7da; color: #721c24; border: 1px solid #f5c6cb; }
        ''',
        'dark': '''
            body { font-family: system-ui, -apple-system, sans-serif; line-height: 1.5; max-width: 1200px; margin: 0 auto; padding: 2rem; background: #1a1a1a; color: #fff; }
            .code { background: #2d2d2d; padding: 1rem; border-radius: 6px; font-family: monospace; }
            .blockquote { border-left: 4px solid #444; margin: 0; padding-left: 1rem; color: #aaa; }
            .row { display: flex; gap: 1rem; margin: 1rem 0; }
            .col { flex: 1; }
            .card { border: 1px solid #444; border-radius: 6px; padding: 1rem; margin: 1rem 0; }
            .divider { border: 0; border-top: 1px solid #444; margin: 2rem 0; }
            .pandas-table { width: 100%; overflow-x: auto; }
            .pandas-table table { width: 100%; border-collapse: collapse; }
            .pandas-table th, .pandas-table td { border: 1px solid #444; padding: 0.5rem; }
            .table { width: 100%; border-collapse: collapse; margin-bottom: 1rem; color: #fff; }
            .table th, .table td { padding: 0.75rem; vertical-align: top; border-top: 1px solid #444; }
            .table thead th { vertical-align: bottom; border-bottom: 2px solid #444; }
            .table tbody + tbody { border-top: 2px solid #444; }
            .table-bordered { border: 1px solid #444; }
            .table-bordered th, .table-bordered td { border: 1px solid #444; }
            .table-bordered thead th, .table-bordered thead td { border-bottom-width: 2px; }
            .table-striped tbody tr:nth-of-type(odd) { background-color: rgba(255, 255, 255, 0.05); }
            .table-hover tbody tr:hover { color: #fff; background-color: rgba(255, 255, 255, 0.075); }
            .alert { padding: 1rem; margin: 1rem 0; border-radius: 6px; }
            .alert-info { background-color: #1a3f4c; color: #8ed9f6; border: 1px solid #164e63; }
            .alert-warning { background-color: #4c3a10; color: #fcd34d; border: 1px solid #92400e; }
            .alert-error { background-color: #4c1d24; color: #fca5a5; border: 1px solid #991b1b; }
        '''
    }

    def __init__(self, title='My Report', destination=None, autosave=False, theme='default', custom_css=None):
        self.title = title
        self.destination = destination
        self.autosave = autosave
        self.theme = theme
        self.custom_css = custom_css
        self._blocks = []

    def get_context(self):
        return {
            'title': self.title,
            'theme_css': self.THEMES.get(self.theme, self.THEMES['default']),
            'custom_css': self.custom_css or '',
            'blocks': [block.render() for block in self._blocks]
        }
    
    def get_template(self):
        return '''
        <!DOCTYPE html>
        <html>
        <head>
            <title>{{ title }}</title>
            <style>
                {{ theme_css }}
                {{ custom_css }}
            </style>
        </head>
        <body>
            {% for block in blocks %}
                {{ block }}
            {% endfor %}
        </body>
        </html>
        '''
    
    def save(self, destination=None):
        if destination is None:
            destination = self.destination
        if destination is None:
            raise ValueError('No destination provided')
        with open(destination, 'w') as f:
            f.write(self.render())

    def add_block(self, block):
        block.pre_add_hook(self)
        self._blocks.append(block)
        if self.autosave:
            self.save()
        return block

    def pre_add_hook(self, parent):
        # raise Error because this should never be called on a Document
        raise ValueError('Document cannot be added to another block')


class H1(Block):
    def __init__(self, text):
        self.text = text

    def get_template(self):
        return '<h1>{{ text }}</h1>'
    
    def get_styles(self):
        return '''
            h1 {
                margin-top: 0;
                margin-bottom: 0.5em;
                font-weight: 600;
                font-size: 2em;
            }
        '''

class H2(Block):
    def __init__(self, text):
        self.text = text

    def get_template(self):
        return '<h2>{{ text }}</h2>'
    
class H3(Block):
    def __init__(self, text):
        self.text = text

    def get_template(self):
        return '<h3>{{ text }}</h3>'
    
class H4(Block):
    def __init__(self, text):
        self.text = text

    def get_template(self):
        return '<h4>{{ text }}</h4>'

class H5(Block):
    def __init__(self, text):
        self.text = text

    def get_template(self):
        return '<h5>{{ text }}</h5>'

class H6(Block):
    def __init__(self, text):
        self.text = text

    def get_template(self):
        return '<h6>{{ text }}</h6>'


class Paragraph(Block):
    def __init__(self, text):
        self.text = text

    def get_template(self):
        return '<p>{{ text }}</p>'


class Image(Block):
    def __init__(self, src, alt=''):
        self.src = src
        self.alt = alt

    def get_template(self):
        return '<img src="{{ src }}" alt="{{ alt }}" />'


class List(Block):
    def __init__(self, items, ordered=False):
        self.items = items
        self.ordered = ordered

    def get_template(self):
        if self.ordered:
            return '<ol>{% for item in items %}<li>{{ item }}</li>{% endfor %}</ol>'
        else:
            return '<ul>{% for item in items %}<li>{{ item }}</li>{% endfor %}</ul>'


class Markdown(Block):
    def __init__(self, text):
        import mistune
        self.text = textwrap.dedent(text)
        self.html = mistune.markdown(self.text)

    def get_template(self):
        return '{{ html }}'
    

class MplPlot(Block):
    def __init__(self, plot):
        import io
        import base64
        self.plot = plot
        with io.BytesIO() as buf:
            plot.savefig(buf, format='png')
            buf.seek(0)
            self.plot_data = base64.b64encode(buf.getvalue()).decode('utf-8')

    def get_template(self):
        return '<img src="data:image/png;base64,{{ plot }}" />'
    
    def get_context(self):
        return {'plot': self.plot_data}

    
class TOC(Block):
    def __init__(self):
        pass 

    def pre_add_hook(self, parent):
        # check to make sure parent is a Document
        if not isinstance(parent, Document):
            raise ValueError('TOC must be added to a Document')
        self._document_blocks = parent._blocks

    def get_context(self):
        # return list of text and level for each header
        headers = []
        for block in self._document_blocks:
            if isinstance(block, H1):
                headers.append((1, block.text))
            elif isinstance(block, H2):
                headers.append((2, block.text))
            elif isinstance(block, H3):
                headers.append((3, block.text))
        return {'headers': headers}            

    def get_template(self):
        return '''
        <h1>Table of Contents</h1>
        <ul>
            {% for level, text in headers %}
                <li><a href="#{{ text }}">{{ text }}</a></li>
            {% endfor %}
        </ul>
        '''


class Code(Block):
    def __init__(self, code, language=None):
        self.code = code
        self.language = language

    def get_template(self):
        return '<pre class="code"{% if language %} data-language="{{ language }}"{% endif %}>{{ code }}</pre>'


class Blockquote(Block):
    def __init__(self, text):
        self.text = text

    def get_template(self):
        return '<blockquote class="blockquote">{{ text }}</blockquote>'


class Table(Block):
    def __init__(self, data, headers=None, striped=False, bordered=True, hover=False):
        self.data = data
        self.headers = headers
        self.classes = ['table']
        if striped:
            self.classes.append('table-striped')
        if bordered:
            self.classes.append('table-bordered')
        if hover:
            self.classes.append('table-hover')

    def get_template(self):
        return '''
        <table class="{{ ' '.join(classes) }}">
            {% if headers %}
            <thead>
                <tr>
                    {% for header in headers %}
                    <th>{{ header }}</th>
                    {% endfor %}
                </tr>
            </thead>
            {% endif %}
            <tbody>
                {% for row in data %}
                <tr>
                    {% for cell in row %}
                    <td>{{ cell }}</td>
                    {% endfor %}
                </tr>
                {% endfor %}
            </tbody>
        </table>
        '''


class PandasTable(Block):
    def __init__(self, df, index=True, striped=True, bordered=True, hover=True):
        self.html = df.to_html(index=index, classes=['table'] + 
            (['table-striped'] if striped else []) +
            (['table-bordered'] if bordered else []) +
            (['table-hover'] if hover else []))

    def get_template(self):
        return '<div class="pandas-table">{{ html }}</div>'


class Row(Block):
    def __init__(self):
        self._blocks = []

    def add_block(self, block):
        block.pre_add_hook(self)
        self._blocks.append(block)
        return block

    def get_template(self):
        return '''
        <div class="row">
            {% for block in blocks %}
                {{ block }}
            {% endfor %}
        </div>
        '''

    def get_context(self):
        return {'blocks': [block.render() for block in self._blocks]}


class Col(Block):
    def __init__(self):
        self._blocks = []

    def add_block(self, block):
        block.pre_add_hook(self)
        self._blocks.append(block)
        return block

    def get_template(self):
        return '''
        <div class="col">
            {% for block in blocks %}
                {{ block }}
            {% endfor %}
        </div>
        '''

    def get_context(self):
        return {'blocks': [block.render() for block in self._blocks]}


class Card(Block):
    def __init__(self, title=None, content=None):
        self.title = title
        self.content = content
        self._blocks = []

    def add_block(self, block):
        block.pre_add_hook(self)
        self._blocks.append(block)
        return block

    def get_template(self):
        return '''
        <div class="card">
            {% if title %}<h3>{{ title }}</h3>{% endif %}
            {% if content %}{{ content }}{% endif %}
            {% for block in blocks %}
                {{ block }}
            {% endfor %}
        </div>
        '''

    def get_context(self):
        return {
            'title': self.title,
            'content': self.content,
            'blocks': [block.render() for block in self._blocks]
        }


class Divider(Block):
    def __init__(self):
        pass

    def get_template(self):
        return '<hr class="divider">'


class Info(Block):
    def __init__(self, content):
        self.content = content

    def get_template(self):
        return '<div class="alert alert-info">{{ content }}</div>'


class Warning(Block):
    def __init__(self, content):
        self.content = content

    def get_template(self):
        return '<div class="alert alert-warning">{{ content }}</div>'


class Error(Block):
    def __init__(self, content):
        self.content = content

    def get_template(self):
        return '<div class="alert alert-error">{{ content }}</div>'


# -------------------------------------------------------------------------------------------------

_current_document = None

def set_current_document(document):
    global _current_document
    _current_document = document


def get_current_document():
    if _current_document is None:
        set_current_document(Document())
    return _current_document


def save(*args, **kwargs):
    get_current_document().save(*args, **kwargs)

def cli():
    parser = argparse.ArgumentParser(description='SDoc - Tool for making HTML reports in a script')
    parser.add_argument('command', choices=['generate-test-doc'], help='Command to execute')
    parser.add_argument('destination', nargs='?', default='sdoc_test_report.html', 
                      help='Destination file for the generated document (default: sdoc_test_report.html)')
    
    args = parser.parse_args()
    
    if args.command == 'generate-test-doc':
        generate_test_doc(args.destination)
        print(f'Test document generated at: {args.destination}')

def generate_test_doc(destination='test_report.html'):
    """Generate a test document showcasing all available block types."""    
    doc = Document(title='SDoc Test Document', destination=destination)

    doc.toc()
    
    # Basic blocks
    doc.h1('SDoc Test Document')
    doc.paragraph('This document demonstrates all available block types in SDoc.')
    
    # Headers
    doc.h2('Headers')
    doc.h3('Header Level 3')
    doc.h4('Header Level 4')
    doc.h5('Header Level 5')
    doc.h6('Header Level 6')
    
    # Text blocks
    doc.h2('Text Blocks')
    doc.paragraph('This is a paragraph block with regular text.')
    doc.markdown('''
    This is a **markdown** block that supports:
    - Bold text
    - *Italic text*
    - Lists
    - And more...
    ''')
    
    # Code
    doc.h2('Code Block')
    doc.code('''
def hello_world():
    print("Hello from SDoc!")
    ''', language='python')
    
    # Lists
    doc.h2('Lists')
    doc.list(['Unordered list item 1', 'Unordered list item 2', 'Unordered list item 3'])
    doc.list(['Ordered list item 1', 'Ordered list item 2', 'Ordered list item 3'], ordered=True)
    
    # Quotes
    doc.h2('Blockquote')
    doc.blockquote('This is a blockquote demonstrating quoted text in SDoc.')
    
    # Tables
    doc.h2('Tables')
    
    # Default table
    doc.h3('Default Table')
    doc.table(
        headers=['Name', 'Age', 'City'],
        data=[
            ['Alice', 25, 'New York'],
            ['Bob', 30, 'San Francisco'],
            ['Charlie', 35, 'Chicago']
        ]
    )
    
    # Striped table
    doc.h3('Striped Table')
    doc.table(
        headers=['Name', 'Age', 'City'],
        data=[
            ['Alice', 25, 'New York'],
            ['Bob', 30, 'San Francisco'],
            ['Charlie', 35, 'Chicago']
        ],
        striped=True
    )
    
    # Bordered table with hover
    doc.h3('Bordered Table with Hover')
    doc.table(
        headers=['Name', 'Age', 'City'],
        data=[
            ['Alice', 25, 'New York'],
            ['Bob', 30, 'San Francisco'],
            ['Charlie', 35, 'Chicago']
        ],
        bordered=True,
        hover=True
    )
    
    # Full featured table
    doc.h3('Full Featured Table (Striped + Bordered + Hover)')
    doc.table(
        headers=['Name', 'Age', 'City'],
        data=[
            ['Alice', 25, 'New York'],
            ['Bob', 30, 'San Francisco'],
            ['Charlie', 35, 'Chicago']
        ],
        striped=True,
        bordered=True,
        hover=True
    )

    # Pandas table
    try:
        import pandas 
        doc.h2('Pandas Table')
        df = pandas.DataFrame({
            'A': [1, 2, 3],
            'B': ['a', 'b', 'c'],
            'C': [True, False, True]
        })
        doc.pandas_table(df)
    except ImportError:
        print('pandas not installed - skipping pandas table example')
        doc.warning('pandas not installed - skipping pandas table example')
    
    # Alerts
    doc.h2('Alerts')
    doc.info('This is an info alert')
    doc.warning('This is a warning alert')
    doc.error('This is an error alert')
    
    # Card
    doc.h2('Card')
    card = doc.card(title='Example Card')
    card.add_block(Paragraph('This is content inside a card.'))
    
    # Layout
    doc.h2('Layout')
    row = doc.row()
    col1 = row.add_block(Col())
    col1.add_block(Paragraph('Column 1'))
    col2 = row.add_block(Col())
    col2.add_block(Paragraph('Column 2'))
    
    # Divider
    doc.divider()
    
    # Plot (if matplotlib is available)
    try:
        import numpy as np
        import matplotlib.pyplot as plt
        doc.h2('Matplotlib Plot')
        fig, ax = plt.subplots()
        x = np.linspace(0, 10, 100)
        ax.plot(x, np.sin(x))
        doc.mplplot(plt)
        plt.close()
    except ImportError:
        print('numpy/matplotlib not installed - skipping plot example')
        doc.warning('numpy/matplotlib not installed - skipping plot example')
    
    doc.save()
    return doc

# Built-in blocks ---------------------------------------------------------------------------------

h1 = register_block('h1', H1)
h2 = register_block('h2', H2)
h3 = register_block('h3', H3)
h4 = register_block('h4', H4)
h5 = register_block('h5', H5)
h6 = register_block('h6', H6)
paragraph = register_block('paragraph', Paragraph)
image = register_block('image', Image)
list = register_block('list', List)
markdown = register_block('markdown', Markdown)
mplplot = register_block('mplplot', MplPlot)
code = register_block('code', Code)
blockquote = register_block('blockquote', Blockquote)
table = register_block('table', Table)
pandas_table = register_block('pandas_table', PandasTable)
row = register_block('row', Row)
col = register_block('col', Col)
card = register_block('card', Card)
divider = register_block('divider', Divider)
info = register_block('info', Info)
warning = register_block('warning', Warning)
error = register_block('error', Error)
toc = register_block('toc', TOC)


if __name__ == '__main__':
    cli()



