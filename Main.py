from fuzzywuzzy import fuzz
from fuzzywuzzy import process
import shutil
import requests
from bs4 import BeautifulSoup
import pandas as pd
import datetime
terminal_width = shutil.get_terminal_size().columns

from fractions import Fraction

# Playoff function
def playoffstats():
    name = input("Please enter the name of the player:")
    name_parts=name.split()
    print(name_parts)
    if len(name_parts) >= 2:
        first_name = name_parts[0]
        last_name = name_parts[-1]

    url = "https://www.basketball-reference.com/players/{}/".format(last_name[0])
    print(url)
    response_p = requests.get(url)
    response_p.text
    tables = pd.read_html(response_p.content)[0]
    pd.set_option('display.max_rows', None)
    file_path = "{}_players.txt".format(last_name[0])
    tables.to_csv(file_path, sep='\t', index = False)
    with open(file_path, 'r', encoding = 'utf-8') as file:
        lines = file.readlines()
    playoff_player_names = set()
    for line in lines:
        line = line.strip()
        player_nme = line.split()
        full_name = player_nme[0] + " " + player_nme[1]
        playoff_player_names.add(full_name)

    closest_match_name = process.extractOne(name, playoff_player_names, scorer=fuzz.token_sort_ratio)
    closest_playoff_name, similarlity_playoff_score = closest_match_name
    playoff_first_name , playoff_last_name = closest_playoff_name.split()
    playoff_sliced_first_name = playoff_first_name[:2]
    playoff_sliced_last_name = playoff_last_name[:5]
    playoff_url_playername = playoff_sliced_last_name +playoff_sliced_first_name +"01"
    print(playoff_url_playername)   
    career_playoff_url = "https://www.basketball-reference.com/players/{}/{}/gamelog-playoffs".format(last_name[0], playoff_url_playername)
    print(career_playoff_url)

    print("What stat Category are you looking for:")

    stat_cat = input("What stat Category are you looking for:")
    stat_dict = {
        "points": -3, "buckets": -3, "rebounds": -9, "boards": -9,
        "assists": -8, "dimes": -8, "PR": [-3,-9], "points rebounds": [-3,-9],
        "PA": [-3,-8], "points assists": [-3,-8], "pra": [-3,-9,-8], "points rebounds assists": [-3,-9,-8],
        "triple double": 0, "double double": 0, "blocks": -6, "steals": -7, "AR":[-9,-8], "assists rebounds":[-9,-8]
    }
    closest_stat = process.extractOne(stat_cat, stat_dict.keys(), scorer=fuzz.token_sort_ratio)
    closest_stat_key = closest_stat[0]
    cat_index = stat_dict.get(closest_stat_key)
    print(closest_stat_key.rjust(terminal_width))

    print("Are you looking for the over/under:")

    ou = input("Are you looking for the over/under")
    over_under_dict = { "over" ,  
                    "under" }
    closest_ou = process.extractOne(ou, over_under_dict, scorer = fuzz.token_sort_ratio)
    closest_ou_key = closest_ou[0]
    print(closest_ou_key.rjust(terminal_width))
    #Incomplete over under points function 

    print("What is the line for the " + closest_ou_key + ":")

    propt_num = input("What is the line for the " + closest_ou_key)
    print(propt_num.rjust(terminal_width))

    propt_num = int(propt_num)

    response = requests.get(career_playoff_url)
    response.text
    tables = pd.read_html(response.content)[7]
    pd.set_option('display.max_rows', None)

    file_path = 'output.txt'
    tables.to_csv(file_path, sep='\t', index=False)  # Write DataFrame to tab-separated text file
    tables


    
    file_path = "output.txt"
    with open(file_path, 'r') as file:
        lines = file.readlines()

    # Initialize an empty list to store the arrays
    data_arrays = []

    # Iterate through each line in the file
    for line in lines:
        # Strip any leading or trailing whitespace characters
        line = line.strip()
        if line:
            # Split the line into an array based on spaces
            data_array = line.split()
            # Append the array to the list of data_arrays
            data_arrays.append(data_array)

    # Display the first few rows of the parsed data arrays
    #for row in data_arrays[:72]:  # Displaying the first 5 rows as an example
        #print(row)
    temp_array = set()
    
    for i in range(len(data_arrays)):
        try:
            if closest_ou_key == "over":
                    if isinstance(cat_index, int):
                        if int(data_arrays[i][cat_index])>propt_num:
                            temp_array.add(tuple(data_arrays[i]))
                    elif isinstance(cat_index, list) and len(cat_index) ==2:
                        temp1 =(data_arrays[i][cat_index[0]]) 
                        temp2 =(data_arrays[i][cat_index[1]])
                        if int(temp1)+int(temp2)>propt_num:
                            temp_array.add(tuple(data_arrays[i]))
                    
            else:
                if isinstance(cat_index, int):
                    if (int(data_arrays[i][cat_index])<propt_num) == True:
                        temp_array.add(tuple(data_arrays[i]))
                elif isinstance(cat_index, list) and len(cat_index)==2:
                    temp1 =(data_arrays[i][cat_index[0]]) 
                    temp2 =(data_arrays[i][cat_index[1]])
                    if (int(temp1)+int(temp2)<propt_num) == True:
                        temp_array.add(tuple(data_arrays[i]))
                


                """
                FOR AWAY GAME IF A INDEX IS MISSING HOW CAN WE FIND THE CORRECT STAT INDEX
                ALREADY FIXED FOR HOME GAMES 

                WHAT IF THE INDEX THATS MISSING IS AFTER THE STAT VALUE 
                HOW CAN THIS ALTER THE HOME GAME DATA WITH HOW I IMPLEMENTED IT
                """
        except ValueError:
            continue

    inactive_games = 0
    print(data_arrays[10][1])
    for i in range(len(data_arrays)):
        if len(data_arrays[i][1]) > 2:
            inactive_games+=1
    start_year = data_arrays[0][2]

    header_counter =0
    for i in range(len(data_arrays)):
        if (data_arrays[i][0]) == "Rk":
            header_counter+=1

    for row in temp_array:
        print(row)
    active_games =(len(data_arrays) - (header_counter) - inactive_games)
    # this needs inactive 
    percentage = (len(temp_array)/active_games)*100
    formatpercentage="{:.2f}".format(percentage)
    print(closest_playoff_name + " has covered the " + closest_ou_key +" " + str(propt_num) +" " + str(closest_stat_key) + " in " + str(len(temp_array)) +"/" + str(active_games) +"(" + str(formatpercentage)  +"%)" + "playoff games.")
    
    

    print("testing")
    latest_series0 = data_arrays[-2][6]
    latest_series = data_arrays[-1][7]
    print(latest_series0)
    print(latest_series)
    print("end testing")
    
    for row in temp_array:
        print(row)
    print(len(temp_array))

    def latest_percentage(data_arrays, closest_ou_key, cat_index, propt_num, closest_playoff_name, closest_stat_key):
        latest_array = set()
        if data_arrays[-1][5] == "@":
            latest_series_numb = 7
            latest_series = int(data_arrays[-1][latest_series_numb])
        else:
            latest_series_numb = 6
            latest_series = int(data_arrays[-1][latest_series_numb])
        end_index = len(data_arrays) - latest_series
        i = len(data_arrays) - 1

        while i>=end_index: 
            if len(data_arrays[i][1]) > 2:
                end_index -=1
            else:
                if closest_ou_key == "over":
                    if isinstance(cat_index, int):
                        if int(data_arrays[i][cat_index])>propt_num:
                            latest_array.add(tuple(data_arrays[i]))
                    elif isinstance(cat_index, list) and len(cat_index) ==2:
                        temp1 =(data_arrays[i][cat_index[0]]) 
                        temp2 =(data_arrays[i][cat_index[1]])
                        if int(temp1)+int(temp2)>propt_num:
                            latest_array.add(tuple(data_arrays[i]))
                else:
                    if isinstance(cat_index, int):
                        if (int(data_arrays[i][cat_index])<propt_num) == True:
                            latest_array.add(tuple(data_arrays[i]))
                    elif isinstance(cat_index, list) and len(cat_index)==2:
                        temp1 =(data_arrays[i][cat_index[0]]) 
                        temp2 =(data_arrays[i][cat_index[1]])
                        if (int(temp1)+int(temp2)<propt_num) == True:
                            latest_array.add(tuple(data_arrays[i]))
    
            i-=1

        if data_arrays[end_index][5] == "@":
            opp_team = data_arrays[end_index][6]
        else:
            opp_team = data_arrays[end_index][5]
        print("\n")
        print(f"Latest Playoff Series vs {opp_team}")
        percentage = (len(latest_array) / latest_series) * 100
        formatted_percentage = "{:.0f}".format(percentage)
        print(f"{closest_playoff_name} game logs where he has covered {closest_ou_key} {propt_num} {closest_stat_key}. {len(latest_array)}/{latest_series}({formatted_percentage}%)")
        if latest_array:
            print(latest_array)
        #Should print the games where is was not covered 
        #luka doesnt work pj washington doesnt work name issue
        #dereck lively doenst work line 162 division by zero
        print(len(data_arrays))
        return end_index

    end_index=latest_percentage(data_arrays, closest_ou_key, cat_index, propt_num, closest_playoff_name, closest_stat_key)


    def second_latest_percentage(data_arrays, closest_ou_key, cat_index, propt_num, end_index, closest_playoff_name, closest_stat_key):
        latest_array = set()
        if data_arrays[end_index-1][5] == "@":
            latest_series = int(data_arrays[end_index-1][7])
        else:
            latest_series = int(data_arrays[end_index-1][6])
        i = end_index-1
        end_index =end_index - latest_series
        while i>=end_index: 
            if len(data_arrays[i][1]) > 2:
                end_index -=1
            else:
                if closest_ou_key == "over":
                    if isinstance(cat_index, int):
                        if int(data_arrays[i][cat_index])>propt_num:
                            latest_array.add(tuple(data_arrays[i]))
                    elif isinstance(cat_index, list) and len(cat_index) ==2:
                        temp1 =(data_arrays[i][cat_index[0]]) 
                        temp2 =(data_arrays[i][cat_index[1]])
                        if int(temp1)+int(temp2)>propt_num:
                            latest_array.add(tuple(data_arrays[i]))
                else:
                    if isinstance(cat_index, int):
                        if (int(data_arrays[i][cat_index])<propt_num) == True:
                            latest_array.add(tuple(data_arrays[i]))
                    elif isinstance(cat_index, list) and len(cat_index)==2:
                        temp1 =(data_arrays[i][cat_index[0]]) 
                        temp2 =(data_arrays[i][cat_index[1]])
                        if (int(temp1)+int(temp2)<propt_num) == True:
                            latest_array.add(tuple(data_arrays[i]))
    
            i-=1
        if data_arrays[end_index][5] == "@":
            opp_team = data_arrays[end_index][6]
        else:
            opp_team = data_arrays[end_index][5]
        print("\n")
        print(f"Latest Playoff Series vs {opp_team}")
        percentage = (len(latest_array) / latest_series) * 100
        formatted_percentage = "{:.0f}".format(percentage)
        print(f"{closest_playoff_name} game logs where he has covered {closest_ou_key} {propt_num} {closest_stat_key}. {len(latest_array)}/{latest_series}({formatted_percentage}%)")
        print(latest_array)
        return end_index
    if data_arrays[end_index -1][7].isdigit() or data_arrays[end_index -1][6].isdigit():
        end_index =second_latest_percentage(data_arrays, closest_ou_key, cat_index, propt_num, end_index, closest_playoff_name, closest_stat_key)
    else:
        print("no second")
    def third_latest_percentage(data_arrays, closest_ou_key, cat_index, propt_num, end_index, closest_playoff_name, closest_stat_key):
        latest_array = set()
        if data_arrays[end_index-1][5] == "@":
            latest_series = int(data_arrays[end_index-1][7])
        else:
            latest_series = int(data_arrays[end_index-1][6])
        i = end_index-1
        end_index =end_index - latest_series
        while i>=end_index: 
            if len(data_arrays[i][1]) > 2:
                end_index -=1
            else:
                if closest_ou_key == "over":
                    if isinstance(cat_index, int):
                        if int(data_arrays[i][cat_index])>propt_num:
                            latest_array.add(tuple(data_arrays[i]))
                    elif isinstance(cat_index, list) and len(cat_index) ==2:
                        temp1 =(data_arrays[i][cat_index[0]]) 
                        temp2 =(data_arrays[i][cat_index[1]])
                        if int(temp1)+int(temp2)>propt_num:
                            latest_array.add(tuple(data_arrays[i]))
                else:
                    if isinstance(cat_index, int):
                        if (int(data_arrays[i][cat_index])<propt_num) == True:
                            latest_array.add(tuple(data_arrays[i]))
                    elif isinstance(cat_index, list) and len(cat_index)==2:
                        temp1 =(data_arrays[i][cat_index[0]]) 
                        temp2 =(data_arrays[i][cat_index[1]])
                        if (int(temp1)+int(temp2)<propt_num) == True:
                            latest_array.add(tuple(data_arrays[i]))
    
            i-=1
        if data_arrays[end_index][5] == "@":
            opp_team = data_arrays[end_index][6]
        else:
            opp_team = data_arrays[end_index][5]
        print("\n")
        print(f"Latest Playoff Series vs {opp_team}")
        percentage = (len(latest_array) / latest_series) * 100
        formatted_percentage = "{:.0f}".format(percentage)
        print(f"{closest_playoff_name} game logs where he has covered {closest_ou_key} {propt_num} {closest_stat_key}. {len(latest_array)}/{latest_series}({formatted_percentage}%)")
        if latest_array:
            print(latest_array)
        return end_index

    if data_arrays[end_index -1][7].isdigit() or data_arrays[end_index -1][6].isdigit():
        end_index =third_latest_percentage(data_arrays, closest_ou_key, cat_index, propt_num, end_index,closest_playoff_name, closest_stat_key)
    else:
        print("no third")
    def fourth_latest_percentage(data_arrays, closest_ou_key, cat_index, propt_num, end_index, closest_playoff_name, closest_stat_key):
        latest_array = set()
        if data_arrays[end_index-1][5] == "@":
            latest_series = int(data_arrays[end_index-1][7])
        else:
            latest_series = int(data_arrays[end_index-1][6])
        i = end_index-1
        end_index =end_index - latest_series
        while i>=end_index: 
            if len(data_arrays[i][1]) > 2:
                end_index -=1
            else:
                if closest_ou_key == "over":
                    if isinstance(cat_index, int):
                        if int(data_arrays[i][cat_index])>propt_num:
                            latest_array.add(tuple(data_arrays[i]))
                    elif isinstance(cat_index, list) and len(cat_index) ==2:
                        temp1 =(data_arrays[i][cat_index[0]]) 
                        temp2 =(data_arrays[i][cat_index[1]])
                        if int(temp1)+int(temp2)>propt_num:
                            latest_array.add(tuple(data_arrays[i]))
                else:
                    if isinstance(cat_index, int):
                        if (int(data_arrays[i][cat_index])<propt_num) == True:
                            latest_array.add(tuple(data_arrays[i]))
                    elif isinstance(cat_index, list) and len(cat_index)==2:
                        temp1 =(data_arrays[i][cat_index[0]]) 
                        temp2 =(data_arrays[i][cat_index[1]])
                        if (int(temp1)+int(temp2)<propt_num) == True:
                            latest_array.add(tuple(data_arrays[i]))
    
            i-=1
        if data_arrays[end_index][5] == "@":
            opp_team = data_arrays[end_index][6]
        else:
            opp_team = data_arrays[end_index][5]
        print("\n")
        print(f"Latest Playoff Series vs {opp_team}")
        percentage = (len(latest_array) / latest_series) * 100
        formatted_percentage = "{:.0f}".format(percentage)
        print(f"{closest_playoff_name} game logs where he has covered {closest_ou_key} {propt_num} {closest_stat_key}. {len(latest_array)}/{latest_series}({formatted_percentage}%)")
        if latest_array:
            print(latest_array)
        return end_index


    if data_arrays[end_index -1][7].isdigit() or data_arrays[end_index -1][6].isdigit():
        end_index =fourth_latest_percentage(data_arrays, closest_ou_key, cat_index, propt_num, end_index, closest_playoff_name, closest_stat_key)
    else:
        print("no fourth")
    input("Press Enter to exit...")



# Main 


print("Regular season or playoff stats: ")

playoff = input("Regular season or playoff stats? ")
playoff_dict = {"Regular season", "Postseason", "Playoffs"}
closest_playoff = process.extractOne(playoff, playoff_dict, scorer=fuzz.token_sort_ratio)
closests_playoff_fuzzy, score = closest_playoff
print(closests_playoff_fuzzy.rjust(terminal_width))

if closests_playoff_fuzzy in {"Postseason", "Playoffs"}:
    playoffstats()
else:
    print("Which year of the regular season ")
    year = input("Which year of the regular season")
    print(year.rjust(terminal_width))
    print("Please enter the name of the player: ")


    url = "https://www.basketball-reference.com/leagues/NBA_{}_per_minute.html".format(year)
    response = requests.get(url)
    response.text
    tables = pd.read_html(response.content)[0]
    pd.set_option('display.max_rows', None)

    tables
    file_path = '{}_players.txt'.format(year)
    tables.to_csv(file_path, sep='\t', index=False)  # Write DataFrame to tab-separated text file
    with open(file_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()

    player_names = set()
    for line in lines:
        line = line.strip()
        player_nme = line.split()
        full_name = player_nme[1] + " " + player_nme[2]
        player_names.add(full_name)


    #Get the play from the user
    user_player = input("Please enter the name of player: ")
    print(user_player.rjust(terminal_width))


    closest_match = process.extractOne(user_player, player_names, scorer=fuzz.token_sort_ratio)
    closests_name, similarirty_score = closest_match
    firstname, lastname = closests_name.split()
    sliced_first_name = firstname[:2]
    sliced_last_name = lastname[:5]
    url_playername = sliced_last_name +sliced_first_name +"01"


    aligned_message = closests_name.rjust(terminal_width)  # Adjust the width as needed
   



    player_link = "https://www.basketball-reference.com/players/w/{}/gamelog/{}".format(url_playername, year)

    print(aligned_message)
    print("What stat Category are you looking for:")
    stat_cat = input("What stat Category are you looking for:")
    stat_dict = {
        "points": -3, "buckets": -3, "rebounds": -9, "boards": -9,
        "assists": -8, "dimes": -8, "PR": [-3,-9], "points rebounds": [-3,-9],
        "PA": [-3,-8], "points assists": [-3,-8], "pra": [-3,-9,-8], "points rebounds assists": [-3,-9,-8],
        "triple double": 0, "double double": 0, "blocks": -6, "steals": -7, "AR":[-9,-8], "assists rebounds":[-9,-8]
    }
    closest_stat = process.extractOne(stat_cat, stat_dict.keys(), scorer=fuzz.token_sort_ratio)
    closest_stat_key = closest_stat[0]
    cat_index = stat_dict.get(closest_stat_key)
    print(closest_stat_key.rjust(terminal_width))

    print("Are you looking for the over/under:")

    ou = input("Are you looking for the over/under")
    over_under_dict = { "over" ,  
                    "under" }
    closest_ou = process.extractOne(ou, over_under_dict, scorer = fuzz.token_sort_ratio)
    closest_ou_key = closest_ou[0]
    print(closest_ou_key.rjust(terminal_width))
    #Incomplete over under points function 

    print("What is the line for the " + closest_ou_key + ":")

    propt_num = input("What is the line for the " + closest_ou_key)
    print(propt_num.rjust(terminal_width))

    propt_num = int(propt_num)

    response = requests.get(player_link)
    response.text
    tables = pd.read_html(response.content)[7]
    pd.set_option('display.max_rows', None)

    file_path = 'output.txt'
    tables.to_csv(file_path, sep='\t', index=False)  # Write DataFrame to tab-separated text file
    tables

    file_path = "output.txt"
    with open(file_path, 'r') as file:
        lines = file.readlines()

    # Initialize an empty list to store the arrays
    data_arrays = []

    # Iterate through each line in the file
    for line in lines:
        # Strip any leading or trailing whitespace characters
        line = line.strip()
        # Split the line into an array based on spaces
        data_array = line.split()
        # Append the array to the list of data_arrays
        data_arrays.append(data_array)

    # Display the first few rows of the parsed data arrays
    """
    Testing
    for row in data_arrays[:72]:  # Displaying the first 5 rows as an example
        print(row)
    
    print(data_arrays[1])
    print(len(data_arrays[1]))

    print(cat_index)
    print(data_arrays[2][cat_index+1])
    print(cat_index+1)
    print(propt_num)
    """
    print("testing")
   
    #print(data_arrays[26][-3])
    #print(data_arrays[26][-9])
    #print(int(data_arrays[26][-3]) + int(data_arrays[26][-9]) <42)
    #print("end testing")

    temp_array = set()
    for i in range(len(data_arrays)):
        try:
            if closest_ou_key == "over":
                if isinstance(cat_index, int):
                    if int(data_arrays[i][cat_index])>propt_num:
                        temp_array.add(tuple(data_arrays[i]))
                elif isinstance(cat_index, list) and len(cat_index) ==2:
                    temp1 =(data_arrays[i][cat_index[0]]) 
                    temp2 =(data_arrays[i][cat_index[1]])
                    if int(temp1)+int(temp2)>propt_num:
                        temp_array.add(tuple(data_arrays[i]))
                
            else:
                if isinstance(cat_index, int):
                    if (int(data_arrays[i][cat_index])<propt_num) == True:
                        temp_array.add(tuple(data_arrays[i]))
                elif isinstance(cat_index, list) and len(cat_index)==2:
                    temp1 =(data_arrays[i][cat_index[0]]) 
                    temp2 =(data_arrays[i][cat_index[1]])
                    if (int(temp1)+int(temp2)<propt_num) == True:
                        temp_array.add(tuple(data_arrays[i]))
                
                """
                FOR AWAY GAME IF A INDEX IS MISSING HOW CAN WE FIND THE CORRECT STAT INDEX
                ALREADY FIXED FOR HOME GAMES 

                WHAT IF THE INDEX THATS MISSING IS AFTER THE STAT VALUE 
                HOW CAN THIS ALTER THE HOME GAME DATA WITH HOW I IMPLEMENTED IT
                """
        except ValueError:
            continue
    
    def last5_percentage(data_arrays, closest_ou_key, cat_index, propt_num):
        last5_array = set()



        i = len(data_arrays) - 1
        end_index = len(data_arrays) - 6 # Ensure we don't go out of bounds

        while i> end_index: 
            if len(data_arrays[i][1]) > 2:
                end_index -=1
                print(data_arrays[i][1])
            else:
                if closest_ou_key == "over":
                    if isinstance(cat_index, int):
                        if int(data_arrays[i][cat_index])>propt_num:
                            last5_array.add(tuple(data_arrays[i]))
                    elif isinstance(cat_index, list) and len(cat_index) ==2:
                        temp1 =(data_arrays[i][cat_index[0]]) 
                        temp2 =(data_arrays[i][cat_index[1]])
                        if int(temp1)+int(temp2)>propt_num:
                            last5_array.add(tuple(data_arrays[i]))
                else:
                    if isinstance(cat_index, int):
                        if (int(data_arrays[i][cat_index])<propt_num) == True:
                            last5_array.add(tuple(data_arrays[i]))
                    elif isinstance(cat_index, list) and len(cat_index)==2:
                        temp1 =(data_arrays[i][cat_index[0]]) 
                        temp2 =(data_arrays[i][cat_index[1]])
                        if (int(temp1)+int(temp2)<propt_num) == True:
                            last5_array.add(tuple(data_arrays[i]))
    
            i-=1
        print("Testing last 5games")
        print(len(last5_array)/5)
        
        print("End testing last 5games")



    def last10_percentage(data_arrays, closest_ou_key, cat_index, propt_num):
        last10_array = set()



        i = len(data_arrays) - 1
        end_index = len(data_arrays) - 11 # Ensure we don't go out of bounds

        while i> end_index: 
            if len(data_arrays[i][1]) > 2:
                end_index -=1
            else:
                if closest_ou_key == "over":
                    if isinstance(cat_index, int):
                        if int(data_arrays[i][cat_index])>propt_num:
                            last10_array.add(tuple(data_arrays[i]))
                    elif isinstance(cat_index, list) and len(cat_index) ==2:
                        temp1 =(data_arrays[i][cat_index[0]]) 
                        temp2 =(data_arrays[i][cat_index[1]])
                        if int(temp1)+int(temp2)>propt_num:
                            last10_array.add(tuple(data_arrays[i]))
                else:
                    if isinstance(cat_index, int):
                        if (int(data_arrays[i][cat_index])<propt_num) == True:
                            last10_array.add(tuple(data_arrays[i]))
                    elif isinstance(cat_index, list) and len(cat_index)==2:
                        temp1 =(data_arrays[i][cat_index[0]]) 
                        temp2 =(data_arrays[i][cat_index[1]])
                        if (int(temp1)+int(temp2)<propt_num) == True:
                            last10_array.add(tuple(data_arrays[i]))
    
            i-=1
        print("Testing last 10games")
        print(len(last10_array)/10)
                
        print("End testing last 10games")

        
    
    def last15_percentage(data_arrays, closest_ou_key, cat_index, propt_num):
        last15_array = set()



        i = len(data_arrays) - 1
        end_index = len(data_arrays) - 16 # Ensure we don't go out of bounds

        while i> end_index: 
            if len(data_arrays[i][1]) > 2:
                end_index -=1
            else:
                if closest_ou_key == "over":
                    if isinstance(cat_index, int):
                        if int(data_arrays[i][cat_index])>propt_num:
                            last15_array.add(tuple(data_arrays[i]))
                    elif isinstance(cat_index, list) and len(cat_index) ==2:
                        temp1 =(data_arrays[i][cat_index[0]]) 
                        temp2 =(data_arrays[i][cat_index[1]])
                        if int(temp1)+int(temp2)>propt_num:
                            last15_array.add(tuple(data_arrays[i]))
                else:
                    if isinstance(cat_index, int):
                        if (int(data_arrays[i][cat_index])<propt_num) == True:
                            last15_array.add(tuple(data_arrays[i]))
                    elif isinstance(cat_index, list) and len(cat_index)==2:
                        temp1 =(data_arrays[i][cat_index[0]]) 
                        temp2 =(data_arrays[i][cat_index[1]])
                        if (int(temp1)+int(temp2)<propt_num) == True:
                            last15_array.add(tuple(data_arrays[i]))
    
            i-=1
        print("Testing last 15games")
        print(len(last15_array)/15)
        print(last15_array)
        print("End testing last 15games")

    print("testing last5_percentage")
    last5_percentage(data_arrays, closest_ou_key, cat_index, propt_num)





    inactive_games = 0
    print(data_arrays[10][1])
    for i in range(len(data_arrays)):
        if len(data_arrays[i][1]) > 2:
            inactive_games+=1

    for row in temp_array:
        print(row)
    active_games =(len(data_arrays) - (len(data_arrays)// 20) - inactive_games)
     # this needs inactive 
    percentage = (len(temp_array)/active_games)*100
    formatpercentage="{:.2f}".format(percentage)
    print(closests_name + " has covered the " + closest_ou_key +" " + str(propt_num) +" " + str(closest_stat_key) +" line in " + str(year) + " in " + str(len(temp_array)) +"/" + str(active_games) +"(" + str(formatpercentage)  +"%)" + " games.")
    
    print(data_arrays[0])
    input("Press Enter to exit...")





    