from datetime import datetime, timedelta
import yaml
from dataStructs import *
from driver.notifications import *

class SchoologyListener:
    def __init__(self, textnowCreds, scCreds):
        self.north = SchoolName.NEWTON_NORTH
        self.south = SchoolName.NEWTON_SOUTH
        self.notifications = NotificationDriver(textnowCreds, scCreds)
        self.restTime = timedelta(seconds=10)
    
    # Run function, for listening and calling notifications code.
    def run(self) -> bool:
        lastCheckTime = datetime.now() - self.restTime # Last time a check was made.
        sentNorth = False
        sentSouth = False

        while sentNorth == False or sentSouth == False:
            date = datetime.now() - timedelta(hours=5) # Convert from UTC --> EST
            states = self.fetchStates(date)
            # Reads from state file to determine whether notifications have been sent today.
            if not states[self.north] or not states[self.south]: 
                currentTime = datetime.now()
                if lastCheckTime + self.restTime < currentTime: # Sleep without delay   
                    # NNHS Runtime.
                    if not states[self.north]:
                        update = self.notifications.run(date, self.north) # Sends notifications, checks sucess.
                        if update:
                            self.writeState(self.north, date) # Update statefile and var.
                            sentNorth = True
                    # NSHS Runtime
                    if not states[self.south]:
                        update = self.notifications.run(date, self.south) # Sends notifications, check sucess.
                        if update:
                            self.writeState(self.south, date) # Update statefile and var.
                            sentSouth = True
                    states = self.fetchStates(date)
                    lastCheckTime = currentTime
            else:
                sentNorth = True
                sentSouth = True
        return True 
        

    # Function for fetching an up to date state file content.
    def fetchStates(self, date, statePath = 'state.yml'):
        stateDict = {
            SchoolName.NEWTON_NORTH: False,
            SchoolName.NEWTON_SOUTH: False
        }
        # Read state yaml file.
        with open(statePath, 'r') as f:
            state = yaml.safe_load(f)
        if state[str(SchoolName.NEWTON_NORTH)] == date.strftime('%m/%-d/%Y'):
            stateDict[SchoolName.NEWTON_NORTH] = True
        if state[str(SchoolName.NEWTON_SOUTH)] == date.strftime('%m/%-d/%Y'):
            stateDict[SchoolName.NEWTON_SOUTH] = True
        return stateDict

    # Function for writing state.
    def writeState(self, school: SchoolName, date, statePath = 'state.yml'):
        # Read state yaml file.
        with open(statePath, 'r') as f:
            state = yaml.safe_load(f)
        state[str(school)] = date.strftime('%m/%-d/%Y')
        if school == SchoolName.NEWTON_NORTH:
            state[str(SchoolName.NEWTON_SOUTH)] = state[str(SchoolName.NEWTON_SOUTH)]
        else:
            state[str(SchoolName.NEWTON_NORTH)] = state[str(SchoolName.NEWTON_NORTH)]
        # Write new state to state file
        with open('state.yml', 'w') as f:
            yaml.safe_dump(state, f)
        return state
    

