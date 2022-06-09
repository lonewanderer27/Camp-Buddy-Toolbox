import os
import time
import PySimpleGUI as sg
from unrpa import UnRPA
from tools import *
from about import *

current_directory = os.getcwd
debug_mode = True
sg.theme('DarkBrown3')

# UnRPA Settings
verbosity = 2

def list_rpa_files_2(rpafile: str) -> list:
    unrpa = UnRPA(filename=rpafile, verbosity=2)
    files_list = sorted(unrpa.list_files())
    return files_list

def popup_long_operation_finished(title, message):
    sg.popup(message, title=title, grab_anywhere=True, keep_on_top=True, non_blocking=True)

def operation_done_popup(title: str, message: str, dest_folder: str, open_folder_key: str):
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

def get_main_window():

    cb_chars = [
        [sg.VPush()],
        [sg.Checkbox("Yuri", key='-cb_yuri-'), sg.Push(), sg.Checkbox("Hunter", key='-cb_hunter-'), sg.Push(),
        sg.Checkbox("Taiga", key='-cb_taiga-'), sg.Push(), sg.Checkbox("Yuki", key='-cb_yuki-'), sg.Push(),
        sg.Checkbox("Seto", key='-cb_seto-'), sg.Push(), sg.Checkbox("Eduard", key='-cb_eduard-'), ],
        [sg.VPush()],
        [sg.Checkbox("Felix", key='-cb_felix-'), sg.Push(), sg.Checkbox("Kieran", key='-cb_kieran-'), sg.Push(),
        sg.Checkbox("Lee", key='-cb_lee-'), sg.Push(), sg.Checkbox("Hina Akiba", key='-cb_hina-'), sg.Push(),
        sg.Checkbox("Natsumi", key='-cb_natsumi-'), sg.Push(), sg.Checkbox("Yoichi", key='-cb_yoichi-')],
        [sg.VPush()],
        [sg.Checkbox("Keitaro", key='-cb_keitaro-'), sg.Push(), sg.Checkbox("Hiro", key='-cb_hiro-'), sg.Push(),
        sg.Checkbox("Goro", key='-cb_goro-'), sg.Push(), sg.Checkbox("Yoshi", key='-cb_yoshi-'), sg.Push(),
        sg.Checkbox("Aiden", key='-cb_aiden-'), sg.Push(), sg.Checkbox("Naoto", key='-cb_naoto-')],
        [sg.VPush()],
        [sg.Checkbox("Heather Springfield", key='-cb_heather-'), sg.Push(),
        sg.Checkbox("Archer Springfield", key='-cb_archer-'), sg.Push(),
        sg.Checkbox("William Clermont", key='-cb_william-')],
        [sg.VPush()],
    ]

    cb_sm_chars = [
        [sg.VPush()],
        [sg.Checkbox("Andre", key='-cb_sm_andre-'), sg.Push(), sg.Checkbox("Lloyd", key='-cb_sm_lloyd-'), sg.Push(),
        sg.Checkbox("Darius", key='-cb_sm_darius-'), sg.Push(), sg.Checkbox("Emilia", key='-cb_sm_emilia-'), sg.Push(),
        sg.Checkbox("Jin", key='-cb_sm_jin-'), sg.Push(), sg.Checkbox("Vera", key='-cb_sm_vera-')],
        [sg.VPush()],
        [sg.Checkbox("Yoshi", key='-cb_sm_yoshi-'), sg.Push(), sg.Checkbox("Naoto", key='-cb_sm_naoto-'), sg.Push(),
        sg.Checkbox("Taiga", key='-cb_sm_taiga-'), sg.Push(), sg.Checkbox("Yoichi", key='-cb_sm_yoichi-'), sg.Push(),
        sg.Checkbox("Natsumi", key='-cb_sm_natsumi-'), sg.Push(), sg.Checkbox("Hunter", key='-cb_sm_hunter-')],
        [sg.VPush()],
        [sg.Push(), sg.Checkbox("Hiro", key='-cb_sm_hiro-'), sg.Push(), sg.Checkbox("Keitaro", key='cb_sm_keitaro-'), sg.Push(),
        sg.Checkbox("Yuri", key='-cb_sm_yuri-'), sg.Push(), sg.Checkbox("Goro", key='-cb_sm_goro-'), sg.Push(),
        sg.Checkbox("Aiden", key='-cb_sm_aiden-'), sg.Push()],
        [sg.VPush()],
    ]

    extract_dialogs_to_dir_column = [
        [sg.Text('Destination Folder:'), sg.Input(key='-es_dest_folder-', expand_x=True),
        sg.FolderBrowse(key='-es_folder_browse-')]
    ]

    extract_dialogs_to_file_column = [
        [sg.Text('Destination File:'), sg.Input(key='-es_dest_file-', expand_x=True),
        sg.FileSaveAs(key='-es_file_save_as-', file_types=(('CSV File', '.csv'), ('Text File', '.txt')), )]
    ]

    extract_dialogs_tab = [
        [sg.Text('Folder Containing .rpy Files:'), sg.Input(key='-py_dialogs_folder-'), sg.FolderBrowse()],
        [sg.Text('Game:'),
        sg.Combo(['Camp Buddy', 'Camp Buddy: Scoutmasters Edition'], default_value='Camp Buddy', enable_events=True,
                expand_x=True, readonly=True, key='-game_selection_changed-')],
        [sg.VPush()],
        center([sg.Text('Check the characters you want to extract the dialog:')]),
        center([sg.pin(sg.Column(cb_chars, key="-cb_chars-", expand_x=True), vertical_alignment='c')]),
        center([sg.pin(sg.Column(cb_sm_chars, key="-cb_sm_chars-", visible=False, expand_x=True), vertical_alignment='c')]),
        [sg.VPush()],
        [sg.Text('Options:'), sg.Push(),
        sg.Radio('All characters in one file', 'es_option1', key='-all_chars_in_1_file-', default=True,
                enable_events=True),
        sg.Radio('One character per file', 'es_option1', key='-1_char_per_file-', enable_events=True)],
        [sg.pin(sg.Column(extract_dialogs_to_file_column, key='-es_to_file_column-', expand_x=True))],
        [sg.pin(sg.Column(extract_dialogs_to_dir_column, key='-es_to_dir_column-', expand_x=True, visible=False))],
        [sg.Button("Extract Dialogs", key='-extract_dialogs_btn-', expand_x=True, button_color='Green')]
    ]

    extract_assets_tab = [
        [sg.Text('RPA File:'), sg.Input(key='-ea_rpa_path-', expand_x=True),
        sg.FileBrowse(file_types=(('RPA Archives', '*.rpa'),))],
        [sg.Text('RPA File Contents:'), sg.Push(), sg.Button('View Content')],
        [sg.Listbox(values=[], key="-rpa_file_list-", expand_x=True, size=(None, 20), horizontal_scroll=True)],
        [sg.Text('Destination Folder:'), sg.Input(key='-ea_dest_folder-', expand_x=True), sg.FolderBrowse()],
        [
            sg.Button("Extract Assets", key='-extract_assets_btn-', expand_x=True, button_color='Green'), 
            sg.Button("Cancel", button_color='Red', key='-cancel_extract_assets_btn-', expand_x=True, visible=False)
        ],
        # [sg.Button("Perform Long Operation", key='-extract_assets_btn-', expand_x=True)]
    ]

    main_column = [
        [sg.TabGroup([
            [sg.Tab('Extract Assets', extract_assets_tab), sg.Tab('Extract Dialogs', extract_dialogs_tab)]
        ], expand_x=True, tab_location="Top", enable_events=True, key='-switched_tab-')],
    ]

    window_menu = [
        ['File', ['Exit']],
        ['Help', ['Documentation', 'About']],
    ]

    master_layout = [
        [sg.Menu(window_menu)],
        [sg.Column(main_column)],
        [sg.ProgressBar(max_value=100, orientation='horizontal', expand_x=True, key='-progress_bar-', size=(20, 20), style='winnative')],
        [sg.Text('Status:'), sg.Text('Idle', key='-current_status-', size=(75, None), auto_size_text=True)],
    ]

    main_window = sg.Window(title=title, layout=master_layout, icon="icon.png")
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
    print(message)
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

def disable_ea_extract_assets_btn():
    window['-extract_assets_btn-'].update(button_color='Gray', disabled = True)

def enable_ea_extract_assets_btn():
    window['-extract_assets_btn-'].update(button_color='Green', disabled = False)

def ea_extract_assets(values):
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
        camp_buddy_tool_window=window,
        path=ea_dest_folder,
        verbosity=verbosity
    )
    window.perform_long_operation(unrpa.extract_files, '-ea_done-')
    long_operation = True
    disable_ea_extract_assets_btn()

def ea_done(values):
    rpapath = values['-ea_rpa_path-']
    ea_dest_folder = values["-ea_dest_folder-"]

    # Enable the extract assets button
    enable_ea_extract_assets_btn()

    # Make the progress bar 100% to indicate completeness
    finish_progress_bar()

    # Update the status to indicate completeness
    update_status(f'[100%] Finished extracting {get_filename_from_path(rpapath)}')

    # Show the popup
    popup = operation_done_popup(
        title='Finished Extracting Assets',
        message=f'{get_filename_from_path(rpapath)} has been extracted to {ea_dest_folder}',
        dest_folder=ea_dest_folder,
        open_folder_key='-open_ea_dest_folder-'
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

def switch_to_cb():
    window['-cb_sm_chars-'].update(visible=False)
    window['-cb_chars-'].update(visible=True)

def switch_to_cb_sm():
    window['-cb_chars-'].update(visible=False)
    window['-cb_sm_chars-'].update(visible=True)

def switch_game(values):
    if values['-game_selection_changed-'] == 'Camp Buddy':
        switch_to_cb()
    else:
        switch_to_cb_sm()

def all_chars_in_one_file(values):
    # -es_file_save_as-
    window['-es_to_file_column-'].update(visible=True)
    window['-es_to_dir_column-'].update(visible=False)

def one_char_per_file(values):
    # -es_folder_browse-
    window['-es_to_file_column-'].update(visible=False)
    window['-es_to_dir_column-'].update(visible=True)

def long_ops_2(window, number):
    window.Refresh()
    for num in range(number):
        time.sleep(1)
        update_status(num)
        window['-progress_bar-'].update(current_count=num)
    return number


while True:
    event, values = window.read()

    if debug_mode:
        print_debug_info('Main Window', event, values)
        # sg.show_debugger_window()

    if event == 'About':
        about()

    if event == 'Exit' or event == sg.WIN_CLOSED:
        break

    # EXTRACT ASSETS TAB

    if event == 'View Content':
        ea_view_content(values)

    if event == '-cb_selected-':
        switch_to_cb()

    if event == '-cb_sm_selected-':
        switch_to_cb_sm()

    if event == '-game_selection_changed-':
        switch_game(values)

    if event == '-extract_assets_btn-':
        ea_extract_assets(values)

    if event == '-update_status-':
        update_status(values['-update_status-'])

    if event == '-update_progress_bar-':
        update_progress_bar(values['-update_progress_bar-'])

    if event == '-ea_done-':
        ea_done(values)


    # EVENTS USED JUST TO TEST THE LONG OPERATION FUNCTION OF PYSIMPLEGUI
    # DOES NOT DO ANYTHING MEANINGFUL !!!

    if event == '-extract_assets_btn-1':
        number = 10
        window['-progress_bar-'].update(max=number - 3)
        window.perform_long_operation(lambda: long_ops_2(window, number), '-long_ops_2_completed-')

    if event == '-long_operation_done-':
        sg.popup('long operation is done!')

    if event == '-long_ops_2_completed-':
        update_status("long ops 2 has completed!")


    # EXTRACT DIALOGS TAB

    if event == '-all_chars_in_1_file-':
        all_chars_in_one_file(values)

    if event == '-1_char_per_file-':
        one_char_per_file(values)