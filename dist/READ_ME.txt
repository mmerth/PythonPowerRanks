How to use this program.
1) create a text file containing all of the challonge URLs that you want to use.

2) double click on PowerRankGUI.exe to start the program

3) click on the 'browse' button and select the file you made from step 1.

4) click on the 'Go' button, and the text box will be populated with all of the
   player names from all the tournaments. These will be listed in alphabetic order.
   In order for accurate calculations, please make sure players that used multiple
   tag names get assigned the same name.
        Ex: the same player is Pockets in one bracket, and mrPockets in another,
            so both tags show up. These should become the same name.
                   before -------> after
            Pockets =               Pockets = Pockets (this could also be left blank since it's the name you want)
            mrPockets =             mrPockets = Pockets
            
5) ***Optional***
   Whole tournaments can be entered in manually after all the names.
   Ex:
        Pockets =
        mrPockets = Pockets                 (last line of Name Data)
        t : tName[playerCnt]:               't : ' -> this is an indicator that you are passing in new tournament data
        p1,rank                             multiple tournaments can be added this way. just use another 't : ' to 
        p2,rank                             indicate another.
        winnner,loser,score(winner#-loser#)
        winner,loser,score
        
                                            tName -> can be any tournament name that you did not use in the challonge URLs.
        t : tName[2]:                       [16] -> number of tournament entrants.
        Pockets,1                           These are the final player rankings
        RandomGuy,2                         NOTE: these must also use the same normalized names form above
        Pockets,RandomGuy,2-0               This is the match info, the score must be in the form #-#
                                            ***MAKE SURE*** you add a newline character (enter) after each match data entry.
        
6) after all the name data has been normalized and any extra data added, click the 'Go' button again
   A message box will popup saying that it created a file. This file will be named PR_ranks.txt and
   it will be in the same folder as PowerRankGUI.exe