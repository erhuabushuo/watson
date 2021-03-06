---
layout: default
tags: [installation, getting started]
title: Installation
area: Getting Started
---
<section>

All stable versions of Watson are available via [pip](https://pypi.python.org/pypi/pip) and can be installed using the following command `pip install watson-framework` via your CLI of choice.

Watson is maintained at [Github](https://github.com/simoncoulton/watson), and can be used to get the latest development version of the code if required.

#### Setting up a virtualenv
We recommend creating a standalone environment for each new project you work on to isolate any dependencies that it may need. To do so enter the following commands in your terminal:

	pyvenv /where_you_want_to_store_venv
	source /where_you_want_to_store_venv/bin/activate


#### Verifying the installation
To ensure that Watson has been installed correctly, launch `python` from your CLI and then enter the following:

	>>> import watson
	>>> print(watson.__version__)
	# latest watson version will be printed here


Once you've got Watson installed, head on over to the [Your first application]({{ site.baseurl }}/getting-started/your-first-application.html) area to learn how to create your first web application.
</section>
