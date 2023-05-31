# Robert Jones
# 5.30.23
# Python 3.10.7 - 64 bit
# Make a crossword puzzle

# import PyDictionary
# from english_words import get_english_words_set
import pandas as pd
import random
import re
import itertools
from texttable import Texttable
import string

# Big List
'''
all_words = get_english_words_set(['web2'], lower=True)
all_words = dict.fromkeys(all_words,0)
for word in all_words:
    all_words[word] = len(word)
ALL_WORDS = list(all_words.items())
'''
# Small List
all_words = open('mit_words.txt').read()
all_words = all_words.split('\n')
all_words = {k: v for v, k in enumerate(all_words)}
for word in all_words:
    all_words[word] = len(word)
ALL_WORDS = list(all_words.items())

# Grid Size
GRID_SIZE = 7

# Remove words that are too long
df_all_words = pd.DataFrame(ALL_WORDS,columns=['word','len'])
DF_ALL_wORDS = df_all_words[df_all_words['len']<=GRID_SIZE]


class NoPossibleWordException(Exception):
    def __init__(self,row,message=None):
        self.message = message
        self.row = row
        message = f'No Word found for row {row}'
        super().__init__(self.message)


class CrossWord():
    grid_size = GRID_SIZE
    run_counter = 1

    def __init__(self):     
        self.all_words = ALL_WORDS
        self.df_all_words = DF_ALL_wORDS
        self.indicies_rows = []   
        self.indicies_cols = []
        self.possible_matches = []
        self.alphabet = list(string.ascii_lowercase)

    def make_grid(self):
        self.grid = []
        x = True
        while x:
            try:
                square_size = CrossWord.grid_size
                if type(square_size) == int and square_size >= 2 and square_size <= 15:
                    x = False
            except:
                print('Enter an integer between 2 and 15')
        for x in range(square_size):
            self.grid.append('0')
            for j in range(square_size-1):
                self.grid.append('0')
        self.grid = [self.grid[i:i+square_size] for i in range(0,len(self.grid),square_size)]
        percent_blank = .30
        cells_blank = round((square_size*square_size)*percent_blank)        
        counter = 0
        while counter < cells_blank: 
            blank_1 = random.randint(0,len(self.grid)-1)
            blank_2 = random.randint(0,len(self.grid)-1)
            self.grid[blank_1][blank_2] = '~'
            counter += 1
        self.max_len_words = self.df_all_words[self.df_all_words['len']==len(self.grid[0])]

    def fill_grid(self):

        def insert_regex():
            for i in range(0,len(self.grid)):
                for cell in range(0,len(self.grid)):
                    if self.grid[i][cell] == '0':
                        self.grid[i][cell] = '[a-z]'

        def get_indicies(col=None):
                if col == True:
                    flip_grid()
                index_list = []
                for i in range(0,len(self.grid)):
                    last_index = 0
                    out = []                
                    for cell, value in itertools.groupby(enumerate(self.grid[i]),lambda k:k[1]):
                        l = [*value]
                        out.append([i,cell,last_index,l[-1][0]])
                        last_index += len(l)
                        index_list.append(out)
                index_list = [item for sublist in index_list for item in sublist]
                df_index = pd.DataFrame(index_list,columns=['row','group','start_index','end_index'])
                df_index = df_index[df_index['group'] != '~']
                if col == True:
                    self.indicies_cols = df_index.drop_duplicates().values.tolist()
                    flip_grid()
                else:
                    self.indicies_rows = df_index.drop_duplicates().values.tolist()

        def print_grid():
            t = Texttable()
            t.add_rows(self.grid)
            print(t.draw())

        def flip_grid():
            self.grid = [list(i) for i in zip(*self.grid)]

        def find_words(pattern,row,testing=None):
            len_word = len(pattern)
            possible_words = self.df_all_words['word'][self.df_all_words['len']==len_word].values.tolist()
            pattern = ''.join(pattern)
            r = re.compile(pattern)
            self.possible_matches = list(filter(r.match, possible_words))
            if testing:
                return self.possible_matches                
            if self.possible_matches == []:
                print_grid()
                raise NoPossibleWordException(row=row)
            # Choose word for first row insert
            word = self.possible_matches[random.randint(0,len(self.possible_matches)-1)]
            return word

        def insert_word(word,row,start_index,end_index):
            self.grid[row][start_index:end_index+1] = word

        def get_row_letters(row,testing=None,start_index=None,end_index=None):
            if start_index is None and end_index is None:
                start_index = 0
                end_index = len(self.grid)-1
            if testing:
                testing = True
                len_possibles = {}
            pattern = []
            word_letters = []
            for cell in range(start_index,end_index+1):
                if self.grid[row][cell] != '~':
                    pattern.append(self.grid[row][cell])
                if self.grid[row][cell] == '~':
                    if pattern:
                        if testing:
                            len_possibles[cell] = find_words(pattern,row,testing)
                            pattern = []
                        else:            
                            word_letters.append(find_words(pattern,row))
                            pattern = []
                if end_index is not None:
                    if cell != '~' and cell == end_index:
                        if pattern:
                            if testing:
                                len_possibles[cell] = find_words(pattern,row,testing)
                                pattern = []
                            else:    
                                word_letters.append(find_words(pattern,row))
                                pattern = [] 

                if cell != '~' and cell == len(self.grid[row])-1:
                    if pattern:
                        if testing:
                            len_possibles[cell] = find_words(pattern,row,testing)
                            pattern = []
                        else:    
                            word_letters.append(find_words(pattern,row))
                            pattern = []
            if testing:
                return len_possibles
            
            return word_letters
  

        def next_letter(row,cell,start_index,end_index):
            possible_row_dict = {}
            for letter in self.alphabet:
                self.grid[row][cell] = letter
                possible_row = get_row_letters(row,testing=True,start_index=start_index,end_index=end_index)
                num_possibles = len(list(possible_row.values())[0])
                possible_row_dict[letter] = num_possibles
            
            flip_grid()
            possible_col_dict = {}
            for i in range(0,len(self.indicies_cols)):
                if self.indicies_cols[i][0] == cell:
                    if row >= self.indicies_cols[i][2] and row <= self.indicies_cols[i][3]:
                        start = self.indicies_cols[i][2]
                        end = self.indicies_cols[i][3]
            for letter in self.alphabet:
                self.grid[cell][row] = letter
                possible_row = get_row_letters(row=cell,testing=True,start_index=start,end_index=end)
                num_possibles = len(list(possible_row.values())[0])
                possible_col_dict[letter] = num_possibles
            flip_grid()

            # Remove value of 0 for each 
            possible_row_dict = {key:val for key, val in possible_row_dict.items() if val != 0}
            possible_col_dict= {key:val for key, val in possible_col_dict.items() if val != 0}
            # Remove values where letter does not intersect
            possible_row_dict = dict((k, possible_row_dict[k]) for k in possible_col_dict.keys() if k in possible_row_dict)
            possible_col_dict= dict((k, possible_col_dict[k]) for k in possible_row_dict.keys() if k in possible_col_dict)
            # combine both lists to see which letter is most common
            combined_possibles = {i: possible_col_dict.get(i, 0) + possible_row_dict.get(i, 0)
                for i in set(possible_col_dict).union(possible_row_dict)}
            
            # If no combinations exist
            try:
                best_letter = max(combined_possibles, key=combined_possibles.get)
            except:
                raise NoPossibleWordException(row=row)
        
            self.grid[row][cell] = best_letter

            print_grid()


        def get_next():
            for row in range(1,len(self.grid)):
                row_indicies = self.indicies_rows
                indicies_sublist = [item for item in row_indicies if item[0] == row]
                for i in range(0,len(indicies_sublist)):
                    for j in range(indicies_sublist[i][2],(indicies_sublist[i][3]+1)):
                        start = indicies_sublist[i][2]
                        stop = indicies_sublist[i][3]
                        next_letter(row,cell=j,start_index=start,end_index=stop)       


        def print_words():
            row_words = []
            for i in range(0,len(self.indicies_rows)):
                row = self.indicies_rows[i][0]
                start = self.indicies_rows[i][2]
                end = self.indicies_rows[i][3]
                word = self.grid[row][start:end+1]
                str_word = ''.join(map(str,word))
                row_words.append(str_word)

            flip_grid()
            col_words = []
            for i in range(1,len(self.indicies_cols)):
                row = self.indicies_cols[i][0]
                start = self.indicies_cols[i][2]
                end = self.indicies_cols[i][3]
                word = self.grid[row][start:end+1]
                str_word = ''.join(map(str,word))
                col_words.append(str_word)
            flip_grid()
            

            print(f'row words = {[x for x in row_words if len(x) > 1]}')
            print(f'col words = {[x for x in col_words if len(x) > 1]}')

            for word in row_words:
                if word not in self.df_all_words['word'].values.tolist():
                    print(f'{word} not in list')

            for word in col_words:
                if word not in self.df_all_words['word'].values.tolist():
                    print(f'{word} not in list')   


        def insert_first_row(row=0):
            row_indicies = self.indicies_rows
            indicies_sublist = [item for item in row_indicies if item[0] == row]
            row_letters = get_row_letters(row=row)
            for j in range(0,len(indicies_sublist)):
                start_index = indicies_sublist[j][2]
                end_index = indicies_sublist[j][3]
                word = row_letters[j]
                insert_word(word,row,start_index,end_index)


        def get_clues():
            # To Do
            pass
        def guess_word():
            # To Do
            pass
        def colorize():
            # To Do
            pass

        insert_regex()
        get_indicies()
        get_indicies(col=True)
        insert_first_row()
        get_next()
        print_grid()
        print_words()
        return 'Completed'


words = None # Initalize word list outside of __init__, then pass into make grid
run = True
run_count = 1
while run:
    try:
        instance = CrossWord()
        instance.make_grid()
        if instance.fill_grid() == 'Completed':
            print(f'Completed in {run_count} runs')            
            run = False
    except NoPossibleWordException:
        run_count += 1

# To improve
'''
step 1 - Take top n (maybe top 3) from combined_possibles 
step 2 - see where to go from there.
OR
try inserting first column?
idk
'''