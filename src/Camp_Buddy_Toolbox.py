import os
import PySimpleGUI as sg
from functools import reduce
import operator
import re
from cb_dialog_extractor import CBDialogExtractor
from unrpa import UnRPA
from tools import *
from about import *

if sg.running_windows():
    from ctypes import windll
    windll.shcore.SetProcessDpiAwareness(1) # FIXES BLURRINESS IF THE PROGRAM IS RUNNING ON WINDOWS PC WITH HIGH DPI DISPLAY

current_directory = os.getcwd
debug_mode = False
sg.theme('DarkBrown3')

# UnRPA Settings
verbosity = 2

def list_rpa_files_2(rpafile: str) -> list:
    unrpa = UnRPA(filename=rpafile, verbosity=2)
    files_list = sorted(unrpa.list_files())
    return files_list

def popup_long_operation_finished(title, message):
    sg.popup(message, title=title, grab_anywhere=True, keep_on_top=True, non_blocking=True)

def operation_done_popup(title: str, message: str, dest_folder: str):
    operation_done_popup_layout = [
        [sg.Text(message)],
        center([sg.Button('OK', key='-OK-'), sg.Button('Open Folder', key='-open_dest_folder-', metadata=dest_folder)])
    ]
    return sg.Window(
        title=title,
        layout=operation_done_popup_layout,
        grab_anywhere=True,
        keep_on_top=True,
        text_justification='center'
    )

def ed_operation_done_popup(
    title: str, 
    message: str, 
    open_folder_key: str,
    export_to_file: bool = True,
    dest_folder: str = None, 
    dest_file: str = None):
    
    if export_to_file:
        button = sg.Button('Open File', key='-open_dest_file-', metadata=dest_file)
    else:
        button = sg.Button('Open Folder', key='-open_dest_folder-', metadata=dest_folder)


    operation_done_popup_layout = [
        [sg.Text(message)],
        center([sg.Button('OK', key='-OK-'), button])
    ]
    return sg.Window(
        title=title,
        layout=operation_done_popup_layout,
        grab_anywhere=True,
        keep_on_top=True,
        text_justification='center'
    )

def get_main_window():

    cb_chars = [
        [sg.VPush()],
        [sg.Checkbox("Yuri", key='cb-yu-'), sg.Push(), sg.Checkbox("Hunter", key='cb-hu-'), sg.Push(),
        sg.Checkbox("Taiga", key='cb-t-'), sg.Push(), sg.Checkbox('Chiaki', key='cb-ch-'), sg.Push(),
        sg.Checkbox("Seto", key='cb-s-'), sg.Push(), sg.Checkbox("Eduard", key='cb-e-'), ],
        [sg.VPush()],
        [sg.Checkbox("Felix", key='cb-f-'), sg.Push(), sg.Checkbox("Kieran", key='cb-ki-'), sg.Push(),
        sg.Checkbox("Lee", key='cb-l-'), sg.Push(), sg.Checkbox("Hina", key='cb-hm-'), sg.Push(),
        sg.Checkbox("Natsumi", key='cb-n-'), sg.Push(), sg.Checkbox("Yoichi", key='cb-yi-')],
        [sg.VPush()],
        [sg.Checkbox("Keitaro", key='cb-k-'), sg.Push(), sg.Checkbox("Hiro", key='cb-hi-'), sg.Push(),
        sg.Checkbox("Goro", key='cb-g-'), sg.Push(), sg.Checkbox("Yoshi", key='cb-yo-'), sg.Push(),
        sg.Checkbox("Aiden", key='cb-a-'), sg.Push(), sg.Checkbox("Naoto", key='cb-na-')],
        [sg.VPush()],
        [sg.Checkbox("Heather", key='cb-he-'), sg.Push(), sg.Checkbox("Archer", key='cb-ar-'), sg.Push(),
        sg.Checkbox("William", key='cb-w-'), sg.Push(), sg.Checkbox("Rayne", key='cb-ra-'), sg.Push(),
        sg.Checkbox('Toshu', key='cb-to-'), sg.Push(), sg.Checkbox('Ichiru', key='cb-ic-')],
        [sg.VPush()],
        [sg.Checkbox('Connor', key='cb-co-'), sg.Push(), sg.Checkbox('Jirou', key='cb-ji-'), sg.Push(),
        sg.Checkbox('Avan', key='cb-ha-'), sg.Push(), sg.Checkbox('Yuuto', key='cb-yt-'), sg.Push(),
        sg.Checkbox('Haruki', key='cb-hr-'), sg.Push(), sg.Checkbox('Noah', key='cb-no-')],
        [sg.VPush()]
    ]

    cb_sm_chars = [
        [sg.VPush()],
        [sg.Checkbox("Andre", key='cb_sm-u-'), sg.Push(), sg.Checkbox("Lloyd", key='cb_sm-l-'), sg.Push(),
        sg.Checkbox("Darius", key='cb_sm-d-'), sg.Push(), sg.Checkbox("Emilia", key='cb_sm-e-'), sg.Push(),
        sg.Checkbox("Jin", key='cb_sm-j-'), sg.Push(), sg.Checkbox("Vera", key='cb_sm-v-')],
        [sg.VPush()],
        [sg.Checkbox("Yoshi", key='cb_sm-yo-'), sg.Push(), sg.Checkbox("Naoto", key='cb_sm-na-'), sg.Push(),
        sg.Checkbox("Taiga", key='cb_sm-t-'), sg.Push(), sg.Checkbox("Yoichi", key='cb_sm-yi-'), sg.Push(),
        sg.Checkbox("Natsumi", key='cb_sm-n-'), sg.Push(), sg.Checkbox("Hunter", key='cb_sm-hu-')],
        [sg.VPush()],
        [sg.Checkbox("Hiro", key='cb_sm-hi-'), sg.Push(), sg.Checkbox("Keitaro", key='cb_sm-k-'), sg.Push(),
        sg.Checkbox("Yuri", key='cb_sm-yu-'), sg.Push(), sg.Checkbox("Goro", key='cb_sm-g-'), sg.Push(),
        sg.Checkbox("Aiden", key='cb_sm-a-'), sg.Push(), sg.Checkbox("William", key='cb_sm-w-')],
        [sg.VPush()],
    ]

    extract_dialogs_tab = [
        [sg.Text('Folder Containing .rpy Files:'), sg.Input(key='-rpy_files_folder_path-'), sg.FolderBrowse(key='-ed_browse_rpy_files_folder_path_btn-')],
        [sg.Text('Game:'),
        sg.Combo(['Camp Buddy', 'Camp Buddy Scoutmasters Edition'], default_value='Camp Buddy', enable_events=True,
                expand_x=True, readonly=True, key='-game_selection_changed-')],
        [sg.VPush()],
        center([sg.Text('Check the characters you want to extract the dialog:')]),
        center([sg.pin(sg.Column(cb_chars, key="-cb_chars-", expand_x=True), vertical_alignment='c')]),
        center([sg.pin(sg.Column(cb_sm_chars, key="-cb_sm_chars-", visible=False, expand_x=True), vertical_alignment='c')]),
        [sg.VPush()],
        [sg.Push(), sg.Text('Delimeter:'), 
        sg.Radio('Semicolon [ ; ]', group_id='ed_delimeter_option', key='-delimeter_semicolon-', default=True),
        sg.Radio('Comma [ , ]', group_id='ed_delimeter_option', key='-delimeter_comma-'), sg.Push(),
        sg.Checkbox('Exclude Roleplay Dialogs', default=True, key='-exclude_roleplay_dialogs-'), sg.Push()],
        [sg.VPush()],
        [sg.Text('Export Options:'), sg.Push(), sg.Push(), sg.Push(),
        sg.Radio('Export to File', group_id='ed_export_options', key='-export_to_file-', default=True, enable_events=True),
        sg.Radio('Export to Folder', group_id='ed_export_options', key='-export_to_folder-', enable_events=True)],
        [sg.Text('Destination File:', key='-ed_dest_file_txt-'), sg.Input(key='-ed_dest_file-', expand_x=True), sg.FileSaveAs(key='-ed_dest_file_save_as-', file_types=(('CSV File', '.csv'), ('Text File', '.txt')), ), 
        sg.Text('Destination Folder:', key='-ed_dest_folder_txt-'), sg.Input(key='-ed_dest_folder-', expand_x=True), sg.FolderBrowse(key='-ed_dest_folder_browse-')],
        [sg.Button("Extract Dialogs", key='-extract_dialogs_btn-', expand_x=True, button_color='Green')]
    ]

    extract_assets_tab = [
        [sg.Text('RPA File:'), sg.Input(key='-ea_rpa_path-', expand_x=True),
        sg.FileBrowse(key='-ea_filebrowse-', file_types=(('RPA Archives', '*.rpa'),))],
        [sg.Text('RPA File Contents:'), sg.Push(), sg.Button('View Content', key='-ea_viewcontent-')],
        [sg.Listbox(values=[], key="-rpa_file_list-", expand_x=True, size=(None, 20), horizontal_scroll=True)],
        [sg.Text('Destination Folder:'), sg.Input(key='-ea_dest_folder-', expand_x=True), sg.FolderBrowse(key='-ea_folder_browse-')],
        [
            sg.Button("Extract Assets", key='-extract_assets_btn-', expand_x=True, button_color='Green'), 
            sg.Button("Cancel", button_color='Red', key='-cancel_extract_assets_btn-', expand_x=True, visible=False)
        ],
        # [sg.Button("Perform Long Operation", key='-extract_assets_btn-', expand_x=True)]
    ]

    main_column = [
        [sg.TabGroup([
            [sg.Tab('Extract Assets', extract_assets_tab, key='-ea_tab-'), sg.Tab('Extract Dialogs', extract_dialogs_tab, key='-ed_tab-')]
        ], tab_location="Top", enable_events=True, key='-switched_tab-')],
    ]

    window_menu = [
        ['File', ['Exit']],
        ['Help', ['Documentation', 'About']],
    ]

    layout = [
        [sg.Menu(window_menu)],
        [sg.Column(main_column)],
        [sg.ProgressBar(max_value=100, orientation='horizontal', key='-progress_bar-', size=(56, 20), style='winnative')],
        [sg.Text('Status:'), sg.Text('Idle', key='-current_status-', size=(50, None))],
    ]

    if sg.running_windows():
        icon = resource_path('icon.ico')
    elif sg.running_linux():
        icon = resource_path('icon.png')

    main_window = sg.Window(title=title, layout=layout, icon=icon)
    return main_window
    
window = get_main_window()
long_operation = False
ea_mode = True


# FUNCTIONS FOR GENERAL USE

def update_progress_bar(current_count):
    window['-progress_bar-'].update(current_count=current_count)

def reset_progress_bar():
    window['-progress_bar-'].update(current_count=0)

def finish_progress_bar():
    window['-progress_bar-'].update(current_count=100)

def update_status(message: str):
    if debug_mode:
        print(f'Status: {message}')
    window["-current_status-"].update(value=message)
    window.Refresh()

def reset_status():
    update_status("Idle")

def dest_folder_empty():
    update_status("Error. Destination folder is empty")

def long_operation_ongoing(text: str):
    sg.popup_ok(text, title='Program is Busy', non_blocking=True)



# FUNCTIONS RELATED TO EXTRACTING ASSETS TAB!

def rpa_filepath_empty():
    update_status("Error. No RPA file selected")

def update_rpa_file_list(values):
    window["-rpa_file_list-"].update(values)

def clear_rpa_file_list():
    window["-rpa_file_list-"].update(values=[])

def ea_checks(values):
    rpapath = values['-ea_rpa_path-']
    if not valid_path(rpapath):
        rpa_filepath_empty()
        return False  # rpa file path is empty
    result, message = valid_rpa_file(rpapath)
    update_status(message)
    if not result:
        clear_rpa_file_list()
        return False  # rpa file is not valid or the user has no permission
    else:
        return True

def ea_view_content(values):
    rpapath = values['-ea_rpa_path-']
    if not ea_checks(values):
        return False  # checks have failed
    else:
        update_rpa_file_list(list_rpa_files_2(rpapath))
        update_status(f'{get_filename_from_path(rpapath)} contents listed')

def disable_ea_tab_elements():
    # DISABLE EXTRACT ASSETS BUTTON
    window['-ea_rpa_path-'].update(disabled=True)
    window['-rpa_file_list-'].update(disabled=True)
    window['-ea_filebrowse-'].update(disabled=True)
    window['-ea_folder_browse-'].update(disabled=True)
    window['-extract_assets_btn-'].update(button_color='Gray', disabled = True)

def enable_ea_tab_elements():
    window['-ea_rpa_path-'].update(disabled=False)
    window['-rpa_file_list-'].update(disabled=False)
    window['-ea_viewcontent-'].update(disabled=False)
    window['-ea_filebrowse-'].update(disabled=False)
    window['-ea_folder_browse-'].update(disabled=False)
    window['-extract_assets_btn-'].update(button_color='Green', disabled = False)

def extract_assets(values):
    rpapath = values['-ea_rpa_path-']
    ea_dest_folder = values["-ea_dest_folder-"]

    print(f"ea_dest_folder : {ea_dest_folder}")
    print(f"rpa_path : {rpapath}")

    if not ea_checks(values):
        return  # checks have failed
    if not valid_path(ea_dest_folder):
        dest_folder_empty()
        return  # destination path is empty

    unrpa = UnRPA(
        filename=rpapath,
        camp_buddy_toolbox_window=window,
        path=ea_dest_folder,
        verbosity=verbosity
    )
    window.perform_long_operation(unrpa.extract_files, '-ea_done-')
    long_operation = True
    disable_ea_tab_elements()

def ea_done(values):
    rpapath = values['-ea_rpa_path-']
    ea_dest_folder = values["-ea_dest_folder-"]

    # Enable the extract assets tab elements
    enable_ea_tab_elements()

    # Make the progress bar 100% to indicate completeness
    finish_progress_bar()

    # Update the status to indicate completeness
    update_status(f'[100%] Finished extracting {get_filename_from_path(rpapath)}')

    # Show the popup
    popup = operation_done_popup(
        title='Finished Extracting Assets',
        message=f'{get_filename_from_path(rpapath)} has been extracted to:\n{ea_dest_folder}',
        dest_folder=ea_dest_folder
    )

    while True:
        event2, values2 = popup.Read()
        print_debug_info('Assets Extracted Popup', event2, values2)

        if event2 == '-OK-' or sg.WIN_CLOSED:
            popup.close()
            break

        if event2 == '-open_dest_folder-':
            open_folder(popup['-open_dest_folder-'].metadata)
            popup.close()
            break

    # Reset the progress bar and status
    reset_progress_bar()
    reset_status()



# FUNCTIONS RELATED TO EXTRACTING DIALOGS TAB     

def switch_game(values):
    if values['-game_selection_changed-'] == 'Camp Buddy':
        window['-cb_sm_chars-'].update(visible=False)
        window['-cb_chars-'].update(visible=True)
    else:
        window['-cb_chars-'].update(visible=False)
        window['-cb_sm_chars-'].update(visible=True)

def export_to_file():
    window['-ed_dest_file_txt-'].update(visible=True)
    window['-ed_dest_file-'].update(visible=True)
    window['-ed_dest_file_save_as-'].update(visible=True)
    window['-ed_dest_folder-'].update(visible=False)
    window['-ed_dest_folder_browse-'].update(visible=False)
    window['-ed_dest_folder_txt-'].update(visible=False)

def export_to_folder():
    window['-ed_dest_folder_txt-'].update(visible=True)
    window['-ed_dest_folder-'].update(visible=True)
    window['-ed_dest_folder_browse-'].update(visible=True)
    window['-ed_dest_file_txt-'].update(visible=False)
    window['-ed_dest_file-'].update(visible=False)
    window['-ed_dest_file_save_as-'].update(visible=False)

def rpy_files_folder_path_empty():
    update_status('Error. Folder containing .rpy Files is empty')

def ed_destination_file_empty():
    update_status('Error. Destination File is empty')

def ed_selected_chars_empty():
    update_status('Error. Check at least one character')

def get_ed_cb_checkboxes():
    '''Returns the character checkboxes of Camp Buddy'''
    
    checkboxes = []
    for element in reduce(operator.concat, window['-cb_chars-'].Rows):      # get the flatenned elements inside the list of rows
        if 'Checkbox' in str(element):                                      # if it's a checkbox
            checkboxes.append(element)                                      # add it to the list
    return checkboxes                                                       # return the list

def get_ed_cb_sm_checkboxes():
    '''Returns the character checkboxes of Camp Buddy Scoutmasters Edition'''

    checkboxes = []
    for element in reduce(operator.concat, window['-cb_sm_chars-'].Rows):   # get the flatenned elements inside the list of rows
        if 'Checkbox' in str(element):                                      # if it's a checkbox
            checkboxes.append(element)                                      # add it to the list
    return checkboxes                                                       # return the list

def disable_ed_checkboxes():
    cb_checkboxes = get_ed_cb_checkboxes()
    for checkbox in cb_checkboxes:
        checkbox.update(disabled=True)

    cb_sm_checkboxes = get_ed_cb_sm_checkboxes()
    for checkbox in cb_sm_checkboxes:
        checkbox.update(disabled=True)

def enable_ed_checkboxes():
    cb_checkboxes = get_ed_cb_checkboxes()
    for checkbox in cb_checkboxes:
        checkbox.update(disabled=False)

    cb_sm_checkboxes = get_ed_cb_sm_checkboxes()
    for checkbox in cb_sm_checkboxes:
        checkbox.update(disabled=False)

def disable_ed_tab_elements():
    window['-rpy_files_folder_path-'].update(disabled=True)
    window['-ed_browse_rpy_files_folder_path_btn-'].update(disabled=True)
    window['-game_selection_changed-'].update(disabled=True)
    disable_ed_checkboxes()  # we can't enable / disable columns so we disable each checkboxes instead
    window['-delimeter_semicolon-'].update(disabled=True)
    window['-delimeter_comma-'].update(disabled=True)
    window['-exclude_roleplay_dialogs-'].update(disabled=True)
    window['-export_to_folder-'].update(disabled=True)
    window['-export_to_file-'].update(disabled=True)
    window['-ed_dest_folder-'].update(disabled=True)
    window['-ed_dest_folder_browse-'].update(disabled=True)
    window['-ed_dest_file-'].update(disabled=True)
    window['-ed_dest_file_save_as-'].update(disabled=True)
    window['-extract_dialogs_btn-'].update(disabled=True)

def enable_ed_tab_elements():
    window['-rpy_files_folder_path-'].update(disabled=False)
    window['-ed_browse_rpy_files_folder_path_btn-'].update(disabled=False)
    window['-game_selection_changed-'].update(disabled=False)
    enable_ed_checkboxes()  # we can't enable / disable columns so we disable each checkboxes instead
    window['-delimeter_semicolon-'].update(disabled=False)
    window['-delimeter_comma-'].update(disabled=False)
    window['-exclude_roleplay_dialogs-'].update(disabled=False)
    window['-export_to_folder-'].update(disabled=False)
    window['-export_to_file-'].update(disabled=False)
    window['-ed_dest_folder-'].update(disabled=False)
    window['-ed_dest_folder_browse-'].update(disabled=False)
    window['-ed_dest_file-'].update(disabled=False)
    window['-ed_dest_file_save_as-'].update(disabled=False)
    window['-extract_dialogs_btn-'].update(disabled=False)   

def ed_checks(values):
    '''Warns the user if any of the required fields in Extract Dialogs are empty'''

    # CHECK IF THE FOLDER CONTAINING .RPY FILES FOLDER PATH IS EMPTY
    rpy_files_folder_path = values['-rpy_files_folder_path-']
    if not valid_path(rpy_files_folder_path):
        rpy_files_folder_path_empty()
        return False
        

    # CHECK IF THE DESTINATION FILE IS EMPTY
    if values['-export_to_file-']:
        if not valid_path(values['-ed_dest_file-']):
            ed_destination_file_empty()
            return False

    # CHECK IF THE DESTINATION FOLDER IS EMPTY
    if values['-export_to_folder-']:
        if not valid_path(values['-ed_dest_folder-']):
            dest_folder_empty()
            return False

    # CHECK IF THE USER CHECKED AT LEAST CHARACTER CHECKBOX
    chars_checked = 0
    if values['-game_selection_changed-'] == 'Camp Buddy':
        checkboxes = get_ed_cb_checkboxes()

    if values['-game_selection_changed-'] == 'Camp Buddy Scoutmasters Edition':
        checkboxes = get_ed_cb_sm_checkboxes()

    for checkbox in checkboxes:      # Get the checkboxes of Camp Buddy characters
        if checkbox.get():           # If the checkbox is not checked
            chars_checked += 1       # Add value to the non checked characters
        
    if chars_checked == 0:           # If the amount of checkboxes that are not checked is beyond 1
        ed_selected_chars_empty()    # Warn the user that they have to check at least one
        return False                 # Return False

    return True

def get_char_aliases_to_be_extracted():
    '''Returns the character aliases based on the characters you checked'''
    alias_pattern = '-(.*?)-'

    if values['-game_selection_changed-'] == 'Camp Buddy':
        checkboxes = get_ed_cb_checkboxes()

    if values['-game_selection_changed-'] == 'Camp Buddy Scoutmasters Edition':
        checkboxes = get_ed_cb_sm_checkboxes()

    char_aliases_to_be_extracted = []
    for checkbox in checkboxes:
        if checkbox.get():
            alias = re.search(alias_pattern, checkbox.Key).group(1)
            char_aliases_to_be_extracted.append(alias)

    return char_aliases_to_be_extracted   
    
def extract_dialogs(values):
    rpy_files_folder_path = values['-rpy_files_folder_path-']
    ed_dest_folder = values['-ed_dest_folder-']
    ed_dest_file = values['-ed_dest_file-']
    game = 1 if values['-game_selection_changed-'] == 'Camp Buddy' else 2
    export_to_file = values['-export_to_file-']
    if values['-delimeter_semicolon-']:
        delimeter = ';'
    else:
        delimeter = ','


    if not ed_checks(values):
        return  # checks have failed

    char_aliases_to_extract = get_char_aliases_to_be_extracted()
    print(f'Character Aliases you wanted to extract:\n\n{char_aliases_to_extract}')

    global cb_dialog_extractor 
    cb_dialog_extractor = CBDialogExtractor(
        source_directory=rpy_files_folder_path,
        game=game,
        chosen_chars=char_aliases_to_extract,
        export_to_file=export_to_file,
        destination_file=ed_dest_file,
        destination_directory=ed_dest_folder,
        delimeter=delimeter,
        show_stats=True,
        verbose_level=3,
        cb_toolbox_window=window
    )

    window.perform_long_operation(cb_dialog_extractor.extract, '-ed_done-')
    long_operation = True
    disable_ed_tab_elements()

def ed_done(values):
    ed_dest_folder = values['-ed_dest_folder-']
    ed_dest_file = values['-ed_dest_file-']

    # Enable extract dialogs tab elements
    enable_ed_tab_elements()

    # Make the progress bar 100% to indicate completeness
    finish_progress_bar()

    # Update the status to indicate completeness
    update_status('[100%] Finished extracting dialogs')

    # Show the popup
    popup = operation_done_popup(
        title='Finished Extracting Dialogs',
        message=f'{cb_dialog_extractor.stats_str}\n\nDialogs have been extracted to:\n{ed_dest_folder if valid_path(ed_dest_folder) else ed_dest_file}',
        dest_folder=get_folder_path_from_filepath(values['-ed_dest_file-']) if not valid_path(values['-ed_dest_folder-']) else values['-ed_dest_folder-']
    )

    while True:
        event2, values2 = popup.Read()
        if debug_mode:
            print_debug_info('Dialogs Extracted Popup', event2, values2)

        if event2 == '-OK-' or sg.WIN_CLOSED:
            popup.close()
            break

        if event2 == '-open_dest_folder-':
            open_folder(popup['-open_dest_folder-'].metadata)
            popup.close()
            break

    # Reset the progress bar and status
    reset_progress_bar()
    reset_status()
    


while True:
    event, values = window.read()

    if debug_mode:
        print_debug_info('Main Window', event, values)
        # sg.show_debugger_window()

    if event == 'About':
        about()

    if event == 'Exit' or event == sg.WIN_CLOSED:
        break

    if event == '-switched_tab-':
        export_to_file()
        reset_status()

    if event == '-update_status-':
        update_status(values['-update_status-'])

    if event == '-update_progress_bar-':
        update_progress_bar(values['-update_progress_bar-'])



    # EXTRACT ASSETS TAB

    if event == '-ea_viewcontent-':
        ea_view_content(values)

    if event == '-extract_assets_btn-':
        extract_assets(values)

    if event == '-ea_done-':
        ea_done(values)



    # EXTRACT DIALOGS TAB

    if event == '-game_selection_changed-':
        switch_game(values)

    if event == '-export_to_file-':
        export_to_file()

    if event == '-export_to_folder-':
        export_to_folder()

    if event == '-extract_dialogs_btn-':
        extract_dialogs(values)

    if event == '-ed_done-':
        ed_done(values)