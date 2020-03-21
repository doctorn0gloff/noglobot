import discord

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