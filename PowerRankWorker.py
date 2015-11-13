import sys
import re
import urllib2
import json
import threading


class PowerRankWorker(threading.Thread):
    
    myInput = ""
    grandTotalPR = 0
    userInputComplete = False
    waiting = False
    finished = False
    userInputText = ""
    uniquePlayers = {}
    def __init__(self, fileName):
        super(PowerRankWorker, self).__init__()
        self.myInput = fileName

    def run(self):
        inputFile = open(self.myInput, "r")
        
        tourneyNames = []
        tourneyPlayerCount = {} #{tourneyName: player count}
        matchListPerTourney = {} #{tourneyName: getMatches(tourney)}
        playerDict = {} #{tourneyName: getParticipants(tourney)}
        
        playerIDsPerTourney = {}#{tourneyName: {playerID: playerName}} this is to find a playerName from a playerID
        playerInfo = {}#{playerName:{attendance: number of tournies attended, PP:value, opponents:[], victories:{myOpponentName:number of times I beat them}, {losses: {myOpponentName:number of times I lost to them}}}}
        PRList = []
        normalizedNames = {} #{oldName: newName} this dict is generated from the userInput and used to relate the same players across tournaments
        
        
        for line in inputFile:
            tourneyNames.append(self.parseURL(line.strip()))
            
        
        inputFile.close()
        
        for name in tourneyNames:
            playerDict[name] = self.getParticipants(name)#get all the players from each tourney
            matchListPerTourney[name] = self.getMatches(name)#get all matches from each tourney
        
        for tourney in tourneyNames:
            cnt = 0
            for player in playerDict.get(tourney):
                playerName = player['participant']['name']
                #add 1 to the playerCount for this tourney
                cnt = cnt + 1
                #populate the GUI dictionary - uniquePlayers
                if not self.uniquePlayers.has_key(playerName):
                    self.uniquePlayers[playerName] = ""
                    
            tourneyPlayerCount[tourney] = cnt
            
        self.waiting = True
        while self.userInputComplete is False:
            pass
        
        #make new data structure here with the userInput of names
        
        
        manualData = False
        tName = ''
        for line in self.userInputText.split('\n'):
            if manualData == False:
                oldName = re.sub(r'^(.*) =\s*.*', '\\1', line)
                newName = re.sub(r'^.* =\s*(.*)', '\\1', line)
                if newName != '':
                    normalizedNames[oldName] = newName
                if re.match(r'^t :.*$', line):
                    tName = re.sub(r'^t : ([^\[]+)\[(\d+)\]:$', '\\1', line)
                    numOfPlayers = re.sub(r'^t : ([^\[]+)\[(\d+)\]:$', '\\2', line)
                    tourneyNames.append(tName)
                    tourneyPlayerCount[tName] = int(numOfPlayers)
                    manualData = True
            else:
                if re.match(r'^t :.*$', line):#info for tourney
                    tName = re.sub(r'^t : ([^\[]+)\[(\d+)\]:$', '\\1', line)
                    numOfPlayers = re.sub(r'^t : ([^\[]+)\[(\d+)\]:$', '\\2', line)
                    tourneyNames.append(tName)
                    tourneyPlayerCount[tName] = int(numOfPlayers)
                elif re.match(r'^[^,]+,[^,]+$', line):#player name and rank
                    pName = re.sub(r'^([^,]+),(.*)', '\\1', line)
                    rank = re.sub(r'^([^,]+),(.*)', '\\2', line)
                    if playerDict.has_key(tName):
                        playerDict[tName].append({'participant': {'id': pName, 'name': pName, 'final_rank': int(rank)}})
                    else:
                        playerDict[tName] = [{'participant': {'id': pName, 'name': pName, 'final_rank': int(rank)}}]
                elif re.match(r'^([^,]+),([^,]+),(.*)$', line):#match info
                    wName = re.sub(r'^([^,]+),([^,]+),(.*)', '\\1', line)
                    lName = re.sub(r'^([^,]+),([^,]+),(.*)', '\\2', line)
                    score = re.sub(r'^([^,]+),([^,]+),(.*)', '\\3', line)
                    if matchListPerTourney.has_key(tName):
                        matchListPerTourney[tName].append({'match': {'winner_id': wName, 'loser_id': lName, 'scores_csv': score}})
                    else:
                        matchListPerTourney[tName] = [{'match': {'winner_id': wName, 'loser_id': lName, 'scores_csv': score}}]
                
            #t : tName[playerCnt]:
            #p1,rank
            #p2,rank
            #winnner,loser,score
            #winner,loser,score
            #
            
                
                
        for tourney in tourneyNames:
            playerIDsPerTourney[tourney] = {}#create a dict entry for this tourney to keep track of playerIDs and player count
            for player in playerDict.get(tourney):
                playerName = player['participant']['name']#used to populate playerIDsPerTourney
                playerRank = player['participant']['final_rank']#used to calculate PP
                playerID = player['participant']['id']#used to populate playerIDsPerTourney
                playerCount = tourneyPlayerCount[tourney]
                    
                #find the normalized player name to use as key
                playerNameKey = playerName
                    
                if normalizedNames.has_key(playerName):
                    playerNameKey = normalizedNames.get(playerName)
                    #print playerName + " = " + playerNameKey
                
                #calculate Total PP and add to the count of tournaments this player has attended
                if playerInfo.has_key(playerNameKey):
                    playerInfo[playerNameKey]['PP'] = self.addRankPoints(playerRank, playerCount, playerInfo[playerNameKey]['PP'])
                    playerInfo[playerNameKey]['attendance'] = playerInfo[playerNameKey]['attendance'] + 1
                else:
                    playerInfo[playerNameKey] = {'attendance': 1, 'PP': self.addRankPoints(playerRank, playerCount)}
                    
                #populate playerIDsPerTourney
                if playerIDsPerTourney[tourney].has_key(playerID) is False:
                    playerIDsPerTourney[tourney][playerID] = playerNameKey
                    

        
        #print self.uniquePlayers
        #loop through the matches to populate the data I need
        for tourney in tourneyNames:
            playersInTourney = playerIDsPerTourney[tourney]
            for match in matchListPerTourney[tourney]:
                if self.isValidMatch(match['match']['scores_csv']):
                    #get winner and loser IDs
                    #winnerID -> victories{loserID: +1}
                    #loserID -> losses{winnerID: +1}
                    
                    winner = playerIDsPerTourney[tourney][match['match']['winner_id']]
                    loser = playerIDsPerTourney[tourney][match['match']['loser_id']]
                    
                    #add each player to the other's opponent list
                    if playerInfo[winner].has_key('opponents'):
                        if loser not in playerInfo[winner]['opponents']:
                            playerInfo[winner]['opponents'].append(loser)
                    else:
                        playerInfo[winner]['opponents'] = [loser]
                        
                    if playerInfo[loser].has_key('opponents'):
                        if winner not in playerInfo[loser]['opponents']:
                            playerInfo[loser]['opponents'].append(winner)
                    else:
                        playerInfo[loser]['opponents'] = [winner]
                    
                    #victories for winner
                    if playerInfo[winner].has_key('victories'):
                        if playerInfo[winner]['victories'].has_key(loser):
                            playerInfo[winner]['victories'][loser] = playerInfo[winner]['victories'][loser] + 1
                        else:
                            playerInfo[winner]['victories'][loser] = 1
                    else:
                        playerInfo[winner]['victories'] = {}
                        playerInfo[winner]['victories'][loser] = 1
                    
                    #losses for loser
                    if playerInfo[loser].has_key('losses'):
                        if playerInfo[loser]['losses'].has_key(winner):
                            playerInfo[loser]['losses'][winner] = playerInfo[loser]['losses'][winner] + 1
                        else:
                            playerInfo[loser]['losses'][winner] = 1
                    else:
                        playerInfo[loser]['losses'] = {}
                        playerInfo[loser]['losses'][winner] = 1
                
                
        
        
        #loop through each players opponents and calculate PRs
        for playerName in playerInfo:
            #average all players PP before calculations
            playerInfo[playerName]['PP'] = playerInfo[playerName]['PP']/playerInfo[playerName]['attendance']
            
        for playerName in playerInfo:
            self.calcPR(playerName, playerInfo[playerName], PRList, playerInfo)
            
        
        output = open("PR_ranks.txt", "w")
        sortedList = sorted(PRList, key=lambda player: player[1], reverse=True)
        for p in sortedList:
            #re-calculate based on average PR
            output.write("%s - (%f); Tourneys attended: %d\n" % (p[0], p[1], p[2]))
        
        output.close()
        self.finished = True
        return
        #final formula: finalPP + ((V - L * MU_weight)+...for each opponent)
        # V = (opp/pp * victories)
        # L = (pp/opp * losses)
        # finalPP = pp * PP_weight
        
        
        
        
    def calcPR(self, playerName, playerDict, PRList, playerInfo):
        PP_WEIGHT = 1;
        MU_WEIGHT = 2;
        totalPR = 0;
        #print "player name: {0} -> pp = {1}".format(playerName, playerDict['PP'])
        if playerDict.has_key('opponents'):
            for opponent in playerDict['opponents']:
                V = 0;
                L = 0;
                if playerDict.has_key('victories') and playerDict['victories'].has_key(opponent):
                    if playerDict['PP'] != 0:
                        V = (playerInfo[opponent]['PP'] / playerDict['PP']) * playerDict['victories'][opponent]
                    else:
                        V = 0
                    
                if playerDict.has_key('losses') and playerDict['losses'].has_key(opponent):
                    if playerInfo[opponent]['PP'] != 0:
                        L = (playerDict['PP'] / playerInfo[opponent]['PP']) * playerDict['losses'][opponent]
                    else:
                        L = 0
                    
                totalPR = totalPR  + (playerDict['PP'] * PP_WEIGHT) + ((V - L) * MU_WEIGHT)
                self.grandTotalPR = self.grandTotalPR + totalPR
        
        PRList.append((playerName, totalPR, playerInfo[playerName]['attendance']))
        

    def addRankPoints(self, rank, playerCount, oldPP=0):
        if rank == 1:
            return (1 * playerCount) + oldPP
        elif rank == 2:
            return (.65 * playerCount) + oldPP
        elif rank == 3:
            return (.42 * playerCount) + oldPP
        elif rank == 4:
            return (.27 * playerCount) + oldPP
        elif rank == 5 or rank == 6:
            return (.18 * playerCount) + oldPP
        elif rank == 7 or rank == 8:
            return (.12 * playerCount) + oldPP
        elif rank >= 9 and rank <= 12:
            return (.08 * playerCount) + oldPP
        elif rank >= 13 and rank <= 16:
            return (.05 * playerCount) + oldPP
        elif rank >= 17 and rank <= 24:
            return (.03 * playerCount) + oldPP
        elif rank >= 25 and rank <= 32:
            return (.02 * playerCount) + oldPP
        elif rank >= 33 and rank <= 48:
            return (.01 * playerCount) + oldPP
        elif rank >= 49:
            return 0 + oldPP
        else:
            return 0 + oldPP
        
        
        
    
    def isValidMatch(self, scores_csv):
        #the scores_csv attribute of the match json is in the form of #-# (0-2)
        #if the match was not complete, it will be 0--1
        #add these numbers together in order to determine if the match was played.
        num1 = int(re.sub(r'(\d+)--?(\d+).*', '\\1', scores_csv))
        num2 = int(re.sub(r'(\d+)--?(\d+).*', '\\2', scores_csv))
        total = num1 + num2
        if total <= 0:
            return False
        else:
            return True
    
    def parseURL(self, tournamentURL):
        if re.match('http://[^\.]+\.challonge\.com/.*', tournamentURL):
            return re.sub('http://(.*)\.challonge.com/(.*)', '\\1-\\2', tournamentURL)
        else:
            return re.sub('http://challonge\.com/(.*)', '\\1', tournamentURL)
        
    def getParticipants(self, tourneyName):
        auth_handler = urllib2.HTTPBasicAuthHandler()
        req = urllib2.Request("https://api.challonge.com/v1/tournaments/%s/participants.json" % (tourneyName))
        auth_handler.add_password(
            realm = "Application",
            uri = req.get_full_url(),
            user = "mattems12",
            passwd = "lzjwhwSbSEOMnLwAh0zccH5Cwm4cpSxsTSxDQQIw"
        )
        opener = urllib2.build_opener(auth_handler)
        response = opener.open(req)
        responseAsDict = json.load(response)
        response.close()
        return responseAsDict
        
    def getMatches(self, tourneyName):
        auth_handler = urllib2.HTTPBasicAuthHandler()
        req = urllib2.Request("https://api.challonge.com/v1/tournaments/%s/matches.json" % (tourneyName))
        auth_handler.add_password(
            realm = "Application",
            uri = req.get_full_url(),
            user = "mattems12",
            passwd = "lzjwhwSbSEOMnLwAh0zccH5Cwm4cpSxsTSxDQQIw"
        )
        opener = urllib2.build_opener(auth_handler)
        response = opener.open(req)
        responseAsDict = json.load(response)
        response.close()
        return responseAsDict