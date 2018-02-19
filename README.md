# jpg2latex
![jpg2latex](https://github.com/droudy/jpg2latex/blob/master/README_img.png "jpg2latex")

jpg2latex is a python library created for easily converting images of compiled latex equations into latex source. 

---

### Motivation
This project was born out of my annoyance with typing up the latex source for already compiled latex when taking notes from a calculus textbook

### Requirements
* Python 2.7
* [Python Imaging Library (PIL)](http://www.pythonware.com/products/pil/)
* [Numpy](http://www.numpy.org/)
* [SciPy](https://www.scipy.org/)

### Code example
```python
from image_to_latex import image_to_latex

print image_to_latex('path_to_image')
```

### Limitations
jpg2latex is very much a work in progress and lacks support for many latex symbols/characters and mathematical operations. As of now it supports the following operators:
* Addition
* Subtraction
* Multiplication 
* Division
* Square roots
* Indefinite integrals
