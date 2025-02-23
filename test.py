
import sdoc
import matplotlib.pyplot as plt

doc = sdoc.Document()

doc.h1('My Report')

# Markdown
doc.markdown("""
    ## Section 2

    Lorem ipsum dolor sit amet, consectetur adipiscing elit.
""")


# Matplotlib Plot
plt.plot([0, 1], [0, 1])
doc.mplplot(plt)

# Save to file
output_file = 'test.html'
doc.save(output_file)
print(f'Saved to {output_file}')

