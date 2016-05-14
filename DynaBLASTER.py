#!/usr/bin/env python3

"""Program that recreates the multiplayer aspect of the DOS game DynaBlaster.
   Tactfully place bombs against your opponent and become the bomber champ!
   Author: Abel Svoboda
   Date: 08/07/15
"""

from tkinter import PhotoImage, Tk, Canvas, Label, StringVar, IntVar, Frame
from time import clock
from random import randint
from PIL import Image, ImageTk

import json


ITEMS = ('+bombs', '+power')


class Graphics(object):
    def __init__(self, canvas, rows, cols, size, window):
        '''initialises the graphics object and its properties'''
        self.canvas = canvas
        self.window = window
        self.rows = rows*2+1
        self.cols = cols*2+1
        self.size = size/2
        self.label = {}
        self.label_vars = {}
        self.icons = (ImageTk.PhotoImage(file='png/faceicon0.png'),
                      ImageTk.PhotoImage(file='png/faceicon1.png'))
        self.draw_static_grid()
        self.draw_changing_grid()
        self.info_labels()
        self.make_creator_label()

    def make_creator_label(self):
        self.canvas.create_text(self.cols*self.size/2+self.size/2,
                                self.rows*self.size+self.size*2/3+2,
                                text='Created by Abel Svoboda, 08/07/15')

    def draw_static_grid(self):
        '''draws the grid that is made at the start of the game'''
        hardblock = PhotoImage(file='gifs/hardblock.gif')
        label = Label(image=hardblock)
        label.image = hardblock #keeping a reference
        self.regular = {}
        self.absolute = {}
        for col in range(self.cols):
            for row in range(self.rows):
                left = col * self.size
                right = left + self.size+.5*self.size
                top = row * self.size
                bot = top + self.size+.5*self.size
                left += .5*self.size
                top += .5*self.size

                if row%2==0 and col%2==0 or \
                   row==0 or col==0 or \
                   row==self.rows-1 or col==self.cols-1: #hardblock
                    self.absolute[(col-1,row-1)] = self.canvas.create_image(
                        (left+right)/2,(top+bot)/2,image=hardblock)
                else: #walkable
                    self.regular[(col-1,row-1)] = self.canvas.create_rectangle(
                        left,top,right,bot,fill='#307100',width=0)

    def draw_changing_grid(self):
        '''draws the grid that is made at the start of each round'''
        softblock = PhotoImage(file='gifs/softblock.gif')
        label = Label(image=softblock)
        label.image = softblock #keeping a reference
        self.rocks = {}
        for col in range(self.cols):
            for row in range(self.rows):
                left = col * self.size
                right = left + self.size+.5*self.size
                top = row * self.size
                bot = top + self.size+.5*self.size
                left += .5*self.size
                top += .5*self.size

                if (row==1 or row==2) and (col==1 or col==2) or \
                   (row==self.rows-2 or row==self.rows-3) and (col==self.cols-2 or col==self.cols-3) or \
                   row%2==0 and col%2==0 or \
                   row==0 or col==0 or row==self.rows-1 or col==self.cols-1:
                    pass
                elif randint(0,100) < 50: #soft block density
                    self.rocks[(col-1,row-1)] = self.canvas.create_image(
                        (left+right)/2,(top+bot)/2,image=softblock)

    def info_labels(self):
        '''creates some labels on the UI'''
        self.time_var = StringVar()
        self.time_var.set(0)
        time_label = Label(self.window,textvariable=self.time_var,
                           fg='white', bg='black',
                           font=('DINPro-Black',20), width=8)
        time_label.grid(row=0,column=2)
        self.pause_label = Label(self.window,text='PAUSE',
                                 fg='white',bg='black',
                                 font=('DINPro-Black',20),width=8)

    def pause_game(self):
        '''changes the UI to show the game is paused'''
        if 'row' in self.pause_label.grid_info():
            self.pause_label.grid_forget()
        else:
            self.pause_label.grid(row=0,column=2)

    def end_round_kill_screen(self, canvas, string, player):
        '''creates the end of round kill screen'''
        self.end_round_frame = Frame(self.window, background='#AF0000',bd=4)
        self.end_round_frame.grid(row=1, column=0, columnspan=6)
        if player is not None:
            winner_image = Label(self.end_round_frame,
                                 image=self.icons[player.player_number-1],
                                 borderwidth=18)
            winner_image.grid(row=0, column=0)
        end_kill_label=Label(self.end_round_frame, text=string+' ',
                             font=('DINPro-Black',25),borderwidth=9)
        end_kill_label.grid(row=0, column=1)

    def kill_end_round_screen(self):
        '''removes the end of round screen'''
        self.end_round_frame.grid_forget()

    def create_player_score(self, player_num):
        '''creates a score counter for a player'''
        col = player_num*3
        string = 'player'+str(player_num+1)
        self.label_vars[string] = IntVar()
        self.label_vars[string].set(0)
        self.label[string] = []
        self.label[string].append(Label(self.window, image=self.icons[player_num]))
        self.label[string][0].grid(row=0,column=col,sticky='e')
        self.label[string][0].configure(background='black')
        self.label[string].append(col)
        self.label[string].append(Label(self.window,
                                        textvariable=self.label_vars[string],
                                        borderwidth=6, padx=3,
                                        font=('DINPro-Black', 16),
                                        fg='black', bg='green'))
        self.label[string][2].grid(row=0,column=col+1,sticky='w',padx=0)
        self.label[string][2].configure(highlightcolor='white')

    def settings(self):
        '''settings button (not complete)'''
        button = Button(self.window, text='settings')
        button.grid(row=0, column=4,sticky='e',columnspan=2, padx=(0,5))
        button.columnconfigure(10,weight=9)


class Board(object):
    def __init__(self, canvas, size, num_rows, num_cols, c_width, c_height):
        '''Initialises the board and its attributes'''
        self.canvas = canvas
        self.size = size
        self.c_width = c_width
        self.c_height = c_height
        self.num_rows = num_rows
        self.num_cols = num_cols
        self.create_board()

    def create_board(self):
        '''draws the lines that the player/s use for movement'''
        self.hor_lines = []
        for i in range(self.num_rows):
            y = i*self.size
            y+=self.size
            line = self.canvas.create_line(0,y,self.c_width,y)
            self.canvas.itemconfig(line, state='hidden')
            self.hor_lines.append(line)
        self.ver_lines = []
        for i in range(self.num_cols):
            x = i*self.size
            x+=self.size
            line = self.canvas.create_line(x,0,x,self.c_height)
            self.canvas.itemconfig(line, state='hidden')
            self.ver_lines.append(line)


class Player(object):
    items = {}
    bombs = {}
    players = []
    def __init__(self, canvas, board, width, graphics, col, row):
        '''Initialises the player and its attributes'''
        self.canvas = canvas
        self.start_col = col
        self.start_row = row
        self.players.append(self)
        self.player_number = len(self.players)
        self.board = board
        self.graphics = graphics
        self.width = width
        self.player_size = width/5
        self.direction = 'up'
        self.v_vector = [0,0]
        self.key_pressed=False
        self.rocks_dict = graphics.rocks
        self.regular_dict = graphics.regular
        self.absolute_dict = graphics.absolute
        self.pause=False
        self.round_ended=False
        self.paused_time = 0
        self.round_time = 0
        self.dead = False
        self.afters = []
        self.points = 0
        self.fire = {}
        self.fire_counter = 0
        for i in ITEMS:
            Player.items[i]={}
        self.power = 2
        self.num_bombs = 1
        self.bombs_placed = 0
        self.time = 0
        #bomb images
        self.bombdrop0 = ImageTk.PhotoImage(file='png/bombdrop0.png')
        self.bomb_images = [ImageTk.PhotoImage(file='png/bombdrop0.png'),
                            ImageTk.PhotoImage(file='png/bombdrop1.png'),
                            ImageTk.PhotoImage(file='png/bombdrop2.png')]
        #player images
        self.positions = ['forw','back','right','left']
        self.position = None#'forw'
        self.player_images = {}

        for position in self.positions:
            images_of_position = []
            for i in range(3):
                images_of_position.append(ImageTk.PhotoImage(
                    file='png/'+str(self.player_number)+position+str(i)+'.png'))
            self.player_images[position] = images_of_position
        #dead images
        self.death_images = []
        for i in range(8):
            self.death_images.append(ImageTk.PhotoImage(
                file='png/'+str(self.player_number)+'dead'+str(i)+'.png'))
        #soft block images
        self.soft_block_images = []
        for i in range(1,6):
            self.soft_block_images.append(
                ImageTk.PhotoImage(file='png/softblock'+str(i)+'.png'))
        #fire images
        self.fire_images={}
        fire_text = ['hor','vert','mid','top','bot','left','right']
        for text in fire_text:
            self.fire_images[text]=[]
            num_images=4
            if text == 'mid':
                num_images=5
            for num in range(num_images):
                self.fire_images[text].append(
                    ImageTk.PhotoImage(file='fire/'+text+str(num)+'.png'))
        #scoreboard
        self.graphics.create_player_score(self.players.index(self))
        #images
        self.images = {}
        for i in ITEMS:
            self.images[i]=[]
            self.images[i].append(PhotoImage(file='gifs/'+i+'0.gif'))
            self.images[i].append(PhotoImage(file='gifs/'+i+'1.gif'))

        hobo = ImageTk.PhotoImage(file='png/'+str(self.player_number)+'forw0.png')
        l = Label(image=hobo)
        l.image = hobo # keep a reference! doesnt work without
        left, top, right, bot = self.canvas.coords(self.regular_dict[(col,row)])

        self.player = self.canvas.create_rectangle(
            left, top, right, bot, fill='white')
        self.canvas.itemconfig(self.player, state='hidden')
        self.player_image = self.canvas.create_image(
            (left+right)/2,(top+bot)/2-4, image=self.player_images['forw'][0])

        self.animate_player()
        self.movement()

    def key_press(self, key):
        '''functionality for key press of movement keys'''
        if key == 'Up':
            self.v_vector = [0,-1]
            self.position = 'back'
        elif key == 'Down':
            self.v_vector = [0,1]
            self.position = 'forw'
        elif key == 'Left':
            self.v_vector = [-1,0]
            self.position = 'left'
        elif key == 'Right':
            self.v_vector = [1,0]
            self.position = 'right'

    def key_release(self, key):
        '''functionality for key realease of movement keys'''
        if key == 'Up':
            self.v_vector[1] = 0
            self.position = None
        elif key == 'Down':
            self.v_vector[1] = 0
            self.position = None
        elif key == 'Left':
            self.v_vector[0] = 0
            self.position = None
        elif key == 'Right':
            self.v_vector[0] = 0
            self.position = None

    def animate_player(self,position='forw',x=0,num=0):
        '''animates the player'''
        if self.position is not None:
            position = self.position
            num = [0,1,0,2][int(x)]
            x+=0.075
            if int(x)==4:
                x=0
        else:
            num=0
            x=0.999
        if not self.dead and not self.round_ended:
            self.canvas.itemconfig(self.player_image,image=self.player_images[position][num])
            self.after(10,lambda:self.animate_player(position,x))

    def after(self, time, function, num_loops=-1):
        '''like the canvas.after method but incorporates pause functionality'''
        loop_time = 5 #ms
        if num_loops == -1:
            num_loops = time // loop_time
        if num_loops == 0:
            function()# Call it
            return
        if not self.pause:
            num_loops -= 1
            new_time = time-loop_time
        else:
            new_time = time
        self.canvas.after(loop_time, self.after, new_time, function, num_loops)

    def place_bomb(self, event):
        '''places a bomb when a key is pressed if conditions are met'''
        if self.bombs_placed < self.num_bombs and not self.round_ended and not self.dead and not self.pause:
            col = self.row_col[0]
            row = self.row_col[1]
            if (col,row) not in self.bombs:
                left, top, right, bot = self.canvas.coords(
                    self.regular_dict[(col,row)])
                bomb = self.canvas.create_image(
                    (left+right)/2,(top+bot)/2,image=self.bombdrop0)
                self.bombs[(col,row)]=bomb
                self.animate_bomb(col,row)
                self.bombs_placed += 1
        elif self.round_ended:
            self.end_round()
            self.graphics.kill_end_round_screen()

    def animate_bomb(self, col, row, counter=0, bomb_num=1, reverse=True):
        '''animates a bomb'''
        if (col,row) not in self.bombs or self.round_ended:
            return
        elif counter < 2700:
            self.canvas.itemconfig(self.bombs[(col,row)],
                                   image=self.bomb_images[bomb_num])
            counter += 210
            if reverse:
                bomb_num -= 1
                if bomb_num==0:
                    reverse = False
            else:
                bomb_num += 1
                if bomb_num==2:
                    reverse = True
            self.after(210, lambda:self.animate_bomb(col,row,counter,
                                                     bomb_num,reverse))
        else:
            self.destroy_blocks(col,row)

    def destroy_blocks(self, col, row):
        '''determines where fire should go and what it will affect'''
        for player in self.players:
            if player.round_ended:
                return
        if (col,row) in self.bombs:
            self.canvas.delete(self.bombs[(col,row)])
            del self.bombs[(col,row)]
            self.bombs_placed -= 1
            fire_counter = self.fire_counter
            self.fire_counter += 1
            self.destroy_blocks_per_side(col, row, 1, 0, 'right', 'hor',fire_counter)
            self.destroy_blocks_per_side(col, row, -1, 0, 'left', 'hor',fire_counter)
            self.destroy_blocks_per_side(col, row, 0, 1, 'bot', 'vert',fire_counter)
            self.destroy_blocks_per_side(col, row, 0, -1, 'top', 'vert',fire_counter)
            self.after(500, lambda:self.remove_fire(fire_counter))

    def destroy_blocks_per_side(self, col, row, d1, d2, end, side, fire_counter):
        '''determines where fire should go and what it will affect for a specific direction'''
        left, top, right, bot = self.canvas.coords(self.regular_dict[(col,row)])
        if fire_counter not in self.fire:
            self.fire[fire_counter] = []
        self.create_fire(fire_counter, 'mid', col, row)
        for i in range(1,self.power+1):
            if (col+i*d1,row+i*d2) in self.absolute_dict:#if fire touches a hard block
                break
            if (col+i*d1,row+i*d2) in self.bombs:#if fire touches another bomb
                self.destroy_blocks(col+i*d1,row+i*d2)
            for p in Player.items:
                if (col+i*d1,row+i*d2) in Player.items[p]:#if fire touches an item
                    self.use_item(p,(col+i*d1,row+i*d2),False)
            if i==self.power:
                side = end
            if (col+i*d1,row+i*d2) in self.rocks_dict:
                self.delete_rocks(col+i*d1,row+i*d2)
                break
            self.create_fire(fire_counter, side, col+i*d1,row+i*d2)

    def create_fire(self, fire_counter, image_type, col, row):
        '''creates a specific fire at a specific location'''
        left, top, right, bot = self.canvas.coords(self.regular_dict[(col,row)])
        self.fire[fire_counter].append(self.canvas.create_image(
            (left+right)/2,(top+bot)/2,image=self.fire_images[image_type][0]))
        list_num = len(self.fire[fire_counter])-1
        for player in self.players:
            if (col,row) == player.row_col:#if fire touches the player
                player.die()
        self.after(125,lambda:self.animate_fire(
            fire_counter, image_type, list_num, col, row))

    def animate_fire(self, fire_counter, image_type, list_num, col, row, counter=0):
        '''animates the fire'''
        if counter < 4:
            for player in self.players:
                if (col,row) == player.row_col:#if fire touches the player
                    player.die()
            self.canvas.itemconfig(self.fire[fire_counter][list_num],
                                   image=self.fire_images[image_type][counter])
            self.after(125,lambda:self.animate_fire(
                fire_counter,image_type, list_num, col, row, counter+1))

    def remove_fire(self, fire_counter):
        '''removes the fire from a specific bomb'''
        for i in self.fire[fire_counter]:
            self.canvas.delete(i)
        del self.fire[fire_counter]

    def die(self):
        '''handles the death of the player'''
        if not self.dead:
            self.dead = True
            self.after(50, self.animate_death)
            num_alive = 0
            for player in self.players:
                if not player.dead:
                    num_alive += 1
            if num_alive < 2:
                num_dead = False
                for player in self.players:
                    if player.dead:
                        num_dead += 1
                if num_dead < 2:
                    self.after(3000, self.end_round_screen)

    def end_round_screen(self):
        '''determines data used for the end of round kill screen'''
        alive = None
        for player in self.players:
            if not player.dead:
                alive = player

        if alive is not None:
            alive.points += 1
            self.graphics.label_vars['player'+str(alive.player_number)].set(alive.points)
            string = 'wins!'
        else:
            string = 'Draw'

        for player in self.players:
            player.round_ended = True
        self.graphics.end_round_kill_screen(self.canvas,string,alive)

    def animate_death(self, count=0, num_flaps=3):
        '''animates the player on death'''
        if count == 2 and num_flaps > 0:
            count = 0
            num_flaps -= 1
        if count < 8:
            self.canvas.itemconfig(self.player_image,image=self.death_images[count])
            self.after(130, lambda:self.animate_death(count+1, num_flaps))
        else:
            self.canvas.itemconfig(self.player_image,state='hidden')

    def end_round(self):
        '''resets the round to play a new round'''
        for i in self.bombs:
            self.canvas.delete(self.bombs[i])
        self.bombs = {}
        for i in Player.items:
            for item in Player.items[i]:
                self.canvas.delete(Player.items[i][item])
        Player.items={}

        for i in ITEMS:
            Player.items[i]={}

        for i in self.rocks_dict:
            self.canvas.delete(self.rocks_dict[i])
        self.graphics.draw_changing_grid()

        for player in self.players:
            player.rocks_dict = self.graphics.rocks
            left, top, right, bot = player.canvas.coords(
                player.regular_dict[(player.start_col,player.start_row)])
            player.canvas.coords(player.player, left, top, right, bot)
            player.canvas.coords(player.player_image, (left+right)/2,(top+bot)/2-4)

            player.canvas.itemconfig(player.player_image,state='normal')
            player.canvas.itemconfig(player.player_image,
                                     image=self.player_images['forw'][0])
            player.dead=False
            player.canvas.tag_raise(player.player_image)
            player.round_ended = False
            player.bombs_placed = 0
            player.num_bombs = 1
            player.power = 2
            player.animate_player()
            player.movement()
            player.round_time = clock()
            player.paused_time = 0

    def drop_item(self, col, row):
        '''creates an item'''
        length = len(ITEMS)
        chance = randint(0,99)
        segment = 100/length
        for i in range(length):
            if chance >= i*segment and chance < (i+1)*segment:
                item_name = ITEMS[i]
        left, top, right, bot = self.canvas.coords(self.regular_dict[(col,row)])

        item = self.canvas.create_image((left+right)/2,(top+bot)/2,image=self.images[item_name][0])
        Player.items[item_name][(col,row)]=item
        self.animate_item(col,row,item_name)

    def use_item(self, item, col_row, use=True):
        '''removes the item, gaining properties if necessary'''
        if item=='+power':
            self.canvas.delete(Player.items['+power'][(col_row)])
            del Player.items['+power'][(col_row)]
            if use:
                self.power += 1
        elif item=='+bombs':
            self.canvas.delete(Player.items['+bombs'][(col_row)])
            del Player.items['+bombs'][(col_row)]
            if use:
                self.num_bombs += 1

    def delete_rocks(self, col, row):
        '''destroys the rock and does other necessary things
        related to block destruction, e.g. item drops.'''
        self.animate_soft_block_death(col, row)
        chance = randint(0,99)
        if chance <= 25:
            self.drop_item(col, row)

    def animate_soft_block_death(self, col, row, counter=0):
        '''animates the destruction of a soft block'''
        try:
            if counter < 5:
                self.canvas.itemconfig(self.rocks_dict[(col,row)], image=self.soft_block_images[counter])
                self.after(120,lambda:self.animate_soft_block_death(col, row, counter+1))
            else:
                self.canvas.delete(self.rocks_dict[(col,row)])
                del self.rocks_dict[(col,row)]
        except IndexError:
            pass
        except KeyError:
            pass

    def get_row_col(self, ver_line_num, hor_line_num):
        '''returns the current column and row of the player'''
        return round(ver_line_num*2), round(hor_line_num*2)

    def animate_item(self, col, row, item, count=0):
        '''animates the item'''
        if item in Player.items:
            if (col,row) in Player.items[item]:
                if count > 1:
                    count = 0
                self.canvas.itemconfig(Player.items[item][(col,row)],image=self.images[item][count])
                self.after(240, lambda:self.animate_item(col, row, item, count+1))

    def movement(self):
        '''handles the movement of the player'''

        if self.v_vector == [0,-1]:
            self.position = 'back'
        elif self.v_vector == [0,1]:
            self.position = 'forw'
        elif self.v_vector == [-1,0]:
            self.position = 'left'
        elif self.v_vector == [1,0]:
            self.position = 'right'

        self.centre = self.get_centre()

        #near vertical line
        near_ver_line, ver_line_num = self.near_line(0)
        if not near_ver_line:
            self.v_vector[1] = 0
        #near horizontal line
        near_hor_line, hor_line_num = self.near_line(1)
        if not near_hor_line:
            self.v_vector[0] = 0

        self.row_col = self.get_row_col(ver_line_num,hor_line_num)

        self.stop_player(ver_line_num, 0) #stop player at top/bot boundaries
        self.stop_player(hor_line_num, 1) #stop player at left/right boundaries

        #picking up item
        for i in Player.items:
            if self.row_col in Player.items[i]:
                self.use_item(i, self.row_col)

        #stops player when meeting a soft block
        self.stop_player_at_tile(self.rocks_dict, ver_line_num, hor_line_num)
        #stops player when meeting a bomb
        self.stop_player_at_tile(self.bombs, ver_line_num, hor_line_num)

        #gets player to the centre of the horizontal line
        if near_hor_line:
            self.get_player_to_middle(self.board.hor_lines, round(hor_line_num), 1)
        #gets player to the centre of the horizontal line
        if near_ver_line:
            self.get_player_to_middle(self.board.ver_lines, round(ver_line_num), 0)

        if not self.dead and not self.round_ended:
            self.move(self.v_vector[0], self.v_vector[1])
            self.after(round(1000/60), self.movement)

    def clock(self):
        '''determines the value on the clock'''
        self.time_value = clock() - self.paused_time - self.round_time
        second = int(self.time_value % 60)
        if second < 10:
            second = '0'+str(second)
        minute = round(self.time_value//60)
        time = '{}:{}'.format(minute, second)
        self.graphics.time_var.set(time)

    def move(self, x, y):
        '''moves the player on the x-y axis'''
        x*=2
        y*=2
        self.canvas.move(self.player, x, y)
        self.canvas.move(self.player_image, x, y)

    def stop_player(self, line_num, dimension):
        '''stops the player at the boundaries and other blockades'''
        if dimension == 0:
            row_col = self.board.num_cols-1
        elif dimension == 1:
            row_col = self.board.num_rows-1
        #stop player at left/top boundary
        if line_num <= 0:
            if self.v_vector[dimension] < 0:
                self.v_vector[dimension] = 0
        #stop player at right/bot boundary
        if line_num >= row_col:
            if self.v_vector[dimension] > 0:
                self.v_vector[dimension] = 0

    def stop_player_at_tile(self, tile_type, ver_line_num, hor_line_num):
        '''stops the player at tile types'''
        col = self.row_col[0]
        row = self.row_col[1]
        if self.v_vector[0]<0:
            if (col-1,row) in tile_type:
                if ver_line_num*2 <= col:
                    self.v_vector[0] = 0
        elif self.v_vector[0]>0:
            if (col+1,row) in tile_type:
                if ver_line_num*2 >= col:
                    self.v_vector[0] = 0
        elif self.v_vector[1] < 0:
            if (col,row-1) in tile_type:
                if hor_line_num*2 <= row:
                    self.v_vector[1] = 0
        elif self.v_vector[1] > 0:
            if (col,row+1) in tile_type:
                if hor_line_num*2 >= row:
                    self.v_vector[1] = 0

    def near_line(self, dimension):
        '''returns a boolean whether the player is near a line
           returns the line number of said line'''
        near_line = False
        size = self.board.size
        line_num = self.centre[dimension] / size - 1
        if round(line_num) - line_num > -0.4 and round(line_num) - line_num < 0.4:
            near_line = True
        return near_line, line_num

    def get_player_to_middle(self, lines, line_num, d1):
        '''gets player to the centre of the column or row'''
        d2 = abs(d1-1)
        if self.v_vector[d2] != 0:
            dif_to_line = self.centre[d1] - self.canvas.coords(lines[line_num])[d1]
            if dif_to_line < 0:
                self.move(d2, d1)
            elif dif_to_line > 0:
                self.move(-d2, -d1)

    def get_centre(self):
        '''returns the position of the player on the canvas'''
        left, top, right, bot = self.canvas.coords(self.player)
        centre = [(left+right)/2, (top+bot)/2]
        return centre

    def pause_game(self, event=0):
        '''pauses/unpauses the functionalities of the player'''
        if self.pause:
            self.pause = False
            self.paused_time += clock() - self.pause_time
        else:
            self.pause = True
            self.pause_time = clock()


def pause_game(player1, player2, graphics):
    '''pauses/unpauses the functionalities of the game'''
    dead=False
    for player in player1.players:
        if player.dead:
            dead=True
    if not dead:
        graphics.pause_game()
        player1.pause_game()
        player2.pause_game()

def key_release_of(key):
    key_val = key.strip()[1:-1]   # Strip angle brackets
    return "<KeyRelease-" + key_val + ">"

def main():
    '''runs the program'''
    square_width = 64
    num_cols = 7
    num_rows = 6
    canvas_width = (num_cols+1)*square_width
    canvas_height = (num_rows+1)*square_width

    window = Tk()
    window.configure(background='black')
    window.title("DynaBLASTER")
    window.resizable(0,0) #removes maximize option
    #window.iconbitmap('icon.ico')
    #window.tk.call('tk', 'scaling', 20.0)

    canvas = Canvas(window, width=canvas_width, highlightthickness=0,
                    height=canvas_height, background='#717171')
    canvas.grid(row=1,column=0, columnspan=5)

    graphics = Graphics(canvas, num_rows, num_cols, square_width, window)
    board = Board(canvas, square_width, num_rows, num_cols,
                  canvas_width, canvas_height)
    col=0
    row=0
    player1 = Player(canvas, board, square_width, graphics, col, row)
    col = graphics.cols - 3
    row = graphics.rows - 3
    player2 = Player(canvas, board, square_width, graphics, col, row)

    # Import settings from bindings file
    bindings_file = open('bindings.json')
    p1_bindings, p2_bindings, gen_bindings = json.load(bindings_file)

    window.bind(key_release_of(p1_bindings["Up"]), lambda event:player1.key_release('Up'))
    window.bind(key_release_of(p1_bindings["Down"]), lambda event:player1.key_release('Down'))
    window.bind(key_release_of(p1_bindings["Left"]), lambda event:player1.key_release('Left'))
    window.bind(key_release_of(p1_bindings["Right"]), lambda event:player1.key_release('Right'))
    window.bind(p1_bindings["Up"], lambda event:player1.key_press('Up'))
    window.bind(p1_bindings["Down"],lambda event:player1.key_press('Down'))
    window.bind(p1_bindings["Left"], lambda event:player1.key_press('Left'))
    window.bind(p1_bindings["Right"], lambda event:player1.key_press('Right'))
    window.bind(p1_bindings["Bomb"], player1.place_bomb)

    window.bind(key_release_of(p2_bindings["Up"]), lambda event:player2.key_release('Up'))
    window.bind(key_release_of(p2_bindings["Down"]), lambda event:player2.key_release('Down'))
    window.bind(key_release_of(p2_bindings["Left"]), lambda event:player2.key_release('Left'))
    window.bind(key_release_of(p2_bindings["Right"]), lambda event:player2.key_release('Right'))
    window.bind(p2_bindings["Up"], lambda event:player2.key_press('Up'))
    window.bind(p2_bindings["Down"], lambda event:player2.key_press('Down'))
    window.bind(p2_bindings["Left"], lambda event:player2.key_press('Left'))
    window.bind(p2_bindings["Right"], lambda event:player2.key_press('Right'))
    window.bind(p2_bindings["Bomb"], player2.place_bomb)

    window.bind(gen_bindings["Pause"], lambda event:pause_game(player1, player2, graphics))

    window.mainloop()


main()
