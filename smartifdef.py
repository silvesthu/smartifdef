# -*- coding: utf-8 -*-
import sublime, sublime_plugin
from collections import deque

class SmartIfDefCommand(sublime_plugin.TextCommand):

    def __init__(self, *args, **kwargs):
        super(SmartIfDefCommand, self).__init__(*args, **kwargs)

    def run(self, edit):
        macros = set(sublime.load_settings('smartifdef.sublime-settings').get('macros'))
        macro = None

        scopes = deque()
        regions = []

        MACRO = 0
        LINE = 1
        ENABLED = 2

        line_count = self.view.rowcol(self.view.size())[0] + 1
        for l in range(line_count):
            line_point = self.view.text_point(l, 0)
            line_region = self.view.line(line_point)
            line = self.view.substr(line_region)

            if line.startswith("#ifdef"):
                macro = line.split()[1]
                enabled = macro in macros
                if len(scopes) != 0 and not scopes[-1][2]:
                    enabled = False
                scopes.append((macro, l + 1, enabled))

                pass

            if line.startswith("#ifndef"):
                macro = line.split()[1]
                enabled = macro not in macros
                if len(scopes) != 0 and not scopes[-1][2]:
                    enabled = False
                scopes.append((macro, l + 1, enabled))

                pass

            if line.startswith("#else"):
                if not scopes[-1][ENABLED]:
                    region_first_line = scopes[-1][LINE]
                    region_last_line = l - 1
                    region_begin = self.view.line(self.view.text_point(region_first_line, 0)).a
                    region_end = self.view.line(self.view.text_point(region_last_line, 0)).b
                    regions.append(sublime.Region(region_begin, region_end))

                scope = (scopes[-1][MACRO], l + 1, not scopes[-1][ENABLED])
                scopes.pop()
                scopes.append(scope)

                pass

            if line.startswith("#endif"):
                if not scopes[-1][ENABLED]:
                    region_first_line = scopes[-1][LINE]
                    region_last_line = l - 1
                    region_begin = self.view.line(self.view.text_point(region_first_line, 0)).a
                    region_end = self.view.line(self.view.text_point(region_last_line, 0)).b
                    regions.append(sublime.Region(region_begin, region_end))

                scopes.pop()

                pass

            if line.startswith("#define"):
                macro = line.split()[1]
                macros.add(macro)
                pass

            if line.startswith("#undef"):
                macro = line.split()[1]
                macros.remove(macro)
                pass

            # print(line)
            # print(scopes)
            # print(regions)

        print(macros)

        self.view.add_regions('ifdef', regions, 'comment', '', sublime.DRAW_NO_OUTLINE)

class TriggerIfdefEvent(sublime_plugin.EventListener):
        def on_post_save(self, view):
            view.run_command('smart_if_def')
