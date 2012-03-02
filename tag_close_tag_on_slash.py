import sublime, sublime_plugin, re

valid_tag = re.compile("^[a-z0-9\:-]+$", re.I);

self_closing_tags = re.compile("^\?xml|\!|area|base|br|col|frame|hr|img|input|link|meta|param|command|embed|source", re.I)


class TagCloseTagOnSlashCommand(sublime_plugin.TextCommand):

	def run(self, edit):

		view = self.view

		closed_some_tag = False
		new_selections = []

		for region in view.sel():
			cursorPosition = region.begin()
			previousCharacter = view.substr(sublime.Region(cursorPosition - 1, cursorPosition))

			if '<' == previousCharacter:
				closed_some_tag = True
				tag = self.close_tag(view.substr(sublime.Region(0, cursorPosition)))
				view.insert(edit, cursorPosition, tag);
				new_selections.append(sublime.Region(region.end()+len(tag), region.end()+len(tag)))
			else:
				if region.empty():
					view.insert(edit, cursorPosition, '/');
				else:
					view.replace(edit, sublime.Region(region.begin(), region.end()), '/');
				new_selections.append(sublime.Region(region.end(), region.end()))

		# hide the autocomplete popup
		if closed_some_tag and view.window():
			view.window().show_input_panel("boo!", '', '', None, None)
			view.window().run_command('hide_panel');

		# re-add selections
		view.sel().clear()
		for sel in new_selections:
			view.sel().add(sel)

	def close_tag(self, data):

		data = data.split('<')
		data.reverse()
		data.pop(0);

		try:
			i = 0
			lenght = len(data)-1
			while i < lenght:
				maybe_tag = self.tag_name(data[i])
				# if opening tag, close the tag
				if maybe_tag and not self.tag_is_closing(data[i]):
					return '/'+self.tag_name(data[i])+'>'
				# if closing tag, jump to opening tag
				else:
					if maybe_tag:
						i = i+1
						while i < lenght:
							if self.tag_name(data[i]) == maybe_tag and not self.tag_is_closing(data[i]):
								break
							i = i+1
				i = i+1
			return '/'
		except:
			return '/';

	def tag_name(self, content):

		if content[:1] == '/':
			tag_name = content.split('/')[1].split('>')[0];
		else:
			tag_name = content.split(' ')[0].split('>')[0];

		if valid_tag.match(tag_name) and not self_closing_tags.match(tag_name):
			return tag_name
		else:
			return ''

	def tag_is_closing(self, content):

		if content[:1] == '/':
			return True
		else:
			return False