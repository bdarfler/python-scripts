#!/usr/bin/env python

from __future__ import with_statement

import os, sys, re, csv
from itertools import dropwhile, takewhile
    
if len(sys.argv) is 3:
    input_dir = sys.argv[1]
    output_dir = sys.argv[2]
else:
    print('You must specify an input directory of html files and an output directory of csv files')
    sys.exit(2)

for file in os.listdir(input_dir):
    
    if 'html' not in file: continue
    
    with open(input_dir+'/'+file) as f:
        page = f.read()
    
    matches = re.findall('<h2 align="center">(.*?)</h2>', page)
    if len(matches) is 2:
        (field, pool) = matches[1].split('-', 1)
        prefix = [field, pool]
    else:
        print('Could not find the field and pool name in file:'+file)
        sys.exit(1)
        
    with open(output_dir+'/'+field.replace('/','_')+'-'+pool.replace('/','_')+'.csv', 'wb') as f:  
        w = csv.writer(f,dialect='excel')
        for line in takewhile(lambda y: '&nbsp;' not in y, dropwhile(lambda x: '<td nowrap="" align="right">' not in x, page.split(os.linesep))):
            parts = re.findall('<td.*?>(.*?)</td>',line)    
            w.writerow(prefix + parts)
    