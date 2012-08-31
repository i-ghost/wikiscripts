#!/usr/bin/env python
# -*- coding: utf-8 -*-
from redirectupdater import redirectupdater
import sys
from wikiConf import wikis

'''
An example file showing usage of the redirectUpdater class
'''

for i in wikis:
	print("Running redirectupdater for wiki: %s") % (i)
	x = redirectupdater.redirectUpdater(wikis[i]["wikiAPI"], user=wikis[i]["wikiUser"], password=wikis[i]["wikiPass"], verbosity=True)
	try:
		x.run()
	except redirectupdater.redirectUpdaterError, e:
		sys.exit(e)