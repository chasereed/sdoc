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

import collections
import textwrap
import uuid 
import jinja2
import mistune



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
    
    def add_hook(self, parent):
        pass



class Document(Block):
    def __init__(self, title='My Report', destination=None, autosave=False):
        self.title = title
        self.destination = destination
        self.autosave = autosave
        self._blocks = []

    def get_context(self):
        return {
            'title': self.title,
            'blocks': [block.render() for block in self._blocks]
        }
    
    def get_template(self):
        return '''
        <!DOCTYPE html>
        <html>
        <head>
            <title>{{ title }}</title>
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
        block.add_hook(self)
        self._blocks.append(block)
        if self.autosave:
            self.save()
        return block

    def add_hook(self, parent):
        # raise Error because this should never be called on a Document
        raise ValueError('Document cannot be added to another block')

    def h1(self, text):
        return self.add_block(H1(text))

    def h2(self, text):
        return self.add_block(H2(text))

    def h3(self, text):
        return self.add_block(H3(text))

    def markdown(self, text):
        return self.add_block(Markdown(text)) 
    
    def mplplot(self, *args, **kwargs):
        return self.add_block(MplPlot(*args, **kwargs))


class H1(Block):
    def __init__(self, text):
        self.text = text

    def get_template(self):
        return '<h1>{{ text }}</h1>'
    

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
    

class Markdown(Block):
    def __init__(self, text):
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

    def add_hook(self, parent):
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
    

# Global API --------------------------------------------------------------------------------------

# Example usage:
# import sdoc
# sdoc.h1('My Report')
# sdoc.save('report.html')

_current_document = None

def set_current_document(document):
    global _current_document
    _current_document = document

def get_current_document():
    if _current_document is None:
        set_current_document(Document())
    return _current_document

def h1(*args, **kwargs):
    get_current_document().h1(*args, **kwargs)

def h2(*args, **kwargs):
    get_current_document().h2(*args, **kwargs)

def h3(*args, **kwargs):
    get_current_document().h3(*args, **kwargs)

def mplplot(*args, **kwargs):
    get_current_document().mplplot(*args, **kwargs)

def markdown(*args, **kwargs):
    get_current_document().markdown(*args, **kwargs)




        