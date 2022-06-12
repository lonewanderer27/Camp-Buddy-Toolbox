import PySimpleGUI as sg
from tools import center, resource_path, todays_date, open_url

title = 'Camp Buddy Toolbox'
description = 'Camp Buddy Toolbox allows you to extract assets and dialogs of Camp Buddy easily!'
short_description = 'Allows you to extract assets and dialogs of Camp Buddy easily!'
version_num = '0.3 Alpha'
github_username = 'lonewanderer27'
my_github_link = 'https://github.com/lonewanderer27'
nickname = 'Jay'
license_notice = f'''{title} is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

{title} is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with {title}.  If not, see <http://www.gnu.org/licenses>'''

sg.theme('DarkBrown3')

def get_about_window():
    about_tab = [
        center([sg.Image(resource_path('icon.png'))]),
        center([sg.Text(text=title)]),
        center([sg.Text(text=version_num)]),
        center([sg.Text(text=f'PySimpleGUI: {sg.version}')]),
        center([sg.Text(text=short_description)]),
        center([sg.Text(text=f'Copyright © {todays_date.year} {github_username} ({nickname})')]),
        center([sg.Text(text='This program comes with absolutely no warranty.\nSee the GNU General Public License 3 for details.'
        )])
    ]

    left_credits_column = [
        [sg.Text('Created by:')],
        [sg.Text('Artwork by:\n')],
        [sg.Text('Used Libraries:\n\n\n')]
    ]

    right_credits_column = [
        [sg.Text(f'{github_username} ({nickname})')],
        [sg.Text(f'Font Awesome\n{github_username} ({nickname})')],
        [sg.Text('unrpa\nrpatool\nPySimpleGUI')]
    ]

    credits_tab = [
        center([sg.Image(resource_path('icon.png'))]),
        center([sg.Text(title)]),
        center([sg.vtop(sg.Column(left_credits_column, element_justification='right')), sg.vtop(sg.Column(right_credits_column))])
    ]

    license_tab = [
        center([sg.Image(resource_path('icon.png'))]),
        center([sg.Text(title)]),
        center([sg.Multiline(default_text=license_notice,justification='center', disabled=True, size=(50,8))])
    ]

    about_window_layout = [
        [sg.TabGroup([
            [sg.Tab(title='About', layout=about_tab), sg.Tab(title='Credits', layout=credits_tab), sg.Tab(title='License', layout=license_tab)]
        ], tab_location='top')]
    ]

    return sg.Window(title=f'About {title}', layout=about_window_layout, icon='icon.png', finalize=True)

def about():
    about_window = get_about_window()