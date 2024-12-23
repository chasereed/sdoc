
import sdoc


doc = sdoc.Document()

doc.h1('My Report')

block = doc.markdown("""
    ## Section 2

    Lorem ipsum dolor sit amet, consectetur adipiscing elit.
""")

doc.save('test.html')

