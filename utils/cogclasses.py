import discord
import csv

#######################################
#         Cog superclasses            #
#           -------------             #
# Pick and choose superclasses for    #
# your cogs for extra features!       #
#######################################

# The Reactable cog superclass.
# For cogs that need to have messages that listen for reactions.

class Reactable:
    def __init__(self):
        self.emoji_to_choice_map = dict()
        self.emojis = set() #set of discord.Emoji objects
        self.currently_listening = False
        self.msgs_listening_for_reactions = []
    
    async def init_new_choice(self, emoji: discord.Emoji, choice, refresh: bool):
        self.emoji_to_choice_map[emoji] = choice
        n_emojis_before = len(self.emojis)
        self.emojis.add(emoji)
        if (refresh == True):
            if (len(self.emojis) > n_emojis_before):
                # refreshes all existing listening msgs to include the new choice
                for msg in self.msgs_listening_for_reactions:
                    await msg.add_reaction(emoji)
            
    async def init_reactable_message(self, msg: discord.Message):
        self.msgs_listening_for_reactions.append(msg)
        for e in self.emojis:
            await msg.add_reaction(e)
        self.currently_listening = True
    
    async def on_react(self, reaction: discord.Reaction, choice_func, purge_irrelevant_reactions: bool):
        if (not self.currently_listening):
            return None
        #choice_func :: choice -> b
        reacted_msg = reaction.message
        for msg in self.msgs_listening_for_reactions:
            if (msg == reacted_msg):
                e = reaction.emoji
                if (e in self.emoji_to_choice_map):
                    return choice_func(self.emoji_to_choice_map[reaction.emoji])
                else:
                    if (purge_irrelevant_reactions == True):
                        await reacted_msg.clear_reaction(reaction)


# The SavesDataCSV cog superclass.
# For cogs that need to save large amounts of user data compactly.
# Since it uses a generic functional interface to pass in a hashing function, 
# this actually works with any key type, not just Member objects 
# (so it could also be a bot config data store, if needed)
# As of now, this uses a CSV file to store data for each.

DATA_DIRECTORY = "db"

class SavesDataCSV:
    def __init__(self, filename, fieldnames, fielddefaults, member_hash_func):
        self.file = DATA_DIRECTORY + "/" + filename
        self.hash_func = lambda m: str(member_hash_func(m))
        self.fieldnames = fieldnames # a list of field names, representing their order in each csv row
        self.fielddefaults = fielddefaults
        self.defaults = dict(zip(fieldnames, fielddefaults))
        self.fieldtypes = list(map(type, fielddefaults)) #types / typecasting functions

    def get_data_dict(self, member = None) -> dict:
        member_id = None if member is None else self.hash_func(member)
        dict_to_export = dict()
        with open(self.file, "r", encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile, delimiter=',', quotechar='|')
            for record in reader:
                # if member is not specified, get dict of all members' values
                # if member is specified, just get that one
                if (member is None) or (member_id == record[0]):
                    result = self.fielddefaults[:]
                    #type casting, from the input strings into the proper types
                    for i in range(1, len(record)):
                        result[i-1] = self.fieldtypes[i-1](record[i])
                    # save row to dict. the key is a string, not an int.
                    dict_to_export[record[0]] = dict(zip(self.fieldnames, result))
        if len(dict_to_export) == 0:
            print("No data for key found.")
            return None
        else:
            return dict_to_export

    def get_data_for(self, member) -> dict:
        raw_dict = self.get_data_dict(member)
        member_id = self.hash_func(member)
        try:
            return raw_dict[member_id]
        except:
            return self.defaults

    def get_attribute_for(self, member, fieldname):
        raw_dict = self.get_data_dict(member)
        member_id = self.hash_func(member)
        try:
            return raw_dict[member_id][fieldname]
        except:
            return self.defaults[fieldname]
        
    def write_attribute_for(self, member, fieldname, value):
        recordsbuffer = []
        member_id = self.hash_func(member)
        member_has_record = False
        fieldnum = self.fieldnames.index(fieldname)
        with open(self.file, "r", encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile, delimiter=',', quotechar='|')
            for record in reader:
                if (member_id == record[0]):
                    member_has_record = True
                    try:
                        record[fieldnum+1] = value #modify record with new value
                    finally: #then write the modified record to file
                        recordsbuffer.append(record)
                else:
                    recordsbuffer.append(record)
            if (member_has_record == False): #still no record; create new record
                newrecord = self.fielddefaults[:]
                try:
                    newrecord[fieldnum] = value
                finally:
                    recordsbuffer.append([member_id] + newrecord)

        with open(self.file, "w", encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile, delimiter=',', quotechar='|')
            writer.writerows(recordsbuffer)