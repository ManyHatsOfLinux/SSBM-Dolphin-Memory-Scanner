#!/usr/bin/python3

import os
#from turtle import color
import psutil
import subprocess
from time import sleep
from prettytable import PrettyTable
import sys




#avilable lights
lights=[15,16]

#argument processing.
program_name = sys.argv[0]
arguments = sys.argv[1:]

#enable output
if "--debug" in arguments:
    print("DEBUG MODE:")
    DEBUG=True
else:
    DEBUG=False


if "--no-clear" in arguments and DEBUG==True:
    print("NOCLEAR MODE:")
    NOCLEAR=True
else:
    NOCLEAR=False

if "--no-lights" in arguments:
    if DEBUG==True:
        print("Running without lights")
    lights=[]

program_name = 'dolphin-emu'


#string to search for GALE01..plus some other data.abs
#always results in 3 results, the last of which is the start of the memory table.
base_string="47 41 4C 45 30 31 00 02 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 C2 33 9F 3D"



light_update_interval=0.1
dolphin_check_interval=5

colors=[

        '"#1f822a"',
        '"#69a522"',
        '"#9ebd1c"',
        '"#bdcc19"',
        '"#c3b313"',
        '"#c99c0d"',
        '"#d17905"',
        '"#c95d05"',
        '"#c13f04"',
        '"#ff0e00"'

        ]




def add_hex_strings(hex1, hex2):
    return(hex(int(str(hex1), 16) + int(str(hex2), 16)))[2:]
    

#get list of all dolphin-emu pids
def get_dolphin_pid():
    

    #array to hold all pids
    process_pids = [[process.pid,process.name] for process in psutil.process_iter()]

    #array to hold dolphin ids
    dolphin_pids=[]

    #loop through all processing checking for string
    for process in process_pids:
        tmpid=str((process[1]))
        if program_name in tmpid:
            dolphin_pids.append((process[0]))

    #close if more than one was found
    if len(dolphin_pids) >= 2:
        return(dolphin_pids[0])
    elif len(dolphin_pids) < 1:
        return("NULL")
    else:
        dolphin_id=dolphin_pids[0]
    return(dolphin_id)

def get_map_start():
    shell=subprocess.Popen(['/usr/bin/scanmem'], text=True, shell=True,  stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    command_string=str('pid ' + str(dolphin_pid) +'\noption scan_data_type bytearray \n option region_scan_level 3 \n reset \n' + base_string + '\n')
    shell.stdin.write(command_string)
    shell.stdin.write('list\n')
    output,errors=(shell.communicate(input=('\n')))

    index=0
    lines=[[]]
    for word in output: 
        if word=='\n':
            index=(index + 1)
            lines.append([])
        else:
            lines[index].append(word)
    
    gale_entrys=[]
    for line in lines:
        if line[0] == '[' and line[35] and line[34]==' ':
            gale_entrys.append(line)

    if gale_entrys == []:
        return("NULL")
    startloc=[]
    for x in range(len(gale_entrys[len(gale_entrys)-1])):


        if x >=5:
            if x <= 16:
                startloc.append(gale_entrys[len(gale_entrys)-1][x])
        if x > 20:
            break

    
    startstring=""
    for x in range(len(startloc)):
        startstring+=(str(startloc[x]))
    
    if DEBUG==True:
        print("Found Starting RAM address for GameCube memory:", startstring)
    
    #return("25c0000000")
    return(startstring)

def scan_for_hp(hp_addr):
    return(get_ram_data(hp_addr, 2))

def scan_for_stock(stock_addr):
    return(get_ram_data(stock_addr, 1))
    
def scan_for_char_mode(char_sel_addr):
    char_mode=get_ram_data(char_sel_addr, 2)
    return char_mode

def scan_for_char(char_addr):
    return(get_ram_data(char_addr,1))

def scan_for_byte(address):
    return(get_ram_data(address, 4))

def scan_for_int(address):
    return(get_ram_data(address,2))

#checks #0x80479D33 for value of 2, 1 is stage select, 0 is menues.
def scan_for_menu_state(menu_state_addr):
    menu_state=get_ram_data(menu_state_addr, 1)
    return(menu_state)
                    
#pull data from ram returns hex string I think.
def get_ram_data(address, length):
    shell=subprocess.Popen(['/usr/bin/scanmem'], text=True, shell=True,  stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    command_string=str('pid ' + str(dolphin_pid) +'\noption scan_data_type int32 \n option region_scan_level 3 \n reset \n dump ' + address + ' ' + str(length) + '\n')
    shell.stdin.write(command_string)
    output,errors=(shell.communicate(input=('\n')))
    index=0
    lines=[[]]
    for word in output: 
        if word=='\n':
            index=(index + 1)
            lines.append([])
        else:
            lines[index].append(word)
    for line in lines:
        if len(line) > 4:
            #if line begins with hex address (output of memory dump)
            if line[1] == 'x':
                if line[0]=='0':
                    outputStr=""
                    for x in line:
                        outputStr+=x
                    tmpdata=outputStr.split(' ')
                    tmpdata.pop(0)
                    tmpdata.pop(len(tmpdata)-1)
                    data=""
                    for x in tmpdata:
                        data+=x
                    return(int(data,16))


def turn_on_lights(lights):
    for light in lights:
        shell=subprocess.Popen(['/usr/bin/bash'], text=True, shell=True,  stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        command_string=str('hueadm light ' + str(light) +' on\n')
        shell.stdin.write(command_string)
        output,errors=(shell.communicate(input=('\n')))

def set_lamp_color(light, color):
    #print("Light:" + str(light) + " Color:" + str(color) + "")
    shell=subprocess.Popen(['/usr/bin/bash'], text=True, shell=True,  stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    command_string=str('hueadm light ' + str(light)+ ' ' + str(color)+'\n')
    shell.stdin.write(command_string)
    output,errors=(shell.communicate(input=('\n')))
    
def test_lamp(light):
    for color in colors:
        set_lamp_color(light,color)
        sleep(0.2)

def init_lights(lights):
    #set both lights to stock
    for light in lights:
        set_lamp_color(light, colors[0])

def print_data_table(player_data):
    table = PrettyTable(["Name","HP","Stock", "Character","Color"])
    for data in player_data:
        table.add_row(data)
    if NOCLEAR==False:
        subprocess.call('clear')
    print(table)

def get_players():

    player_data_addrs=[
        #name blockstart char_selectaddr stock_addr light
        ["Player1","453080","3F0E06","45310E","NULL"],
        ["Player2","453F10","3F0E2A","453F9E","NULL"],
        ["Player3","454DA0","3F0E4E","454E2E","NULL"],
        ["Player4","455C30","3F0E72","455CBE","NULL"]
    ]

    players=[]

    #only human or cpu playes are added to players
    for player in player_data_addrs:
        x=Player(player[0],player[1],player[2],player[3],player[4])
        if x.mode!=3:
            players.append(x)
            if DEBUG==True:
                print("My name is ", x.name, " and my hpaddr is :",x.hp_addr)


    #assign lights to players based on port priority
    for light_index in range(len(lights)):
        #if you have enough players to fit this light
        if len(players) >= light_index+1:
            players[light_index].light = lights[light_index]

    return players



#ID Lookup Characters/Costumes
#bad loop i re-wrote becuase python 3.9 does not appear to have 
# support for the match function.
def char_num_to_string(charnum):
    if charnum == 0:
        return("Dr. Mario")
    elif charnum == 1:
        return("Mario")
    elif charnum == 2:
        return("Luigi")
    elif charnum == 3:
        return("Bowser")
    elif charnum == 4:
        return("Peach")
    elif charnum == 5:
        return("Yoshi")
    elif charnum == 6:
        return("DK")
    elif charnum == 7:
        return("Captain Falcon")
    elif charnum == 8:
        return("Ganondorf")
    elif charnum == 9:
        return("Falco")
    elif charnum == 10:
        return("Fox")
    elif charnum == 11:
        return("Ness")
    elif charnum == 12:
        return("Ice Climbers")
    elif charnum == 13:
        return("Kirby")
    elif charnum == 14:
        return("Samus")
    elif charnum == 15:
        return("Zelda")
    elif charnum == 16:
        return("Link")
    elif charnum == 17:
        return("Young Link")
    elif charnum == 18:
        return("Pichu")
    elif charnum == 19:
        return("Pikachu")
    elif charnum == 20:
        return("JigglyPuff")
    elif charnum == 21:
        return("MewTwo")
    elif charnum == 22:
        return("Mr. Game & Watch")
    elif charnum == 23:
        return("Marth")
    elif charnum == 24:
        return("Roy")
    else:
        return("ERROR")

#same here oh well.
def char_color_num_to_string(color_num): 
    
    if color_num == 0:
        return("None")
    elif color_num == 1:
        return("Red")
    elif color_num == 2:
        return("Blue")
    elif color_num == 3:
        return("Green")
    elif color_num == 4:
        return("Pink")
    else :
        return("ERROR")




class Player:

    def hp_to_color_index(self):
        if self.hp < 10:
            return 0
        elif self.hp < 20:
            return 1
        elif self.hp < 30:
            return 2
        elif self.hp < 40:
            return 3
        elif self.hp < 50:
            return 4
        elif self.hp < 60:
            return 5
        elif self.hp < 70:
            return 6
        elif self.hp < 80:
            return 7
        elif self.hp < 90:
            return 8
        else:
            return 9


    def update_stocks(self):
        tmpstock=(scan_for_stock(self.stock_addr))
        self.stock_count=tmpstock
    

    def update_hp(self):
           oldhp=self.hp
           self.hp=(scan_for_hp(self.hp_addr))

           #HP value changed
           if self.hp != oldhp:
                if self.hp is None:
                    if DEBUG==True:
                        print("HP WAS NONE")
                else:
                    self.set_color()
    
                #health percent dropped (died)
                if self.hp is not None and self.hp < oldhp:

                    self.update_stocks()
   

    def set_color(self):
        tmpcolor=self.current_color
        self.current_color=self.hp_to_color_index()
        if tmpcolor != self.current_color:
            set_lamp_color(self.light, colors[self.current_color])    

    def update_char_mode(self):
        return(scan_for_char_mode(self.char_sel_addr))


    def pull_report(self):
        player_report=[]


        #[String Label for value, data]
        #player_report.append([])

        player_report.append(["Name",self.name])
        player_report.append(["Character",self.character])
        player_report.append(["Costume Color",self.character_color])
        player_report.append(["Suicide Count",scan_for_int(add_hex_strings(self.blockstart, self.suicide_count_offset))])
        player_report.append(["P1 KO",scan_for_byte(add_hex_strings(self.blockstart, self.p1_ko_offset))])
        player_report.append(["P2 KO",scan_for_byte(add_hex_strings(self.blockstart, self.p2_ko_offset))])
        player_report.append(["P3 KO",scan_for_byte(add_hex_strings(self.blockstart, self.p3_ko_offset))])
        player_report.append(["P4 KO",scan_for_byte(add_hex_strings(self.blockstart, self.p4_ko_offset))])
        player_report.append(["Jump Count",scan_for_byte(add_hex_strings(self.blockstart, self.jump_count_offset))])
        player_report.append(["Ledge Grabs",scan_for_byte(add_hex_strings(self.blockstart, self.ledge_grab_count_offset))])
        player_report.append(["Taunt Count",scan_for_byte(add_hex_strings(self.blockstart, self.taunt_count_offset))])
        player_report.append(["Sheild Count",scan_for_byte(add_hex_strings(self.blockstart, self.sheild_count_offset))])
        player_report.append(["Total Connected Attacks",scan_for_byte(add_hex_strings(self.blockstart, self.total_connected_attacks_offset))])
        player_report.append(["Winner",str(self.winner)])



        return(player_report)
                

    def __init__(self,name,blockstart,char_sel_addr,stock_addr,light):

        self.name = name

        #Character Block
        self.blockstart=add_hex_strings(blockstart, start_address)

        #HP
        self.hp = 0
        self.hpoffset = "60"
        self.hp_addr = add_hex_strings(self.hpoffset, self.blockstart)
        
        #stock count
        self.stock_count=0
        self.stock_addr = add_hex_strings(start_address,stock_addr)

        #default to no, True if player won the round
        self.winner=False

        
        #player mode mode (hmn, cpu, none)
        self.char_sel_addr=add_hex_strings(start_address,char_sel_addr)
        self.mode = self.update_char_mode()
        if self.mode == 1:
            self.is_cpu=True
            self.name = str(self.name +" (CPU)")
        else:
            self.is_cpu=False

        #get character data
        self.character_addr_offset="4"
        self.char_color_addr_offset="3"
        self.char_addr=add_hex_strings(self.character_addr_offset, self.char_sel_addr)
        self.char_color_addr=add_hex_strings(self.char_color_addr_offset, self.char_sel_addr)
        self.character_color_num=(scan_for_char(self.char_color_addr))
        self.character_num=(scan_for_char(self.char_addr))
        self.character=char_num_to_string(self.character_num)
        self.character_color=char_color_num_to_string(self.character_color_num)
        

        self.light = light
        self.current_color="NULL"
       
    
        #for reporting of stats after match
        self.suicide_count_offset="8C"
        self.p1_ko_offset="70"
        self.p2_ko_offset="74"
        self.p3_ko_offset="78"
        self.p4_ko_offset="7C"
        self.jump_count_offset="674"
        self.ledge_grab_count_offset="690"
        self.taunt_count_offset="694"
        self.sheild_count_offset="69C"
        self.total_connected_attacks_offset="D18"



if __name__ == "__main__": 


    
    turn_on_lights(lights)

    init_lights(lights)


    dolphin_pid=get_dolphin_pid()



    
    #mainloop start
    while True:
        if dolphin_pid == "NULL":
            sleep(dolphin_check_interval)
        
        if DEBUG==True:
            print("Checking For Dolphin.")
        
        dolphin_pid=get_dolphin_pid()

        if DEBUG==True:
            if dolphin_pid != "NULL":
                print("Found Dolphin with pid:",dolphin_pid)
            else:
                print("Dolphin not found.")

        

        #Dolphin is runniing.
        while dolphin_pid != "NULL" and dolphin_pid==get_dolphin_pid():

            start_address=get_map_start()

            if start_address!="NULL":
                if DEBUG==True:
                    print("SSBM found, starting location is, ", start_address)
                
                menu_state_addr=add_hex_strings("479D33", start_address)
            
            elif DEBUG==True:
                print("SSBM Not Found")
           

            #SSMB is loaded
            while start_address != "NULL" and dolphin_pid==get_dolphin_pid():

                #are you in a match?
                while scan_for_menu_state(menu_state_addr)==2:
                    if DEBUG==True:
                        print("Match Started")

                    players=get_players()

                    dolphin_closed=False

                    old_player_data=[]
                    player_data=[]

                    while dolphin_closed==False and scan_for_menu_state(menu_state_addr)==2:


                        for player in players:


                            #update all playing characters
                            if player.mode !=3:
                            
                                player.update_hp()
                                player.set_color()
                                player.update_stocks()
                                player_data.append([player.name, player.hp, player.stock_count,player.character, player.character_color])


                                #None data found
                                if player.hp is None:
                                    if DEBUG==True:
                                        print("Dolphin Endeded, Player did not have hp:", player.hp)

                                    dolphin_closed=True


                        if DEBUG==True and player_data!=old_player_data:

                            print_data_table(player_data)

                        old_player_data=player_data
                        player_data=[]

                    

                        sleep(light_update_interval)

                    #match stoped or dolphin closed
                    #start_address=get_map_start()
                    
                    
                    #get report
                    report_array=[]
                    highest_stock_player="Null"

                    #get winner
                    for player in players:
                        if highest_stock_player=="Null" or (highest_stock_player != "Null" and (highest_stock_player.stock_count < player.stock_count)):
                            highest_stock_player=player
                    
                    #set winner
                    highest_stock_player.winner=True

                    #check for ties
                    for player in players:
                        if player.stock_count == highest_stock_player.stock_count and highest_stock_player != player:
                            player.winner="Tied"
                            highest_stock_player.winner="Tied"
                    
                    


                    for player in players:
                        report_array.append(player.pull_report())
                    print("REPORT")
                    for line in report_array:
                        for bullline in line:
                            print(bullline)
