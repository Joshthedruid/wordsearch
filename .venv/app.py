#TODO:
    #inclusive letter selection breaks for some reason, seemingly at random.choice(my_letters)
    #bugs might occur if @ is present in wordlist items?
    #general validation:
        #if wordlist is too short/long
        #if words are too short/long
        #if words have too few letters for inclusive to ever resolve (if the only word in the puzzle is "NO", the puzzle is pretty much only valid if every fill letter is "N" or "O")
        #if words contain each other (if "PEACH" and "EACH" are in wordlist, there will almost always be two "EACH"s, which fails one and only one validation)
    #make wordlist printable as .doc / .pdf?
    #improve algorithym to contain crossovers
    #diagonals / backwards options
    #make exact size of word search customizeable (plus validation for fuckity user entries)
    #if other things are being made to be customizeable, probably condense all that and word fill type in an "advanced options" menu
    #the starting text in the wordlist HTML area is kinda clunky
    #clean up unneccesary files to make project more presentable
    #comment out code to make things more presentable
    #consider breaking code up into separate .py files (especially for wordsearch logic vs coding)
    #get project onto GitHub
    #get project onto LinkedIn


#header code to get Flask running
import random
from flask import Flask, render_template, redirect, url_for, request
app = Flask(__name__) 

random.seed()
        
#flags, to change what sort of word search you're creating
bonus_size = 2 #increases the matrix size beyond the usual minimum parameters

#lazy matrix size estimator, makes sure matrix is a square neither shorter than the number of items or the length of the longest
#better version could account for criss-crosses, multiple small words, or desired complexity
def matrix_ws(wordlist):
    return_int = 0
    for item in wordlist:
        if len(item) > return_int:
            return_int = len(item)
    if return_int < len(wordlist):
        return_int = len(wordlist)
    return(return_int)

#adds a word horizontally into the word search at a random location.  ensures there's enough room at the chosen location first
def weave_ws(ws, word):
    my_row = random.randint(0,len(ws)-1)
    my_col = random.randint(0,len(ws)-len(word))
    spacer = 0
    for char in word:
        ws[my_row][my_col + spacer] = char
        spacer += 1
    return(ws)

#same as weave_ws, but vertical.  NOT YET IMPLEMENTED
def weave_ver_ws(ws,word):
    my_row = random.randint(0,len(ws)-len(word))
    my_col = random.randint(0,len(ws)-1)
    spacer = 0
    for char in word:
        ws[my_row + spacer][my_col] = char
        spacer += 1
    return(ws)
    
#same as weave_ws, but diagonal.  NOT YET IMPLEMENTED
def weave_dia_ws(ws,word):
    my_row = random.randint(0,len(ws)-len(word))
    my_col = random.randint(0,len(ws)-len(word))
    spacer = 0
    for char in word:
        ws[my_row + spacer][my_col + spacer] = char
        spacer += 1
    return(ws)

#define letterlist if letters_inclusive_to_wordlist == True
def lettersearch(char, wordlist):
    for line in wordlist:
        for item in line:
            if item.find(char) != -1:
                return char
    return ""

#main body function, defines wordsearch size, adds each word, then confirms the wordsearch is valid.  if it's not, it repeats
def makewordsearch(letterfill, wordlist):
    height = matrix_ws(wordlist) + bonus_size
    width = height
    
    ready = False
    while not ready:
        ws = []
        for y in range(height):
            ws_ln = []
            for x in range(width):
                ws_ln.append("@")
            ws.append(ws_ln)
        for word in wordlist:
            my_list = [True,False]
            my_switch = random.choice(my_list)
            if my_switch:
                ws = weave_ws(ws, word)
            else:
                ws = weave_ver_ws(ws, word)
        if valid_ws(ws, wordlist):
            ready = True
        else:
            print("Try Again")
            ws.clear()
    
    #create letterlist if letters_inclusive_to_wordlist == True
    if letterfill == "inclusive":
        letterlist = "qwertyuiopasdfghjklzxcvbnm"
        my_letters = ""
        for char in letterlist:
            my_letters += lettersearch(char,wordlist)
    
    #this block adds nonsense letters, comment out as needed for testing
    at_tickup = 0
    for row in ws:
        for x in range(len(row)):
            if row[x] == "@":
                if letterfill == "inclusive":
                    ws[at_tickup][x] = random.choice(my_letters)
                elif letterfill == "smart":
                    ws[at_tickup][x] = random.choices("eariotnscludpmhgbfywkvxzjq", weights=[11.1607,8.4966,7.5809,7.5448,7.1635,6.9509,6.6544,5.7351,5.4893,4.5388,3.6308,3.3844,3.1671,3.0129,3.0034,2.4705,2.0720,1.8121,1.7779,1.2899,1.1016,1.0074,0.2902,0.2722,0.1965,0.1961],k=1)[0]
                elif letterfill == "rares":
                    ws[at_tickup][x] = random.choice("wertyuiopasdfghlcbnm")
                else:
                    ws[at_tickup][x] = random.choice("qwertyuiopasdfghjklzxcvbnm")
        at_tickup += 1
        
    return(ws)

#iterate through and output word search 2D list
def print_ws(ws):
    return_string = "<table><body>"
    for row in ws:
        return_string += "<tr>"
        for char in row:
            return_string += "<th>" + char.upper() + "</th>"
        return_string += "</tr>"
    return_string += "</body></table>"
    return return_string

#returns true if each word in wordlist exists in the wordsearch
def valid_ws(ws, wordlist):
    for word in wordlist:
        if not valid_word(ws,word):
            return(False)
    return(True)

#checks each row for the given word and returns false if no row contains it
#!! only works for rows at the moment !!
#if columns, diagonals, or backwards words are implemented, this will need updating
def valid_word(ws, word):
    #horizontal check
    count = 0
    for row in ws:
        restring = "" #restring just turns the row back into a string, instead of a list
        for char in row:
            restring += char
        if restring.find(word) > -1:
            count += 1
    #TODO figure out same mechanism as above, but for columns
    for column in range(len(ws[0])):
        restring = ""
        for step in range(len(ws)):
            restring += ws[step][column]
        if restring.find(word) > -1:
            count += 1
    if count == 1:
        return(True)
    else:
        return(False) #requires exactly 1 instance of word



#routing
@app.route("/", methods=["POST","GET"])
def home():
    if request.method == "POST":
        letterfill = request.form["letter_fill"]
        wordlist = request.form["wordlist"].split()
        
        vegetables = ["broccoli","spinach","pepper","kale","lettuce"]
        export = print_ws(makewordsearch(letterfill,wordlist))
        
        return export
    else:
        return render_template('home.html')

#route to wordsearch webpage
@app.route("/<wordlist>")
def wordsearch(wordlist):
    return render_template('wordsearch.html', wordlist = wordlist)