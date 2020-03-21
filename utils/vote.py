class Vote:
    def __init__(self, candidates, winfunc, funcparamslist, winratio, maxballots, passwinnertofunc):
        self.func = winfunc #the function to execute when the vote is won
        self.funcparams = funcparamslist
        self.passwinner = passwinnertofunc #include or not the winner item into the win function. 
            # If the winner is the only argument, then funcparams can be empty list [].
        self.winratio = winratio #min percentage of votes required for any item to win. 
            # Set this to -1 in order to simply pick the item with the highest ballot count as winner.
        self.candidates = candidates #a list containing objects or things to be voted on
        
        self.votesdict = dict()
        for c in candidates:
            self.votesdict[c] = 0 #initializing the vote count for each candidate
        
        self.maxballots = maxballots #if set to -1, then there is no max ballot count. 
            # Vote ends when max ballot count reached; winner will be the candidate with most votes.
        self.ballots = 0
        
    def ballot_add(self, candidate):
        if self.ballots < self.maxballots or self.maxballots==-1 :
            self.votesdict[candidate]+=1
            self.ballots+=1
            if self.ballots==self.maxballots:
                finishmessage = self.ballot_finish(self.funcparams)
                return finishmessage
            else:
                return ""
        
    def ballot_finish(self, paramslist):
        if self.winratio==-1:
            winner = max(self.candidates, key=lambda key: self.candidates[key])
            
        else:
            majorityrequired = round(self.winratio * self.ballots)
            for c in self.candidates:
                if self.votesdict[c] > majorityrequired:
                    winner = c
        # now that the winner is found, execute the function with the winner candidate as a parameter 
            # (along with any other parameters inside the paramlist)
        if self.passwinner:
            paramslist.insert(0, winner)
        
        self.func(*paramslist)
        return "Winning candidate is **{}**".format(str(winner))
