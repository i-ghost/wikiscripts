#!/usr/bin/env python
# -*- coding: utf-8 -*-
import wikitools, calendar
from hashlib import md5
from time import sleep

'''
Redirect Updater Class
To update the lastpatch redirects on Team Fortress Wiki, but could probably be deployed on The Portal Wiki/Dota 2 Wiki
i-ghost
'''
			
class redirectUpdaterError(Exception):
	pass
		
class redirectUpdater(object):
	def __init__(self, wiki, updateTemplateName="Template:Updates", pageName="Lastpatch", betaPageName="Lastpatchbeta", user=False, password=False, rate=False, verbosity=False):
		self.user = user
		self.password = password
		self.rate = rate
		self.wiki = wikitools.wiki.Wiki(wiki)
		self.verbosity = verbosity
		self.pageName = pageName
		self.betaPageName = betaPageName
		self.updateTemplateName = updateTemplateName
		self.page = wikitools.page.Page(self.wiki, pageName, followRedir=False)
		self.betaPage = wikitools.page.Page(self.wiki, betaPageName, followRedir=False)
		self.pageText = wikitools.page.Page(self.wiki, pageName, followRedir=False).getWikiText()
		self.betaPageText = wikitools.page.Page(self.wiki, betaPageName, followRedir=False).getWikiText()
		self.updateTemplateText = wikitools.page.Page(self.wiki, self.updateTemplateName).getWikiText().split("\n")
		self.langs = ["ru", "fr", "de", "pl", "pt-br", "fi", "es", "nl", "zh-hans", "zh-hant", "ar", "cs", "da", "hu", "it", "ja", "ko", "no", "pt", "ro", "sv", "tr"]
		self._get_dates()
		self.patch = "%s %s, %s" % (calendar.month_name[int(self.updates["patch-month"])], self.updates["patch-day"], self.updates["patch-year"])
		self.betaPatch = "%s %s, %s" % (calendar.month_name[int(self.updates["patch-beta-month"])], self.updates["patch-beta-day"], self.updates["patch-beta-year"])
		self.footer = "<!-- This page is automatically generated when %s is modifed. Do not modify this page. -->" % (self.updateTemplateName)
		
	def _get_dates(self):
		"""Internal: Gets dates from update template and stores in dictionary"""
		self.updates = {}
		for i in self.updateTemplateText:
			if i.find("|") == 0:
				# Liable to break
				self.updates[i.lstrip("|").replace(" ", "").partition("=")[0]] = i.replace(" ", "").partition("=")[2].replace("<!--Don'tforgettoupdateme!-->", "")
				
	def _md5sum(self, i):
		"""Internal: Return MD5 digest"""
		return md5(i).hexdigest()
			
	def make_edit_strings(self, beta=False, lang=False):
		"""Creates the final page content."""
		if beta and lang:
			self.redirect_string = "#REDIRECT [[%s Patch (Beta)/%s]]" % (self.betaPatch, lang)
			self.summary_string = "Updated [[%s/%s]] redirect to [[%s Patch (Beta)/%s]]" % (self.betaPageName, lang, self.betaPatch, lang)
		elif beta and not lang:
			self.redirect_string = "#REDIRECT [[%s Patch (Beta)]]" % (self.betaPatch)
			self.summary_string = "Updated [[%s]] redirect to [[%s Patch (Beta)]]" % (self.betaPageName, self.betaPatch)
			
		if lang and not beta:
			self.redirect_string = "#REDIRECT [[%s Patch/%s]]" % (self.patch, lang)
			self.summary_string = "Updated [[%s/%s]] redirect to [[%s Patch/%s]]" % (self.pageName, lang, self.patch, lang)
		elif not lang and not beta:
			self.redirect_string = "#REDIRECT [[%s Patch]]" % (self.patch)
			self.summary_string = "Updated [[%s]] redirect to [[%s Patch]]" % (self.pageName, self.patch)
		
	def _update_redirect(self, beta=False, lang=False):
		"""Internal: Provides editing functionality"""
		self.make_edit_strings(beta, lang)
		# Use the correct page
		if beta:
			if lang:
				_pagetoedit = wikitools.page.Page(self.wiki, "%s/%s" % (self.betaPageName, lang), followRedir=False)
			else:
				_pagetoedit = self.betaPage
		else:
			if lang:
				_pagetoedit = wikitools.page.Page(self.wiki, "%s/%s" % (self.pageName, lang), followRedir=False)
			else:
				_pagetoedit = self.page
		# Verbosity
		if self.verbosity:
			if lang:
				if beta:    _print_string = "%s/%s" % (self.betaPageName, lang);
				else:    _print_string = "%s/%s" % (self.pageName, lang);
			else:
				if beta:    _print_string = "%s" % (self.betaPageName);
				else:    _print_string = "%s" % (self.pageName);
		# Send the edit
		try:
			_pagetoedit.edit(bot=True, minor=True, text="%s\n%s" % (self.redirect_string, self.footer), summary=self.summary_string, md5=self._md5sum(self.redirect_string), token=_pagetoedit.getToken("edit"))
			if self.verbosity:    print("Updated: %s") % (_print_string);
			sleep(self.rate)
		except:
				print("Warning: Couldn't edit %s") % (_print_string)
			
	def check_if_update_needed(self, beta=False):
		"""Checks if redirects needs updating"""
		try:
			if beta:
				if self.betaPageText.split("[[")[1].partition("]]")[0].rstrip("Patch (Beta)") != self.betaPatch:    return True
			else:
				if self.pageText.split("[[")[1].partition("]]")[0].rstrip(" Patch") != self.patch:    return True
		except IndexError:
			return True # Just update anyway
			
	def update(self, beta=False):
		"""Updates the redirects and their lang pages"""
		if beta:
			self._update_redirect(beta=True)
			for lang in self.langs:
				self._update_redirect(beta=True, lang=lang)
		else:
			self._update_redirect()
			for lang in self.langs:
				self._update_redirect(lang=lang)
			
			
	def run(self):
		"""Runs everything"""
		try:
			self.wiki.login(self.user, self.password)
		except:
			raise redirectUpdaterError("Couldn't login")
		# Beta
		if self.check_if_update_needed(beta=True):
			if self.verbosity:    print ("%s: Update required: %s Patch (Beta)") % (self.betaPageName, self.betaPatch)
			self.update(beta=True)
		else:
			if self.verbosity:    print("%s: Nothing to do") % (self.betaPageName);
		# Normal
		if self.check_if_update_needed():
			if self.verbosity:    print ("%s: Update required: %s Patch") % (self.pageName, self.patch)
			self.update()
		else:
			if self.verbosity:    print("%s: Nothing to do") % (self.pageName);
		