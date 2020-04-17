import discord

class CogTaskManager:
    def __init__(self):
        self.tasks = dict()
        self.error_type = NotImplementedError
        #messages on which we're listening for events, indexed by associated owner member
    
    @property
    def task_dict(self):
        return self.tasks

    def define_unknown_owner_error(self, exception):
        self.error_type = exception

    def start_task(self, owner: discord.Member, task_constructor):
        newtask = task_constructor(owner)
        self.tasks[owner] = newtask

    def get_task(self, owner: discord.Member):
        try:
            return self.tasks[owner]
        except KeyError:
            print("Member {} does not own any tasks to refer to".format(str(owner)))
            raise self.error_type

        # identify each running task with its owner, and access each task 
        # by the Member object of the user currently requesting commands.
        # This Member from the message's ctx will be passed along to the bot task manager's 
        # running tasks (running objects) dict, as index names to refer to the correct task instance.
        # this way, there is functionality to restrict access to a game or a task to the owner 
        # or user that requested it.

    def kill_task(self, owner: discord.Member):
        try:
            del(self.tasks[owner])
        except KeyError:
            print("Member {} does not own any tasks to kill".format(str(owner)))