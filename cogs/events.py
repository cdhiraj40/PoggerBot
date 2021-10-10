from discord.ext import commands


class Events(commands.Cog):
    def __init__(self, client):
        self.client = client  # this allows us to access the client within our cog

    # ------------------- Events and Tasks -------------------
    # Loads bot, and lets us know when its ready
    @commands.Cog.listener()
    async def on_ready(self):
        print("Logged in as " + self.client.user.name)
        print(self.client.user.id)
        print("-----------------------")

    # When a known command fails, throws error
    @commands.Cog.listener()
    async def on_command_error(self, ctx: commands.Context, error: commands.CommandError):
        await ctx.send(f"{ctx.command.name} didn't work! Give it another try.\n"
                       f"Error: {error}")
        print(error)

    # Event for monitoring command usage
    @commands.Cog.listener()
    async def on_command(self, ctx):
        print(ctx.command.name + " was invoked.")

    # Event for monitoring successful command usage
    @commands.Cog.listener()
    async def on_command_completion(self, ctx):
        print(ctx.command.name + " was invoked successfully.")


# This function allows us to connect this cog to our bot
def setup(client):
    client.add_cog(Events(client))
