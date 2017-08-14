#!/bin/bash

py2app --make-setup SimplePass.py
python setup.py py2app
