#!/usr/bin/env python

import os
import ntpath
import re
import csv
import argparse
from pprint import pprint

class CBDialogExtractor:
    '''
    Extracts character dialogs from Camp Buddy & Camp Buddy Scoutmasters Edition.

    param   source_directory:           Folder Containing .rpy Files
    type    source_directory:           (str)

    param   game:                       1 = Camp Buddy, 2 = Camp Buddy Scoutmasters Edition
    type    game:                       (int)   

    param   chosen_chars:               Characters to extract dialogs of. Refer to chars_aliases dictionary for the alias of each character
    type    chosen_chars:               (list)

    param   exclude_roleplay_dialogs:   Exclude roleplay dialogs. Default is True
    type    exclude_roleplay_dialogs:   (bool)

    param   export_to_file:             Export the dialogs to file. Default is True. If False then dialogs would be exported to directory
    type    export_to_file:             (bool)

    param   destination_file:           Export destination file path. Used if export_to_file param is True. Ignored if export_to_file param is False
    type    destination_file:           (str)

    param   destination_directory:      Export destination directory. Used if export_to_file param is False. Ignored if export_to_file param is True
    type    destination_directory:      (str)

    param   header:                     Header columns. Default is ['name', 'dialog']
    type    header:                     (list)

    param   delimeter:                  Symbol to separate the character name and their dialog. Default is ;
    type    delimeter:                  (str)

    param   verbose_level:              0 = no output to terminal, 1 = shows message when dialogs extraction has started and finished and where it was saved, 2 = shows the percentage progress and the current file being worked on, 3 = shows the character name and their dialog in real time as they get extracted. Default is 2
    type    verbose_level:              (int)

    param   show_stats:                 At the end of extraction, show the stats detailing the amount of .rpy files processed and total dialog lines per character are exported. Default is True
    type    show_stats:                 (bool)

    param   cb_toolbox_window:          Camp Buddy Toolbox PySimpleGUI Window object. Only used when embedded in Camp Buddy Toolbox program. Default is None
    type    cb_toolbox_window:          (object)
    '''

    def __init__(
        self,
        source_directory: str, 
        game: int, 
        chosen_chars: list, 
        exclude_roleplay_dialogs = True,
        export_to_file = True,
        destination_file = str,
        destination_directory = str,
        header = ['name', 'dialog'],
        delimeter = ';',
        show_stats = True,
        verbose_level = 2,
        cb_toolbox_window = None,
    ) -> None:
        self.window = cb_toolbox_window
        self.source_directory = source_directory
        self.game = game
        self.chosen_chars = chosen_chars
        self.exclude_roleplay_dialogs = exclude_roleplay_dialogs
        self.export_to_file = export_to_file
        self.destination_file = destination_file
        self.destination_directory = destination_directory
        self.header = header
        self.delimeter = delimeter
        self.show_stats = show_stats
        self.verbose_level = verbose_level
        self.chars_aliases = {
            # Camp Buddy Scoutmasters Edition Character Aliases
            'a': 'Aiden',
            'u': 'Andre',
            'g': 'Goro',
            'yo': 'Yoshinori',
            'yu': 'Yuri',
            'l': 'Lloyd',
            'd': 'Darius',
            'j': 'Hyunjin',
            'e': 'Emilia',
            'yi': 'Yoichi',
            't': 'Taiga',
            'k': 'Keitaro',
            'hu': 'Hunter',
            'hi': 'Hiro',
            'n': 'Natsumi',
            'na': 'Naoto',
            'nag': 'Guest',
            'nas': 'Stripper',
            'r': 'Bellboy',
            'm': 'Masseur',
            'bt': 'Bartender',
            'r': 'Reimond',
            'ju': 'Justin',
            'o': 'Officiator',
            'ol': 'Doctor',
            'v': 'Vera',
            'w': 'William',
            'wo': 'Workers',
            'ar': 'Architect',
            'fo': 'Foreman',

            # Camp Buddy Character Aliases
            'f': 'Felix',
            'e': 'Eduard',
            'l': 'Lee',
            'con': 'Conductor',
            'ra': 'Rayne',
            'to': 'Toshu',
            'ic': 'Ichiru',
            'co': 'Connor',
            'ji': 'Jirou',
            'ha': 'Avan',
            'yt': 'Yuuto',
            'hr': 'Haruki',
            'no': 'Noah',
            'ch': 'Chiaki',
            'hm': 'Hina',
            'y': 'Yuki',
            'he': 'Heather',
            'ar': 'Archer',
            'ki': 'Kieran',

            # I only included the characters that it makes sense for someone
            # to get the dialogs of.
            #
            # Character aliases such as 'all' and 'Aiden & Goro' are not included here.
            #
            # And as such an error would occur if someone were to extract
            # their dialogs using their alias.
        }
        self.game_aliases = {
            1: 'Camp Buddy',
            2: 'Camp Buddy Scoutmasters Edition'
        }
        # DIALOGS WOULD BE STORED HERE
        self.dialogs = {
            1: {},  # Camp Buddy
            2: {}   # Camp Buddy Scoutmasters Edition
        }
        self.total_amount_of_rpyfiles = 0   # TOTAL AMOUNT OF .rpy FILES
        self.total_amount_of_dialogs = 0    # TOTAL AMOUNT OF DIALOGS
        self.stats = {}                     # STATS IN DICTIONARY FORM
        self.stats_str = ''                 # STATS IN STRING FORM

        self.valid_parameters()             # CHECKS IF THE PARAMETERS ARE VALID


    # FUNCTIONS THAT SEND PROGRESS TO CAMP BUDDY TOOLBOX

    def update_progress(
        self, 
        file_number: int, 
        total_files: int
    ):
        percentage = file_number / total_files
        percentage = round(percentage, 4)
        percentage *= 100
        int_percentage = int(percentage)
        self.window.write_event_value('-update_progress_bar-', int_percentage)
        self.window.write_event_value('-update_progress_percentage-', f'{file_number / float(total_files):04.2%}')

    def update_status(
            self,
            name: str,
            file_number: int,
            total_files: int
    ):
        self.window.write_event_value('-update_status-', f"[{file_number / float(total_files):04.2%}] {name:>3}")

    def send_stats(self):
        self.window.write_event_value('-ed_done_stats-', self.stats)



    def log(self, message: str, verbose_level_of_message: int) -> None:
        '''Prints the status of the extractor to stdout'''

        if self.verbose_level == 1 and verbose_level_of_message == 1:
            print(message)
        elif self.verbose_level == 2:
            if verbose_level_of_message == 1 or verbose_level_of_message == 2:
                print(message)
        elif self.verbose_level == 3:
            if verbose_level_of_message == 3 or verbose_level_of_message == 1:
                print(message)
        return

    def valid_parameters(self) -> bool:
        '''Raises ValueError when one of the parameters are invalid'''

        if not self.source_directory:
            raise ValueError('Source directory not specified') 
        if not self.game:
            raise ValueError('Game not specified')
        if self.game != 2 and self.game != 1:
            raise ValueError(f'You specified {self.game} for game. Must be 1 or 2')
        if len(self.chosen_chars) == 0:
            raise ValueError('Chosen game characters is empty')
        for char in self.chosen_chars:
            if char not in self.chars_aliases:
                raise ValueError("Chosen game character alias doesn't exist in character aliases")
        if self.export_to_file:
            if self.destination_file == None:
                raise ValueError('Destination file not specified')
        else:
            if self.destination_directory == None:
                raise ValueError('Destination directory not specified')
        if len(self.delimeter) > 1:
            raise ValueError('Only one character is allowed as delimeter')
        if len(self.header) != 2:
            raise ValueError('Header columns must be 2')
        
        # Return True at the end since all parameters passed checks
        return True

    def calculate_progress(self, current_file_num: int) -> tuple:
        '''Returns the current progress percentage'''

        percentage = current_file_num / self.total_amount_of_rpyfiles
        percentage *= 100
        percentage = round(percentage, 2)
        int_percentage = int(percentage)
        return percentage, int_percentage

    def calculate_dialog_part_stats(self, part_num: int) -> float:
        '''Returns the percentage of a character dialog in stats'''

        percentage = part_num / self.total_amount_of_dialogs
        percentage *= 100
        percentage = round(percentage, 2)
        return percentage
    
    def get_filename_from_path(self, path: str) -> str:
        '''Returns the filename from path'''
        return ntpath.basename(path)

    def get_absolute_file_path(self, file_dir_path: str, filename: str) -> str:
        '''Returns the relative path, given the directory and filename'''

        dir = os.path.dirname(__file__)
        file_path = os.path.join(dir, file_dir_path,filename)
        return file_path

    def get_file_paths(self) -> list:
        '''Returns a list containing the absolute paths of .rpy files in a directory'''

        filepaths = []
        for file in os.listdir(self.source_directory):
            if file.endswith(f'.rpy'):
                filepaths.append(self.get_absolute_file_path(self.source_directory, file))
        self.total_amount_of_rpyfiles = len(filepaths)
        return filepaths

    def strip_newline_from_text_lines(self, text_lines: list) -> list:
        '''Returns a list containing text lines of a file clean of newline symbols'''

        text_lines_stripped = []
        for text_line in text_lines:
            text_lines_stripped.append(text_line.strip())
        return text_lines_stripped

    def extract_dialogs_from_file(self, rpyfilepath: str, current_file_num: int) -> None:
        '''Extracts character dialogs from a file then outputs them into the dialog dictionary'''

        # OPEN THE FILE
        file = open(rpyfilepath, 'r', encoding='utf-8')   

        # GET ALL THE LINES OF TEXTS IN THE FILE THEN REMOVE ALL NEWLINE SYMBOLS
        lines_stripped = self.strip_newline_from_text_lines(file.readlines())

        for line in lines_stripped:
            
            # IF {i} IS FOUND IN LINE, IT BELONGS TO A ROLEPLAY SCENE
            if "{i}" in line:
                if self.exclude_roleplay_dialogs:
                    continue    # IF ROLEPLAY DIALOGS ARE EXCLUDED, WE SKIP THE LINE
                else:           # OTHERWISE IF ALLOWED, WE REMOVE {i} and {/i}
                    line = line.replace("{i}",'')       # REMOVES THE {i}
                    line = line.replace("{/i}",'')      # REMOVES THE {/i}
            
            # GET THE DIALOG BETWEEN APOSTROPHES
            dialog = re.findall('"([^"]*)"', line)

            # SKIP THE LINES THAT HAVE NO DIALOG
            if len(dialog) == 0:    
                continue

            # SOME LINES DO NOT HAVE KEYWORDS, THOSE CAUSE ERRORS SO WE SURROUND IT WITH TRY
            try:
                # SPLIT THE LINE INTO LIST OF WORDS
                line_words = line.split()
                
                for char in self.chosen_chars:
                    # DETERMINE IF THE FIRST WORD MATCHES TO THE SELECTED CHARACTER KEYWORDS
                    if line_words[0] == char:
                        if char not in self.dialogs[self.game]:   
                            # CREATE THE KEY FOR THE CHARACTER IF IT DOESN'T EXIST YET
                            # THEN APPEND THE DIALOG INSIDE OF THE CHARACTER'S DIALOG LIST
                            self.dialogs[self.game][char] = [dialog[0]]
                        else:   
                            # APPEND INSIDE CHARACTER'S DIALOG LIST
                            self.dialogs[self.game][char].append(dialog[0])

                        percentage, int_percentage = self.calculate_progress(current_file_num)
                        self.log(
                            message=f'[{percentage}%] [{self.get_filename_from_path(rpyfilepath)}] {self.chars_aliases[char]}: {dialog[0]}',
                            verbose_level_of_message=3
                        )

                        # ADD THE TOTAL AMOUNT OF DIALOG LINES
                        self.total_amount_of_dialogs += 1
            except:
                pass

        # IF CAMP BUDDY TOOLBOX PYSIMPLEGUI WINDOW OBJECT IS PASSED TO THE CONSTRUCTOR, WE UPDATE THE PROGRESS
        if self.window != None:
            self.update_status(self.get_filename_from_path(rpyfilepath), current_file_num, self.total_amount_of_rpyfiles)
            self.update_progress(current_file_num, self.total_amount_of_rpyfiles)
        return

    def export_dialogs_to_directory(self) -> None:
        '''Exports the dialogs to individual csv files to a destination directory'''

        # FOR EACH CHARACTER IN DIALOGS DICTIONARY
        for char in self.dialogs[self.game]:

            #   CREATE A NEW .CSV FILE AT DESTINATION DIRECTORY
            file = open(self.get_absolute_file_path(self.destination_directory, self.chars_aliases[char])+'.csv', 'w')
            #   CREATE A WRITER, SETS THE DELIMETER TO USER'S CHOICE
            writer = csv.writer(file, delimiter=self.delimeter)
            writer.writerow(self.header)    # WRITE THE HEADER COLUMNS
            if len(self.dialogs[self.game]) != 0:
                for dialog in self.dialogs[self.game][char]:                # FOR EACH DIALOG OF THE CHARACTER
                    writer.writerow([self.chars_aliases[char], dialog])     # WRITE THE CHARACTER'S NAME THEN THE DIALOG IN THE ROW

            file.close()    # CLOSE THE FILE
        return

    def export_dialogs_to_file(self) -> None:
        '''Exports dialogs to a destination csv file'''

        # CREATE A NEW .CSV FILE AT DESTINATION DIRECTORY
        file = open(self.destination_file, 'w')
        writer = csv.writer(file, delimiter=self.delimeter)
        writer.writerow(self.header)    # WRITE THE HEADER COLUMNS

        # FOR EACH CHARACTER IN DIALOGS DICTIONARY
        for char in self.dialogs[self.game]:
            if len(self.dialogs[self.game]) != 0:
                for dialog in self.dialogs[self.game][char]:                # FOR EACH DIALOG OF THE CHARACTER
                    writer.writerow([self.chars_aliases[char], dialog])     # WRITE THE CHARACTER'S NAME THEN THE DIALOG IN THE ROW

        file.close()    # CLOSE THE FILE
        return

    def get_stats(self) -> tuple:
        '''Returns the stats that show the amount of .rpy files, and total dialog lines per character.'''

        self.stats = {
            'Total .rpy Files': self.total_amount_of_rpyfiles,
            'Total Dialog Lines': self.total_amount_of_dialogs
        }

        for char in self.dialogs[self.game]:
            char_lines = len(self.dialogs[self.game][char])
            char_percentage = self.calculate_dialog_part_stats(char_lines)
            self.stats[f'{self.chars_aliases[char]} Dialog Count'] = char_lines
            self.stats[f'{self.chars_aliases[char]} Dialog Percentage'] = f'{char_percentage}%'
        
        message = ''
        for key in self.stats.keys(): 
            message += f'{key}: {self.stats[key]}\n'
        self.stats_str = message

        return self.stats, self.stats_str

    def extract(self) -> None:
        '''Main Method. Execute this after constructing an object from CBDialogExtractor class'''

        rpyfilepaths = self.get_file_paths()

        self.log(message='\nStarting dialog extraction...', verbose_level_of_message=1)

        current_file_num = 1
        for rpyfilepath in rpyfilepaths:
            percentage, int_percentage = self.calculate_progress(current_file_num)
            self.log(
                message=f'[{percentage}%] {self.get_filename_from_path(rpyfilepath)}',
                verbose_level_of_message=2)
            self.extract_dialogs_from_file(rpyfilepath, current_file_num)
            current_file_num += 1

        if self.export_to_file:
            self.export_dialogs_to_file()
        else:
            self.export_dialogs_to_directory()

        self.log(
                message=f'\nFinished extracting dialogs, it has been saved to: "{self.destination_file if self.export_to_file else self.destination_directory}"',
                verbose_level_of_message=1)

        self.get_stats()
        if self.show_stats:
            self.log(message=f'{self.game_aliases[self.game]}\n{self.stats_str}', verbose_level_of_message=1)

        return self.stats

def execute_as_script():
    '''
    Allows the program to be executed in a command line environment. 
    Parses the arguments / parameters then passes it to the constructor, then executes the extraction.
    
    Do not use this function in a program, construct an object from CBDialogExtractor class then execute extract()
    '''

    if __name__ == '__main__':

        parser = argparse.ArgumentParser(
                    description='Extracts character dialogs from Camp Buddy & Camp Buddy Scoutmasters Edition',
                    formatter_class=argparse.ArgumentDefaultsHelpFormatter)

        parser.add_argument('source_directory', type=str, help='Folder Containing .rpy Files')
        parser.add_argument('game', type=int, help='1 = Camp Buddy, 2 = Camp Buddy Scoutmasters Edition')
        parser.add_argument('chosen_chars', help='Characters to extract dialogs of', type=str, nargs='*')
        parser.add_argument('-r', '--exclude_roleplay_dialogs', default=True, type=lambda x: (str(x).lower() == 'true'), help='Exclude roleplay dialogs')
        parser.add_argument('-e', '--export_to_file', default=True, type=lambda x: (str(x).lower() == 'true'), help='Export the dialogs to file. If False then dialogs would be exported to directory.')   
        parser.add_argument('-d', '--destination_file', help='Export destination file path. Used if export_to_file is True. Ignored if export_to_file is False.')
        parser.add_argument('-D', '--destination_directory', help='Export destination directory. Used if export_to_file is False. Ignored if export_to_file is True.')
        parser.add_argument('-H', '--header', type=str, nargs='*', default=['name', 'dialog'], help='Header columns')
        parser.add_argument('-m', '--delimeter', type=str, default=';', help='Symbol to separate the character name and their dialog')
        parser.add_argument('-s', '--show_stats', default=True, type=lambda x: (str(x).lower() == 'true'), help='At the end of extraction, show the stats detailing the amount of .rpy files processed and total dialog lines per character are exported.')   
        parser.add_argument('-v', '--verbose_level', type=int, default=2, help='0 = no output to terminal, 1 = shows message when dialogs extraction has started and finished and where it was saved, 2 = shows the percentage progress and the current file being worked on, 3 = shows the character name and their dialog in real time as they get extracted')

        args = parser.parse_args()
        config = vars(args)
        # pprint(config, indent=2)

        cb_dialog_extractor = CBDialogExtractor(
            config['source_directory'], 
            config['game'], 
            config['chosen_chars'], 
            config['exclude_roleplay_dialogs'],
            config['export_to_file'],
            config['destination_file'], 
            config['destination_directory'], 
            config['header'], 
            config['delimeter'], 
            config['show_stats'],
            config['verbose_level'])

        cb_dialog_extractor.extract()

    else:
        
        print(f'{__name__}: {execute_as_script.__doc__}')
        return

execute_as_script()
